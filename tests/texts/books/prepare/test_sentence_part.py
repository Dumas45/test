import pytest

from just_test.texts.books.prepare.sentence_part import SentencePart

@pytest.mark.parametrize("test_case", [
        ('The Cat only grinned when it saw Alice. It looked good-natured', True),
        ('The Cat only grinned when it saw Alice. It looked good-natured ', True),
        ('They very soon came upon a Gryphon, lying fast asleep in the sun.', False),
        ('They very soon came upon a Gryphon, lying fast asleep in the sun. ', False),
        ('They very soon came upon a Gryphon, lying fast asleep in the sun, ', True),
        ('They very soon came upon a Gryphon, lying fast asleep in the sun,', True),
        ('They very soon came upon a Gryphon, lying fast asleep in the sun ', True),
        ('They very soon came upon a Gryphon, lying fast asleep in the sun', True),
        ("(If you don't know what a Gryphon is, look at the picture.)", False),
        ("(If you don't know what a Gryphon is, look at the picture. )", False),
        ("(If you don't know what a Gryphon is, look at the picture.) ", False),
        ("(If you don't know what a Gryphon is, look at the picture,) ", True),
        ("(If you don't know what a Gryphon is, look at the picture,)", True),
        ("(If you don't know what a Gryphon is, look at the picture) ", True),
        ("(If you don't know what a Gryphon is, look at the picture)", True),
        ('"How should I know?"', False),
        ('"How should I know? "', False),
        ('"How should I know?" ', False),
        ('"May it please your Majesty,"', True),
        ('"May it please your Majesty," ', True),
        ('"May it please your Majesty, "', True),
        ('"May it please your Majesty"', True),
        ('"May it please your Majesty" ', True),
        ('"May it please your Majesty "', True),
        ('"Up, lazy thing!"', False),
        ('"Up, lazy thing!" ', False),
        ('"Up, lazy thing! "', False),
    ]
)
def test_sentence_part_opened(test_case):
    text, opened = test_case
    sentence_part = SentencePart(text, direct=False)
    assert sentence_part.opened == opened


@pytest.mark.parametrize("test_case", [
        ('The Cat only grinned when it saw Alice. It looked good-natured', ''),
        ('The Cat only grinned when it saw Alice. It looked good-natured ', ''),
        ('They very soon came upon a Gryphon, lying fast asleep in the sun.', '.'),
        ('They very soon came upon a Gryphon, lying fast asleep in the sun. ', '.'),
        ('They very soon came upon a Gryphon, lying fast asleep in the sun, ', ','),
        ('They very soon came upon a Gryphon, lying fast asleep in the sun,', ','),
        ('They very soon came upon a Gryphon, lying fast asleep in the sun ', ''),
        ('They very soon came upon a Gryphon, lying fast asleep in the sun', ''),
        ("(If you don't know what a Gryphon is, look at the picture.)", '.'),
        ("(If you don't know what a Gryphon is, look at the picture. )", '.'),
        ("(If you don't know what a Gryphon is, look at the picture.) ", '.'),
        ("(If you don't know what a Gryphon is, look at the picture,) ", ','),
        ("(If you don't know what a Gryphon is, look at the picture,)", ','),
        ("(If you don't know what a Gryphon is, look at the picture) ", ''),
        ("(If you don't know what a Gryphon is, look at the picture)", ''),
        ('"How should I know?"', '?'),
        ('"How should I know? "', '?'),
        ('"How should I know?" ', '?'),
        ('"May it please your Majesty,"', ','),
        ('"May it please your Majesty," ', ','),
        ('"May it please your Majesty, "', ','),
        ('"May it please your Majesty"', ''),
        ('"May it please your Majesty" ', ''),
        ('"May it please your Majesty "', ''),
        ('"Up, lazy thing!"', '!'),
        ('"Up, lazy thing!" ', '!'),
        ('"Up, lazy thing! "', '!'),
    ]
)
def test_sentence_part_punct(test_case):
    text, punct = test_case
    sentence_part = SentencePart(text, direct=False)
    assert sentence_part.punct == punct


