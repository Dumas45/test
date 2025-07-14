import io
import itertools
import re

import pytest

from texts.paragraphs_reader import TextParagraphsReader

TEST_CASES = [
    {
        "text": "",
        "paragraphs": [],
    },
    {
        "text": '\n     \n \n\n\n      \n    \n\n',
        "paragraphs": [],
    },
    {
        "text": '\n     \n \n\n------\n      \n    \n\n',
        "paragraphs": [],
    },
    {
        "text": '\n     \n \n\n---AAA---\n      \n    \n\n',
        "paragraphs": ['---AAA---'],
    },
    {
        "text": '\n     \n \n\n- AAA-----\n      \n    \n\n',
        "paragraphs": ['- AAA-----'],
    },
    {
        "text": '\n     \n \n\nAAA\nBBB\n      \n    \n\n',
        "paragraphs": ['AAA\nBBB'],
    },
    {
        "text": '\n     \n \n\nAAA\n   BBB\n      \n    \n\n',
        "paragraphs": ['AAA\n   BBB'],
    },
    {
        "text": '\n     \n \n\nAAA\n\n   BBB\n      \n    \n\n',
        "paragraphs": ['AAA', 'BBB'],
    },
    {
        "text": "This is a single line text.",
        "paragraphs": ["This is a single line text."],
    },
    {
        "text": (
            "Paragraph one.\n"
            "\n"
            "Paragraph two.\n"
            "\n"
            "Paragraph three."
        ),
        "paragraphs": ["Paragraph one.", "Paragraph two.", "Paragraph three."],
    },
    {
        "read_chunk_size": 15,
        "text": (
            "Paragraph one.\n"
            "\n"
            "Paragraph two.\n"
            "\n"
            "Paragraph three."
        ),
        "paragraphs": ["Paragraph one.", "Paragraph two.", "Paragraph three."],
    },
    {
        "read_chunk_size": 25,
        "text": (
            "Paragraph one.\n"
            "\n"
            "Paragraph two.\n"
            "\n"
            "Paragraph three."
        ),
        "paragraphs": ["Paragraph one.", "Paragraph two.", "Paragraph three."],
    },
    {
        "read_chunk_size": 28,
        "text": (
            '"Why with an M?" said Alice.\n'
            '\n'
            '\n'
            '"Why not?" said the March Hare.\n'
            '\n'
            '\n'
            'Alice was silent.\n'
            '\n'
            '\n'
        ),
        "paragraphs": [
            '"Why with an M?" said Alice.',
            '"Why not?" said the March Hare.',
            'Alice was silent.'
        ],
    },
    {
        "read_chunk_size": 29,
        "text": (
            '"Why with an M?" said Alice.\n'
            '\n'
            '\n'
            '"Why not?" said the March Hare.\n'
            '\n'
            '\n'
            'Alice was silent.\n'
            '\n'
            '\n'
        ),
        "paragraphs": [
            '"Why with an M?" said Alice.',
            '"Why not?" said the March Hare.',
            'Alice was silent.'
        ],
    },
    {
        "read_chunk_size": 30,
        "text": (
            '"Why with an M?" said Alice.\n'
            '\n'
            '\n'
            '"Why not?" said the March Hare.\n'
            '\n'
            '\n'
            'Alice was silent.\n'
            '\n'
            '\n'
        ),
        "paragraphs": [
            '"Why with an M?" said Alice.',
            '"Why not?" said the March Hare.',
            'Alice was silent.'
        ],
    },
    {
        "text": (
            '\n'
            'Here one of the guinea-pigs cheered, and was immediately suppressed by'
            'the officers of the court. (As that is rather a hard word, I will just'
            'explain to you how it was done. They had a large canvas bag, which tied\n'
            'up at the mouth with strings: into this they slipped the guinea-pig,\n'
            'head first, and then sat upon it.)\n'
            '\n'
            '“I’m glad I’ve seen that done,” thought Alice. “I’ve so often read in\n'
            'the newspapers, at the end of trials, “There was some attempts at\n'
            'applause, which was immediately suppressed by the officers of the\n'
            'court,” and I never understood what it meant till now.”\n'
            '\n'
            '“If that’s all you know about it, you may stand down,” continued the\n'
            'King.\n'
            '\n'
            '“I can’t go no lower,” said the Hatter: “I’m on the floor, as it is.”\n'
            '\n'
            '“Then you may _sit_ down,” the King replied.\n'
            '\n'
            'Here the other guinea-pig cheered, and was suppressed.\n'
            '\n'
            '“Come, that finished the guinea-pigs!” thought Alice. “Now we shall get\n'
            'on better.”\n'
            '\n'
            '“I’d rather finish my tea,” said the Hatter, with an anxious look at\n'
            'the Queen, who was reading the list of singers.\n'
            '\n'
            '“You may go,” said the King, and the Hatter hurriedly left the court,\n'
            'without even waiting to put his shoes on.\n'
            '\n'
            '“—and just take his head off outside,” the Queen added to one of the\n'
            'officers: but the Hatter was out of sight before the officer could get\n'
            'to the door.\n'
            '\n'
            '“Call the next witness!” said the King.\n'
            '\n'
        ),
        "paragraphs": [
            (
                'Here one of the guinea-pigs cheered, and was immediately suppressed by'
                'the officers of the court. (As that is rather a hard word, I will just'
                'explain to you how it was done. They had a large canvas bag, which tied\n'
                'up at the mouth with strings: into this they slipped the guinea-pig,\n'
                'head first, and then sat upon it.)'
            ),
            (
                '“I’m glad I’ve seen that done,” thought Alice. “I’ve so often read in\n'
                'the newspapers, at the end of trials, “There was some attempts at\n'
                'applause, which was immediately suppressed by the officers of the\n'
                'court,” and I never understood what it meant till now.”'
            ),
            (
                '“If that’s all you know about it, you may stand down,” continued the\n'
                'King.'
            ),
            (
                '“I can’t go no lower,” said the Hatter: “I’m on the floor, as it is.”'
                ),
            (
                '“Then you may _sit_ down,” the King replied.'
            ),
            (
                'Here the other guinea-pig cheered, and was suppressed.'
            ),
            (
                '“Come, that finished the guinea-pigs!” thought Alice. “Now we shall get\n'
                'on better.”'
            ),
            (
                '“I’d rather finish my tea,” said the Hatter, with an anxious look at\n'
                'the Queen, who was reading the list of singers.'
            ),
            (
                '“You may go,” said the King, and the Hatter hurriedly left the court,\n'
                'without even waiting to put his shoes on.'
            ),
            (
                '“—and just take his head off outside,” the Queen added to one of the\n'
                'officers: but the Hatter was out of sight before the officer could get\n'
                'to the door.'
            ),
            (
                '“Call the next witness!” said the King.'
            ),
        ],
    },
]


