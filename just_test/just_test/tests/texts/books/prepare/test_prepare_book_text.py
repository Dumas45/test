import re

from pathlib import Path

import pytest

from just_test.texts.books.prepare.english import prepare_english_book_text

RESOURCES_PATH = Path(__file__).parent / "../../../resources"
BOOK_CASES_PATH = RESOURCES_PATH / "texts/books/prepare/prepare_english_book_cases.txt"


def create_test_cases() -> list[tuple[str, str]]:
    with BOOK_CASES_PATH.open('r', encoding='utf-8') as fp:
        file_text = fp.read(1000000)

    res = []
    for case_text in re.split(r'\n==================================================\n', file_text):
        case_parts = re.split(r'\n=\n', case_text)
        if len(case_parts) == 2:
            res.append(tuple(case_parts))
        elif not case_text.strip():
            continue
        else:
            raise ValueError(f'Invalid test case format: {case_text}')

    return res


@pytest.mark.parametrize("test_case", create_test_cases())
def test_prepare_english_book_text(test_case):
    text, expected = test_case
    result = prepare_english_book_text(text)
    assert result == expected
    print('--------------------------------')
    print(text)
