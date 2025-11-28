"""
Запуск:
 - Поиск в строке: python lab2_hex_colors.py --input "background: #fff; color: #1a2b3c"
 - Поиск по URL:   python lab2_hex_colors.py --url https://example.com
 - Поиск в файле:  python lab2_hex_colors.py --file path/to/file.txt
 - Запуск тестов:   python lab2_hex_colors.py --run-tests

Описание:
 - Поддерживаемые форматы HEX: #RGB, #RGBA, #RRGGBB, #RRGGBBAA (регистронезависимо)
 - Регулярное выражение: r"\b#(?:[0-9A-Fa-f]{3}|[0-9A-Fa-f]{4}|[0-9A-Fa-f]{6}|[0-9A-Fa-f]{8})\b"

"""

import re
import argparse
import sys
import requests
import unittest
import tempfile
from typing import List

HEX_REGEX = re.compile(
    r"(?<![0-9A-Fa-f#])#(?:[0-9A-Fa-f]{3}|[0-9A-Fa-f]{4}|[0-9A-Fa-f]{6}|[0-9A-Fa-f]{8})(?![0-9A-Fa-f])"
)
# находит хеш-цвета длиной 3, 4, 6 или 8 (например, #fff, #abcd, #123456, #11223344) и игнорирует невалидные варианты.

def find_hex_colors(text: str) -> List[str]:
    """Найти все HEX-цвета в тексте. Возвращает список уникальных вхождений
    в порядке появления."""
    matches = HEX_REGEX.findall(text)
    # Сохранить порядок, удалить дубликаты
    seen = {}
    for m in matches:
        if m not in seen:
            seen[m] = True
    return list(seen.keys())


def fetch_url(url: str, timeout: int = 10) -> str:
    """Загрузить содержимое страницы по URL. Возвращает текст страницы или
    выдает исключение requests.RequestException."""
    resp = requests.get(url, timeout=timeout)
    resp.raise_for_status()
    # Попытаемся вернуть текст кодировке в utf-8 или в encoding, указанный сервером
    resp.encoding = resp.encoding or 'utf-8'
    return resp.text

#чтение из файла
def read_file(path: str) -> str:
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()


def generate_report(found: List[str]) -> str:
    """Генерирует простой текстовый отчет по найденным цветам."""
    lines = ["Отчет по найденным HEX-цветам:"]
    if not found:
        lines.append("  Цвета не найдены.")
    else:
        for i, c in enumerate(found, 1):
            fmt = c
            length = len(c) - 1  # длина без '#'
            lines.append(f"  {i}. {fmt} — {length} символов")
    return "\n".join(lines)

#------главная функ------
def main(argv=None):
    parser = argparse.ArgumentParser(description='Поиск HEX-цветов в тексте / URL / файле')
    parser.add_argument('--input', '-i', help='Прямая строка для поиска')
    parser.add_argument('--url', '-u', help='URL для поиска')
    parser.add_argument('--file', '-f', help='Путь к локальному файлу')
    parser.add_argument('--run-tests', '-t', action='store_true', help='Запустить unit-тесты')

    args = parser.parse_args(argv)

    if args.run_tests:
        # Запускаем тесты и выходим
        # unittest.main читает sys.argv, поэтому передаем корректный список
        unittest.main(argv=[sys.argv[0]], exit=False)
        return

    source_text = ''
    try:
        if args.input:
            source_text = args.input
        elif args.url:
            print(f'Загружаю URL: {args.url}')
            source_text = fetch_url(args.url)
        elif args.file:
            print(f'Читаю файл: {args.file}')
            source_text = read_file(args.file)
        else:
            # Если нет аргумента попросим ввести 
            print('Введите текст (Ctrl-D / Ctrl-Z + Enter для конца ввода):')
            source_text = sys.stdin.read()
    except Exception as e:
        print(f'Ошибка при получении данных: {e}')
        return

    found = find_hex_colors(source_text)
    report = generate_report(found)
    print('\n' + report + '\n')


# ----------------- Юнит тесты -----------------
class TestHexFinder(unittest.TestCase):
    def test_simple_3_hex(self):
        self.assertEqual(find_hex_colors('color: #fff;'), ['#fff'])

    def test_simple_6_hex(self):
        self.assertEqual(find_hex_colors('border: #1a2b3c; background:#ABCDEF;'), ['#1a2b3c', '#ABCDEF'])

    def test_short_and_long(self):
        txt = 'a #123 b #123456 c #abcd d #abcdef12 e #fff'
        self.assertEqual(find_hex_colors(txt), ['#123', '#123456', '#abcd', '#abcdef12', '#fff'])

    def test_invalid(self):
        txt = '#ab #12345 #1234z #12g #abcd5'
        self.assertEqual(find_hex_colors(txt), ['#1234'])

    def test_duplicates_preserved_order(self):
        txt = '#fff text #fff more #FFF and #123'
        self.assertEqual(find_hex_colors(txt), ['#fff', '#FFF', '#123'])

    def test_find_in_file(self):
        import os
        tf = tempfile.NamedTemporaryFile('w', delete=False, encoding='utf-8')
        try:
            tf.write('line1\ncolor: #0f0;\nline3 #00FF00')
            tf.close()
            data = read_file(tf.name)
            found = find_hex_colors(data)
            self.assertEqual(found, ['#0f0', '#00FF00'])
        finally:
            try:
                os.unlink(tf.name)
            except Exception:
                pass



if __name__ == '__main__':
    main()
