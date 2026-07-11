import re

from pathlib import Path

import pytest

from just_test.texts.books.prepare.direct_speech import reconstruct_direct_speech


RESOURCES_PATH = Path(__file__).parent / "../../../resources"
TEXT_CASES_PATH = RESOURCES_PATH / "texts/books/prepare/reconstruct_direct_speech_cases.txt"


def create_test_cases() -> list[tuple[str, str]]:
    with TEXT_CASES_PATH.open('r', encoding='utf-8') as fp:
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
def test_reconstruct_direct_speech(test_case):
    text, expected = test_case

    # Replace linebreaks with spaces
    text = re.sub(r'\s+', ' ', text)
    expected = re.sub(r'\s+', ' ', expected)

    result = reconstruct_direct_speech(text)
    assert result == expected
