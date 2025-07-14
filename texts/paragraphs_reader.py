import io
import re

from collections import deque
from typing import Deque, Optional


class TextParagraphsReader:
    """Utility class for reading text streams and splitting them into paragraphs.

    This class is both an Iterator and Iterable.

    Args:
        text_stream (io.TextIOBase): The input text stream to read from.
        read_chunk_size (int): The size of chunks to read from the text stream.
            Defaults to 4 KB.
        max_chunks_in_paragraph (int): The maximum number of chunks allowed in a
            single paragraph. Defaults to 100.
        delimiter_regex (re.Pattern): A regular expression used to split text into
            paragraphs. Defaults to splitting on blank lines.
        offcut_delimiter_regex (re.Pattern): A regular expression used to detect
            text fragments that end in the middle of a paragraph delimiter.

    Methods:
        read() -> str:
            Reads and returns the next paragraph from the text stream. Returns an
            empty string if no more paragraphs are available.

        read_all() -> list[str]:
            Reads and returns all paragraphs from the text stream as a list.

        __iter__() -> TextParagraphsReader:
            Returns the iterator object itself.

        __next__() -> str:
            Retrieves the next paragraph from the text stream. Raises StopIteration
            when no more paragraphs are available.
    """

    DEFAULT_DELIMITER_REGEX = re.compile(r'\r?\n(?:\W*\n)+\s*')
    DEFAULT_OFFCUT_DELIMITER_REGEX = re.compile(r'.+\r?\n\W*$', re.DOTALL)

    def __init__(
            self,
            text_stream: io.TextIOBase,
            read_chunk_size: Optional[int] = None,
            max_chunks_in_paragraph: Optional[int] = None,
            # Regular expression for splitting a read text fragment into paragraphs
            delimiter_regex: re.Pattern = DEFAULT_DELIMITER_REGEX,
            # Regular expression for a piece of text
            # that ends in the middle of a paragraph delimiter
            offcut_delimiter_regex: Optional[re.Pattern] = DEFAULT_OFFCUT_DELIMITER_REGEX,
    ):
        min_chunk_size = 15
        if read_chunk_size is None:
            read_chunk_size = 4 * 1024
        elif read_chunk_size < min_chunk_size:
            raise ValueError(f'read_chunk_size < {min_chunk_size}')

        min_max_chunks = 1
        if max_chunks_in_paragraph is None:
            max_chunks_in_paragraph = 100
        elif max_chunks_in_paragraph < min_max_chunks:
            raise ValueError(f'max_chunks_in_paragraph < {min_max_chunks}')

        self.text_stream = text_stream
        self.read_chunk_size = read_chunk_size
        self.max_chunks_in_paragraph = max_chunks_in_paragraph

        self.delimiter_regex = delimiter_regex
        self.offcut_delimiter_regex = offcut_delimiter_regex

        self.queue: Deque[list[str]] = deque([[]])
        self.eof = False  # end of file

    def read(self) -> str:
        """Reads and returns the next paragraph from the text stream.

        Returns:
            str: The next paragraph from the iterator, or an empty string if the iterator is exhausted.
        """
        return next(self, '')

    def read_all(self) -> list[str]:
        """Reads and returns all paragraphs from the text stream.

        This method exhausts the iterator and collects all paragraphs into a list.

            list[str]: A list of all paragraphs read from the text stream.
        """
        return list(self)

    def __iter__(self):
        return self

    def __next__(self):
        while True:
            if len(self.queue) > 1:
                return self._retrieve_paragraph()

            if self.eof:
                text = ''
            else:
                text = self.text_stream.read(self.read_chunk_size)

            if not text:
                self.eof = True
                while self.queue:
                    res = self._retrieve_paragraph()
                    if res:
                        return res

                raise StopIteration()

            parts = self.delimiter_regex.split(text)
            for part_idx, part in enumerate(parts):
                self._process_split_part(part, is_first=part_idx == 0)

    def _retrieve_paragraph(self) -> str:
        parts = self.queue.popleft()
        for i in range(-1, -len(parts) - 1, -1):
            parts[i] = parts[i].rstrip()
            if parts[i]:
                break

        return ''.join(parts)

    def _append_paragraph_part(self, part: str) -> None:
        if not self.queue:
            raise ValueError('Queue is empty, cannot process paragraph split part')

        peek = self.queue[-1]

        # Check for the maximum number of chunks in a paragraph
        if len(peek) >= self.max_chunks_in_paragraph:
            # Find the last non-empty chunk
            idx, last = -1, peek[-1]
            for i, chunk in reversed(list(enumerate(peek))):
                if chunk:
                    idx, last = i, chunk
                    break

            # Is there any whitespace in the last chunk?
            m = re.search(r'\s', last[::-1])
            if m:
                pos = len(last) - m.end()
                peek[idx] = last[:pos + 1]
                part = last[pos + 1:] + part
                self._append_paragraph(part)
                return

        peek.append(part)

    def _append_paragraph(self, part: str) -> None:
        if part:
            peek = [part]
        else:
            peek = []

        self.queue.append(peek)

    def _process_split_part(self, part: str, is_first: bool) -> None:
        if not self.queue:
            raise ValueError('Queue is empty, cannot process split part')

        peek = self.queue[-1]
        if peek:
            if part:
                if is_first:
                    self._process_continued_split_part(part)
                else:
                    self._append_paragraph(part)
            else:
                self._append_paragraph('')
        elif part:
            self._append_paragraph_part(part.lstrip())

    def _process_continued_split_part(self, part: str) -> None:
        if not self.queue:
            raise ValueError('Queue is empty, cannot process continued split part')

        peek = self.queue[-1]
        if not peek:
            raise ValueError(
                'Last part of the queue is empty, cannot process continued split part')

        previous = peek[-1]

        # If there is no indication that the previous piece of text
        # has ended by breaking the separator
        if self.offcut_delimiter_regex and not self.offcut_delimiter_regex.match(previous):
            self._append_paragraph_part(part)

        else:
            # The delimiter can be broken. Find out it
            parts = self.delimiter_regex.split(previous + part)
            if len(parts) == 2:
                peek[-1] = parts[0]
                self._append_paragraph(parts[1])
            else:
                # delimiter was not broken
                self._append_paragraph_part(part)