@pytest.mark.parametrize(
    "data", TEST_CASES
)
def test_next_with_various_texts(data):
    text = data['text']
    expected_paragraphs = data['paragraphs']
    read_chunk_size = data.get('read_chunk_size', None)

    text_stream = io.StringIO(text)
    reader = TextParagraphsReader(text_stream, read_chunk_size=read_chunk_size)

    paragraphs = []
    try:
        while True:
            paragraphs.append(next(reader))
    except StopIteration:
        pass

    assert paragraphs == expected_paragraphs


@pytest.mark.parametrize(
    "rep_text, length",
    itertools.product(
        [
            "Plenty of ",
            '"See it"  ',
            "Plenty of\n",
            '"See it"\n\n',
        ],
        list(range(1, 24))
    )
)
def test_next_with_replicable_text(rep_text, length):
    if re.search(r'\n\W*\n', rep_text):
        expected_paragraphs = [rep_text.strip() for _ in range(length)]
    else:
        expected_paragraphs = [(rep_text * length).strip()]

    # Take such a parameter size that with each iteration there is a shift
    # in the location of the split relative to the replicable piece of text.
    read_chunk_size = 2 * len(rep_text) - 1

    text_stream = io.StringIO(rep_text * length)
    reader = TextParagraphsReader(text_stream, read_chunk_size=read_chunk_size)

    paragraphs = []
    try:
        while True:
            paragraphs.append(next(reader))
    except StopIteration:
        pass

    assert paragraphs == expected_paragraphs


@pytest.mark.parametrize(
    "data", TEST_CASES
)
def test_read_with_various_texts(data):
    text = data['text']
    expected_paragraphs = data['paragraphs']
    read_chunk_size = data.get('read_chunk_size', None)

    text_stream = io.StringIO(text)
    reader = TextParagraphsReader(text_stream, read_chunk_size=read_chunk_size)

    paragraphs = []
    while True:
        paragraph = reader.read()
        if not paragraph:
            break
        paragraphs.append(paragraph)

    assert paragraphs == expected_paragraphs


@pytest.mark.parametrize(
    "data", TEST_CASES
)
def test_read_all_with_various_texts(data):
    text = data['text']
    expected_paragraphs = data['paragraphs']
    read_chunk_size = data.get('read_chunk_size', None)

    text_stream = io.StringIO(text)
    reader = TextParagraphsReader(text_stream, read_chunk_size=read_chunk_size)

    paragraphs = reader.read_all()

    assert paragraphs == expected_paragraphs


def test_parameter_max_chunks_in_paragraph():
    text = (
        '"How doth the little crocodile '
        'Improve his shining tail, '
        'And pour the waters of the Nile '
        'On every golden scale! '
        '"How cheerfully he seems to grin, '
        'How neatly spread his claws, '
        'And welcome little fishes in '
        'With gently smiling jaws!"'
    )
    expected_paragraphs = [
        '"How doth the little',
        'crocodile Improve his shining tail,',
        'And pour the waters of the Nile',
        'On every golden scale! "How',
        'cheerfully he seems to grin, How',
        'neatly spread his claws, And',
        'welcome little fishes in With',
        'gently smiling jaws!"'
    ]

    text_stream = io.StringIO(text)
    reader = TextParagraphsReader(text_stream, read_chunk_size=15, max_chunks_in_paragraph=2)

    paragraphs = []
    try:
        while True:
            paragraphs.append(next(reader))
    except StopIteration:
        pass

    assert paragraphs == expected_paragraphs