@pytest.mark.parametrize("test_case", [
        (
            'The Cat only grinned when it saw Alice. It looked good-natured',
            'The Cat only grinned when it saw Alice. It looked good-natured',
        ),
        (
            'The Cat only grinned when it saw Alice. It looked good-natured ',
            'The Cat only grinned when it saw Alice. It looked good-natured ',
        ),
        (
            'They very soon came upon a Gryphon, lying fast asleep in the sun.',
            'They very soon came upon a Gryphon, lying fast asleep in the sun',
        ),
        (
            'They very soon came upon a Gryphon, lying fast asleep in the sun. ',
            'They very soon came upon a Gryphon, lying fast asleep in the sun ',
        ),
        (
            'They very soon came upon a Gryphon, lying fast asleep in the sun, ',
            'They very soon came upon a Gryphon, lying fast asleep in the sun ',
        ),
        (
            'They very soon came upon a Gryphon, lying fast asleep in the sun,',
            'They very soon came upon a Gryphon, lying fast asleep in the sun',
        ),
        (
            'They very soon came upon a Gryphon, lying fast asleep in the sun ',
            'They very soon came upon a Gryphon, lying fast asleep in the sun ',
        ),
        (
            'They very soon came upon a Gryphon, lying fast asleep in the sun',
            'They very soon came upon a Gryphon, lying fast asleep in the sun',
        ),
        (
            "(If you don't know what a Gryphon is, look at the picture.)",
            "(If you don't know what a Gryphon is, look at the picture)",
        ),
        (
            "(If you don't know what a Gryphon is, look at the picture. )",
            "(If you don't know what a Gryphon is, look at the picture )",
        ),
        (
            "(If you don't know what a Gryphon is, look at the picture.) ",
            "(If you don't know what a Gryphon is, look at the picture) ",
        ),
        (
            "(If you don't know what a Gryphon is, look at the picture,) ",
            "(If you don't know what a Gryphon is, look at the picture) ",
        ),
        (
            "(If you don't know what a Gryphon is, look at the picture,)",
            "(If you don't know what a Gryphon is, look at the picture)",
        ),
        (
            "(If you don't know what a Gryphon is, look at the picture) ",
            "(If you don't know what a Gryphon is, look at the picture) ",
        ),
        (
            "(If you don't know what a Gryphon is, look at the picture)",
            "(If you don't know what a Gryphon is, look at the picture)",
        ),
        (
            '"How should I know?"',
            '"How should I know"',
        ),
        (
            '"How should I know? "',
            '"How should I know "',
        ),
        (
            '"How should I know?" ',
            '"How should I know" ',
        ),
        (
            '"May it please your Majesty,"',
            '"May it please your Majesty"',
        ),
        (
            '"May it please your Majesty," ',
            '"May it please your Majesty" ',
        ),
        (
            '"May it please your Majesty, "',
            '"May it please your Majesty "',
        ),
        (
            '"May it please your Majesty"',
            '"May it please your Majesty"',
        ),
        (
            '"May it please your Majesty" ',
            '"May it please your Majesty" ',
        ),
        (
            '"May it please your Majesty "',
            '"May it please your Majesty "',
        ),
        (
            '"Up, lazy thing!"',
            '"Up, lazy thing"',
        ),
        (
            '"Up, lazy thing!" ',
            '"Up, lazy thing" ',
        ),
        (
            '"Up, lazy thing! "',
            '"Up, lazy thing "',
        ),
    ]
)
def test_sentence_part_clear_punct(test_case):
    text, expected = test_case
    sentence_part = SentencePart(text, direct=False)
    sentence_part.clear_punct()
    assert sentence_part.text == expected
    assert sentence_part.opened is True


