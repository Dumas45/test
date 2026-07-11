import re

from typing import Callable, Optional

from just_test.texts.books.prepare.sent_tokenize import simple_sent_tokenize
from just_test.texts.books.prepare.sentence_part import SentencePart

# Matches direct speech enclosed in double quotes, ensuring it contains
# at least one word and ends with a punctuation mark.
DIRECT_SPEECH_REGEX = re.compile(r'"[^"]*\w[^"]*(?:[!,.:;?]+\'?"|\'?"\s*$)')

# Matches secondary direct speech enclosed in single quotes,
# ensuring it contains at least one word and ends with a punctuation mark.
SECONDARY_DIRECT_SPEECH_REGEX = re.compile(r"(?:^|(?<=[,.:;?!]\s))'\w(?:[^']|'(?!\W))*[,.:;?!]+'")


def _split_text_to_parts(
        text: str,
        sent_tokenize: Callable[[str], list[str]] = simple_sent_tokenize,
        secondary: bool = False
) -> list[SentencePart]:
    """
    Splits the given text into parts based on direct speech patterns and other text segments.

    This function uses a regular expression to identify direct speech segments within the text.
    It separates these segments from the rest of the text and categorizes them as either direct
    speech or non-direct speech. Each segment is wrapped in a `SentencePart` object.

    Args:
        text (str): The input text to be split into parts.
        sent_tokenize (Callable[[str], list[str]]): A function for tokenizing sentences within
            each text segment. Defaults to `simple_sent_tokenize`.
        secondary

    Returns:
        list[SentencePart]: A list of `SentencePart` objects representing the split text segments.
            Each object contains the text segment, a flag indicating whether it is direct speech,
            and the sentence tokenizer function.
    """
    primary = not secondary
    if primary:
        quote = '"'
        pattern = DIRECT_SPEECH_REGEX
    else:
        pattern = SECONDARY_DIRECT_SPEECH_REGEX
        quote = "'"

    matches: list[re.Match] = list(pattern.finditer(text))
    parts: list[SentencePart] = []
    pos: int = 0
    for match in matches:
        start, end = match.span()
        if pos < start:
            # Non-direct speech
            part_text = text[pos:start].strip()
            if part_text:
                parts.append(SentencePart(part_text, direct=False, sent_tokenize=sent_tokenize))

        # Direct speech
        pos = end
        quoted_text: str = match.group().strip()
        part_text = quoted_text.strip(quote)
        if part_text:
            parts.append(SentencePart(part_text, direct=True, quoted_text=quoted_text, sent_tokenize=sent_tokenize))

    if pos < len(text):
        # Non-direct speech
        part_text = text[pos:].strip()
        if part_text:
            parts.append(SentencePart(part_text, direct=False, sent_tokenize=sent_tokenize))

    prev, last = ((None, None) + tuple(parts))[-2:]
    if last:
        # Corner case: When secondary direct speech at the end of primary speech
        # does not follow a punctuation mark, then it is attached to the previous part.
        if secondary and prev and last.direct and not prev.punct:
            prev.text = f'{prev.text} {last.text}'
            parts.pop()

        # Corner case: When the last part is direct speech without a final punctuation mark
        # and the previous part without the final punctuation mark,
        # then the last part is is marked as non-direct.
        if primary and last.direct and not last.punct:
            if prev and not prev.punct:
                last.direct = False
            else:
                last.close()

    return parts


def _is_quotation_part(parts: list[SentencePart], idx: int, ds_opened: bool) -> bool:
    """
    Determines whether a  part of direct speech is a quotation.

    For example, for the text

    ------------------------------
    "Ah! you'd want to take a thing or two with you," retorted "The Blue
    Posts," "if you was a-going to cross the Atlantic in a small boat."
    ------------------------------

    the part "The Blue Posts," is a quotation,
    the part "Ah! you'd want to take a thing or two with you," is a direct speech,
    the part "if you was a-going to cross the Atlantic in a small boat." is a direct speech.
    For the part "The Blue Posts," this function should return `True`.

    Args:
        parts (list[SentencePart]): A list of sentence parts.
        idx (int): The index of the current sentence part to check.
        ds_opened (bool): A flag indicating that the previous direct speech part is opened.

    Returns:
        bool: `True` if the part is a quotation, `False` otherwise.

    """
    if idx < 1:
        return False

    part = parts[idx]
    prev_part = parts[idx - 1]

    if not part.direct or prev_part.punct or prev_part.direct:
        return False

    if not ds_opened:
        return True

    for p in parts[idx + 1:]:
        if p.direct:
            return True

        if not p.opened or p.is_multi_sentence:
            break

    return False


