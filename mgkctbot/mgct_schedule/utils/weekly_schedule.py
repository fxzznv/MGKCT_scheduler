import re
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta

from mgct_schedule.utils.rediss import push_weekly_schedule

from dotenv import load_dotenv

load_dotenv()

def get_schedule():
    # Получаем HTML с сайта
    response = requests.get("https://mgkct.minskedu.gov.by/%D0%BF%D0%B5%D1%80%D1%81%D0%BE%D0%BD%D0%B0%D0%BB%D0%B8%D0%B8/%D1%83%D1%87%D0%B0%D1%89%D0%B8%D0%BC%D1%81%D1%8F/%D1%80%D0%B0%D1%81%D0%BF%D0%B8%D1%81%D0%B0%D0%BD%D0%B8%D0%B5-%D0%B7%D0%B0%D0%BD%D1%8F%D1%82%D0%B8%D0%B9-%D0%BD%D0%B0-%D0%BD%D0%B5%D0%B4%D0%B5%D0%BB%D1%8E")

    if response.status_code != 200:
        print("Ошибка при получении страницы:", response.status_code)
        exit()

    soup = BeautifulSoup(response.text, 'lxml')

    # Находим все <h2>
    h2_tags = soup.find_all('h2')

    # Ищем индексы нужных <h2>
    start_index = None
    end_index = None
    for i, h2 in enumerate(h2_tags):
        if "Группа - 74" in h2.get_text(strip=True):
            start_index = i
        elif "Группа - 75" in h2.get_text(strip=True) and start_index is not None:
            end_index = i
            break

    if start_index is None or end_index is None:
        print("Не найдены группы 'Группа - 74' или 'Группа - 75'!")
        exit()

    start_h2 = h2_tags[start_index]
    end_h2 = h2_tags[end_index]
    extracted_content = []
    current_element = start_h2
    while current_element and current_element != end_h2:
        if not isinstance(current_element, str) or current_element.strip():
            extracted_content.append(str(current_element))
        current_element = current_element.next_sibling

    extracted_soup = BeautifulSoup(''.join(extracted_content), 'lxml')

    # Извлекаем даты из <h3>
    h3_tag = extracted_soup.find('h3')
    if not h3_tag:
        print("Не найдены даты в <h3>!")
        exit()
    date_range = h3_tag.get_text(strip=True).split(' - ')
    start_date = datetime.strptime(date_range[0], '%d.%m.%Y')
    end_date = datetime.strptime(date_range[1], '%d.%m.%Y')

    # Генерируем список дат
    dates = []
    current_date = start_date
    while current_date <= end_date:
        dates.append(current_date.strftime('%d.%m.%Y'))
        current_date += timedelta(days=1)

    # Находим таблицу
    table = extracted_soup.find('table')
    if not table:
        print("Таблица не найдена!")
        exit()

    # Извлекаем строки таблицы (пропускаем первые две с заголовками)
    rows = table.find_all('tr')[2:]

    # Функция очистки HTML -> текст
    def clean_text(tag):
        if tag is None:
            return ""
        # <br/> превращаем в разделитель " | "
        text = tag.get_text(separator=' | ', strip=True)
        text = text.replace('\xa0', ' ')
        text = re.sub(r'\s+', ' ', text).strip()
        return text

    # Формируем расписание по дням
    schedule_by_date = {date: [] for date in dates}
    for row in rows:
        cells = row.find_all(['th', 'td'])
        if not cells:
            continue
        lesson_number = cells[0].get_text(strip=True)
        for day_idx, date in enumerate(dates):
            cell_idx = 1 + day_idx * 2
            if cell_idx + 1 < len(cells):
                discipline_text = clean_text(cells[cell_idx])
                room_text = clean_text(cells[cell_idx + 1])
                # если обе ячейки пусты, пропускаем
                if discipline_text == "" and room_text == "":
                    continue
                schedule_by_date[date].append((lesson_number, discipline_text, room_text))

    # Печать с днём недели, разделителем и переносом кабинетов
    weekday_names = ["📅 Понедельник","📅 Вторник","📅 Среда","📅 Четверг","📅 Пятница","📅 Суббота","📅 Воскресенье"]
    PAIR_SEPARATOR = "-" * 38
    subgroup_split_re = re.compile(r'(?=\d+\.)')
    room_split_sep = re.compile(r'\s*\|\s*')

    output_lines = []

    for date in dates:
        dt = datetime.strptime(date, '%d.%m.%Y')
        weekday = weekday_names[dt.weekday()]

        # пустая строка перед днём и заголовок
        output_lines.append("")
        output_lines.append(f"<b>{weekday} - {date}</b>")

        lessons = schedule_by_date.get(date, [])
        if not lessons:
            output_lines.append("--")
            output_lines.append("")  # двойной перевод
            continue

        for idx, (lesson_number, discipline, room) in enumerate(lessons):
            ln = lesson_number.strip()
            if not ln.endswith('.'):
                ln = ln + '.'
            output_lines.append(f"<b>{ln}</b>")

            if re.search(r'\d+\.', discipline):
                subparts = [s.strip() for s in subgroup_split_re.split(discipline) if s.strip()]
                rooms_all = [r.strip() for r in room_split_sep.split(room) if r.strip()]
                equal_counts = (len(subparts) == len(rooms_all) and len(subparts) > 1)

                for i, sub in enumerate(subparts):
                    output_lines.append(sub)
                    if equal_counts:
                        r = rooms_all[i]
                        output_lines.append(f"Каб: {r}" if r and r != '-' else "Каб: -")
                    else:
                        if rooms_all:
                            for r in rooms_all:
                                output_lines.append(f"Каб: {r}" if r and r != '-' else "Каб: -")
                        else:
                            output_lines.append("Каб: -")
            else:
                output_lines.append(discipline)
                rooms = [r.strip() for r in room_split_sep.split(room) if r.strip()]
                rooms = [r for r in rooms if r != '-']
                if rooms:
                    for r in rooms:
                        output_lines.append(f"Каб: {r}")
                else:
                    output_lines.append("Каб: -")

            if idx != len(lessons) - 1:
                output_lines.append(PAIR_SEPARATOR)

        output_lines.append("")  # двойной перевод между днями
        output_lines.append("")

    final_text = "\n".join(output_lines)

    # (опционально) показать результат в консоли
    # print(final_text)

    def clean_final_text(text: str) -> str:
        # обработаем построчно: схлопываем подряд идущие '|' и убираем '|' по краям строки
        out_lines = []
        for line in text.splitlines():
            # заменим NBSP
            line = line.replace('\xa0', ' ')
            # схлопываем подряд идущие '|' с любыми пробелами вокруг в один ' | '
            line = re.sub(r'(?:\s*\|\s*)+', ' | ', line)
            # убираем ведущие/замыкающие '|' и пробелы
            line = re.sub(r'^\s*\|\s*', '', line)
            line = re.sub(r'\s*\|\s*$', '', line)
            # убираем лишние пробелы
            line = re.sub(r'\s+', ' ', line).rstrip()
            out_lines.append(line)
        return "\n".join(out_lines)

    cleaned_final = clean_final_text(final_text)
    # print(cleaned_final)
    push_weekly_schedule(cleaned_final)
    return cleaned_final

if __name__ == "__main__":
    actual_schedule = get_schedule()
    # save_schedule_to_redis(actual_schedule, host="localhost", port=6379, db=0)


