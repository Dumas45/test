import doctest
from just_test import texts


def test_doctests_texts_books_prepare_direct_speech():
    """Run doctests in the 'texts.books.prepare.direct_speech' module."""
    failure_count, test_count = doctest.testmod(texts.books.prepare.direct_speech, verbose=True)
    assert failure_count == 0, f"{failure_count} doctests failed out of {test_count}"
    assert test_count, "At least one doctest passed"


def test_doctests_texts_books_prepare_sent_tokenize():
    """Run doctests in the 'texts.books.prepare.sent_tokenize' module."""
    failure_count, test_count = doctest.testmod(texts.books.prepare.sent_tokenize, verbose=True)
    assert failure_count == 0, f"{failure_count} doctests failed out of {test_count}"
    assert test_count, "At least one doctest passed"