def _reconstruct_text_parts(parts: list[SentencePart]) -> list[SentencePart]:
    """
    Reconstructs a list of parts of the text so that direct speech is separated as little as possible.

    Args:
        parts (list[SentencePart]): A list of `SentencePart` objects to be reconstructed.

    Returns:
        list[SentencePart]: A reconstructed list of `SentencePart` objects with proper
        capitalization, punctuation, and closure applied.

    Notes:
        - Direct speech parts are handled differently based on whether they are opened
          or closed, and whether the previous part is direct or non-direct.
        - Deferred parts are used to temporarily store non-direct parts that need to be
          appended later.
        - Multi-sentence parts are processed to ensure proper capitalization and closure.

    """
    res: list[SentencePart] = []
    deferred: list[SentencePart] = []
    ds_opened: bool = False
    prev_part: Optional[SentencePart] = None
    for idx, part in enumerate(parts):
        # Corner case: When direct speech turns out to be a quotation.
        if _is_quotation_part(parts, idx, ds_opened=ds_opened):
            part.direct = False
            part.text = part.quoted_text

        # Join the consecutive non-direct parts.
        if prev_part and not prev_part.direct and not part.direct:
            prev_part.text = f'{prev_part.text} {part.text}'
            continue

        if part.direct and prev_part and not ds_opened:
            prev_part.close()
            part.capitalize()

        # Closed part
        if not part.opened:
            ds_opened = False

            # Direct part
            if part.direct:
                res.append(part)
                if deferred:
                    deferred[-1].close()
                    res.extend(deferred)
                    deferred = []

            # Non-direct part
            else:
                # Corner case: if the previous part is direct and opened,
                # then close it and capitalize the current non-direct part.
                if prev_part and prev_part.opened:
                    prev_part.close()

                deferred.append(part)
                res.extend(deferred)
                deferred = []

        # Opened direct part
        elif part.direct:
            ds_opened = part.opened
            res.append(part)

        # Opened non-direct part while the previous direct part is opened
        elif ds_opened:
            # Multi-sentence part
            if part.is_multi_sentence:
                part.capitalize()
                res.extend(deferred)
                deferred = []
                res.append(part)
                ds_opened = False
                if prev_part:
                    prev_part.close()

            # Single sentence part
            else:
                deferred.append(part)

        # Opened non-direct part while the previous direct part is closed
        else:
            res.extend(deferred)
            deferred = []
            res.append(part)

        prev_part = part

    res.extend(deferred)
    return res


def reconstruct_direct_speech(
        text: str,
        sent_tokenize: Callable[[str], list[str]] = simple_sent_tokenize,
        secondary: bool = False
) -> str:
    """Reconstructs direct speech from a text.

    Args:
        text (str): The input text
        sent_tokenize (Callable[[str], list[str]]): A callable function for tokenizing the text into sentences.
            By default, a less-than-precise regular expression-based function is used that treats abbreviations
            as the end of a sentence. Instead of the default value, use any model-based function.
        secondary (bool): If True, the function treats the secondary direct speech pattern as the primary one.
            Defaults to False, meaning it uses the primary direct speech pattern.

    Returns:
        str: The reconstructed text

    Examples:

    >>> reconstruct_direct_speech('"Yes," said Alice, "we learned French and music."')
    'Yes, we learned French and music. Said Alice.'

    >>> reconstruct_direct_speech('"What a day!" he exclaimed.')
    'What a day! He exclaimed.'

    """
    primary = not secondary

    # Split text into parts:  str -> list[SentencePart]
    parts = _split_text_to_parts(text, sent_tokenize=sent_tokenize, secondary=secondary)

    if secondary:
        if len(parts) == 1:
            # Nothing to do
            return text
    else:
        # Reconstruct secondary direct speech
        for part in parts:
            if part.direct:
                part.text = reconstruct_direct_speech(
                    part.text,
                    sent_tokenize=sent_tokenize,
                    secondary=True
                )

    # Reconstruct text parts:  list[SentencePart] -> list[SentencePart]
    res = _reconstruct_text_parts(parts)

    # Post process:  list[SentencePart] -> list[SentencePart]
    for idx, part in enumerate(res):
        prev_part = (None if idx == 0 else res[idx - 1])
        is_last = idx == len(res) - 1

        if not prev_part and primary:
            part.capitalize()

        if prev_part and not prev_part.opened:
            part.capitalize()

        if is_last and primary:
            part.close()

    # Result:  list[SentencePart] -> str
    return ' '.join(p.text for p in res)
