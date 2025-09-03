import re
import redis

def extract_day_schedule(final_text: str, target_date: str) -> str:
    # Normalize the target date to match the format in the text
    target_date = target_date.strip().replace(',', '.').replace('/', '.')
    if not re.match(r'\d{2}\.\d{2}\.\d{4}', target_date):
        raise ValueError("Invalid date format. Expected 'dd.mm.yyyy'")

    # Split the final_text into lines
    lines = final_text.strip().split('\n')

    # Find the starting index of the target day
    start_idx = None
    for i, line in enumerate(lines):
        # Ищем дату в формате "Четверг - 04.09.2025" (с дефисом)
        if re.search(r' - ' + re.escape(target_date) + r'</b>', line.strip()):
            start_idx = i
            break

    if start_idx is None:
        return f"No schedule found for {target_date}"

    # Collect lines until we hit the end of the day's content
    extracted_lines = [lines[start_idx]]
    i = start_idx + 1
    empty_count = 0
    while i < len(lines):
        line = lines[i].strip()
        # Проверяем начало следующего дня (с дефисом)
        if re.match(r'<b>.* - \d{2}\.\d{2}\.\d{4}</b>', line):
            # Start of next day
            break
        extracted_lines.append(lines[i])
        if line == '':
            empty_count += 1
        else:
            empty_count = 0
        if empty_count >= 2:
            break
        i += 1

    # Join back and strip trailing empties
    result = '\n'.join(extracted_lines).rstrip('\n')
    return result