@pytest.mark.parametrize("test_case", [
        (
            'The Cat only grinned when it saw Alice. It looked good-natured',
            'The Cat only grinned when it saw Alice. It looked good-natured.',
        ),
        (
            'The Cat only grinned when it saw Alice. It looked good-natured ',
            'The Cat only grinned when it saw Alice. It looked good-natured. ',
        ),
        (
            'They very soon came upon a Gryphon, lying fast asleep in the sun.',
            'They very soon came upon a Gryphon, lying fast asleep in the sun.',
        ),
        (
            'They very soon came upon a Gryphon, lying fast asleep in the sun. ',
            'They very soon came upon a Gryphon, lying fast asleep in the sun. ',
        ),
        (
            'They very soon came upon a Gryphon, lying fast asleep in the sun, ',
            'They very soon came upon a Gryphon, lying fast asleep in the sun. ',
        ),
        (
            'They very soon came upon a Gryphon, lying fast asleep in the sun,',
            'They very soon came upon a Gryphon, lying fast asleep in the sun.',
        ),
        (
            'They very soon came upon a Gryphon, lying fast asleep in the sun ',
            'They very soon came upon a Gryphon, lying fast asleep in the sun. ',
        ),
        (
            'They very soon came upon a Gryphon, lying fast asleep in the sun',
            'They very soon came upon a Gryphon, lying fast asleep in the sun.',
        ),
        (
            "(If you don't know what a Gryphon is, look at the picture.)",
            "(If you don't know what a Gryphon is, look at the picture.)",
        ),
        (
            "(If you don't know what a Gryphon is, look at the picture. )",
            "(If you don't know what a Gryphon is, look at the picture. )",
        ),
        (
            "(If you don't know what a Gryphon is, look at the picture.) ",
            "(If you don't know what a Gryphon is, look at the picture.) ",
        ),
        (
            "(If you don't know what a Gryphon is, look at the picture,) ",
            "(If you don't know what a Gryphon is, look at the picture.) ",
        ),
        (
            "(If you don't know what a Gryphon is, look at the picture,)",
            "(If you don't know what a Gryphon is, look at the picture.)",
        ),
        (
            "(If you don't know what a Gryphon is, look at the picture) ",
            "(If you don't know what a Gryphon is, look at the picture.) ",
        ),
        (
            "(If you don't know what a Gryphon is, look at the picture)",
            "(If you don't know what a Gryphon is, look at the picture.)",
        ),
        (
            '"How should I know?"',
            '"How should I know?"',
        ),
        (
            '"How should I know? "',
            '"How should I know? "',
        ),
        (
            '"How should I know?" ',
            '"How should I know?" ',
        ),
        (
            '"May it please your Majesty,"',
            '"May it please your Majesty."',
        ),
        (
            '"May it please your Majesty," ',
            '"May it please your Majesty." ',
        ),
        (
            '"May it please your Majesty, "',
            '"May it please your Majesty. "',
        ),
        (
            '"May it please your Majesty"',
            '"May it please your Majesty."',
        ),
        (
            '"May it please your Majesty" ',
            '"May it please your Majesty." ',
        ),
        (
            '"May it please your Majesty "',
            '"May it please your Majesty. "',
        ),
        (
            '"Up, lazy thing!"',
            '"Up, lazy thing!"',
        ),
        (
            '"Up, lazy thing!" ',
            '"Up, lazy thing!" ',
        ),
        (
            '"Up, lazy thing! "',
            '"Up, lazy thing! "',
        ),
        (
            'A',
            'A.',
        ),
        (
            'A ',
            'A. ',
        ),
        (
            'A"',
            'A."',
        ),
        (
            'A)',
            'A.)',
        ),
        (
            'A")',
            'A.")',
        ),
        (
            'A\'"',
            'A.\'"',
        ),
        (
            'A,',
            'A.',
        ),
        (
            'A, ',
            'A. ',
        ),
        (
            'A,"',
            'A."',
        ),
        (
            'A,)',
            'A.)',
        ),
        (
            'A,")',
            'A.")',
        ),
        (
            'A,\'"',
            'A.\'"',
        ),
    ]
)
def test_sentence_part_close(test_case):
    text, expected = test_case
    sentence_part = SentencePart(text, direct=False)
    sentence_part.close()
    assert sentence_part.text == expected
    assert sentence_part.opened is False
