from typing import List
import string
from collections import Counter
import re


def get_longest_diverse_words(file_path: str) -> List[str]:
    with open(file_path, 'r', encoding='utf-8') as file:
        words = set(word.strip(string.punctuation) for line in file for word in line.split())
    return sorted(words, key=lambda w: (len(set(w)), len(w)), reverse=True)[:10]


def get_rarest_char(file_path: str) -> str:
    with open(file_path, 'r', encoding='utf-8') as file:
        text = file.read()
    counter = Counter(text)
    return min(counter, key=counter.get)


def count_punctuation_chars(file_path: str) -> int:
    with open(file_path, 'r', encoding='utf-8') as file:
        text = file.read()
    return sum(1 for char in text if char in string.punctuation)


def count_non_ascii_chars(file_path: str) -> int:
    with open(file_path, 'r', encoding='utf-8') as file:
        text = file.read().encode().decode('unicode_escape')  # декодируем unicode escape в символы
    non_ascii_chars = re.findall(r'[^\x00-\x7F]', text)
    return len(non_ascii_chars)


def get_most_common_non_ascii_char(file_path: str) -> str:
    with open(file_path, 'r', encoding='utf-8') as file:
        text = file.read().encode().decode('unicode_escape')
    non_ascii_chars = re.findall(r'[^\x00-\x7F]', text)
    counter = Counter(non_ascii_chars)
    return counter.most_common(1)[0][0]


# пример
file_path = "data.txt"

# 10 самых длинных слов с наибольшим количеством уникальных символов
print("10 самых длинных слов с уникальными символами:")
print(get_longest_diverse_words(file_path))

# самый редкий символ
print("\nСамый редкий символ в документе:")
print(get_rarest_char(file_path))

# количество знаков пунктуации
print("\nКоличество знаков пунктуации:")
print(count_punctuation_chars(file_path))

# количество не-ASCII символов
print("\nКоличество не-ASCII символов:")
print(count_non_ascii_chars(file_path))

# самый частый не-ASCII символ
print("\nСамый частый не-ASCII символ:")
print(get_most_common_non_ascii_char(file_path))
