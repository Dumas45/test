import re

from typing import Callable, Optional

from just_test.texts.books.prepare.sent_tokenize import simple_sent_tokenize

# Matches sentences that end with a period, question mark,
# or exclamation mark, possibly followed by whitespace.
END_SENTENCE_REGEX = re.compile(r'.+[.?!]\W*$', re.DOTALL)

# Matches the last punctuation in a sentence, capturing the word letter
# before it, the punctuation itself, and any trailing non-word characters.
LAST_PUNCTUATION_REPLACEMENT_REGEX = re.compile(r'(\w)([!,.:;?]?)(\W*)$')


class SentencePart:
    """
    Represents a part of a sentence with associated properties and methods for manipulation.

    Attributes:
        text (str): The text content of the sentence part.
        direct (bool): Indicates whether the sentence part is direct speech.
        quoted_text (str): Optional, the quoted text if the sentence part is direct speech.
        sent_tokenize (Callable[[str], list[str]]): A callable function for tokenizing the text into sentences.
            By default, a less-than-precise regular expression-based function is used that treats abbreviations
            as the end of a sentence. Instead of the default value, use any model-based function.
    """
    def __init__(
            self,
            text: str,
            *,
            direct: bool = False,
            quoted_text: Optional[str] = None,
            sent_tokenize: Callable[[str], list[str]] =simple_sent_tokenize
    ):
        self.text = text
        self.direct = direct
        self._sent_tokenize = sent_tokenize
        self._quoted_text = quoted_text

    @property
    def quoted_text(self) -> str:
        return self._quoted_text or self.text

    @property
    def opened(self) -> bool:
        """Checks if the sentence is opened (does not end with . ? ! punctuation marks)."""
        return END_SENTENCE_REGEX.match(self.text) is None

    @property
    def is_multi_sentence(self) -> bool:
        """Determines if the text contains multiple sentences."""
        return len(self._sent_tokenize(self.text)) > 1

    @property
    def punct(self) -> str:
        """Retrieves the trailing punctuation from the text, if any."""
        m = LAST_PUNCTUATION_REPLACEMENT_REGEX.search(self.text)
        if m:
            return m.group(2)
        else:
            return ''

    def capitalize(self) -> None:
        """Capitalizes the first letter of the text if it is not already uppercase."""
        if self.text and not self.text[0].isupper():
            self.text = self.text[0].upper() + self.text[1:]

    def close(self) -> None:
        """Closes the sentence by adding a period if it is not already closed."""
        if self.opened:
            self.replace_punct('.')

    def replace_punct(self, punct: str) -> None:
        """Replace (or add if not present) the last punctuation in the text."""
        self.text = LAST_PUNCTUATION_REPLACEMENT_REGEX.sub(rf'\g<1>{punct}\g<3>', self.text)

    def clear_punct(self) -> None:
        """Removes trailing punctuation from the text."""
        self.text = LAST_PUNCTUATION_REPLACEMENT_REGEX.sub(r'\g<1>\g<3>', self.text)

    def sent_tokenize(self) -> list['SentencePart']:
        res = []
        for text in self._sent_tokenize(self.text):
            res.append(SentencePart(
                text,
                direct=self.direct,
                sent_tokenize=self._sent_tokenize
            ))

        return res

    def __str__(self) -> str:
        return repr(self)

    def __repr__(self) -> str:
        return f'SentencePart({self.text!r}, direct={self.direct!r})'
