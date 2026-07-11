import re

# Matches the sentence boundary, based on punctuation marks
SENTENCE_BOUNDARY_REGEX = re.compile(r'\w[^\s\w]*([?!.]+[^\s\w,]*)\s+\S')


def simple_sent_tokenize(text: str) -> list[str]:
    """
    Turns the input text into a list of sentences based on punctuation marks.

    A less-than-precise regular expression-based function
    that treats abbreviations as the end of a sentence.
    Instead, use any model-based function.

    Args:
        text (str): The input text to be processed.

    Returns:
        list[str]: A list of sentences extracted from the input text.

    Example:

    >>> simple_sent_tokenize("Hello world! How are you? I'm fine.")
    ['Hello world!', 'How are you?', "I'm fine."]

    """
    res = []
    pos = 0
    for m in SENTENCE_BOUNDARY_REGEX.finditer(text):
        _, to_pos = m.regs[1]
        sentence = text[pos:to_pos].strip()
        res.append(sentence)
        pos = to_pos

    sentence = text[pos:].lstrip()
    if sentence:
        res.append(sentence)

    return res
