from itertools import chain
from pathlib import Path
import stat
from typing import Callable, TextIO

import nltk
from nltk.tokenize import word_tokenize
from nltk.tokenize.punkt import PunktSentenceTokenizer
import pandas as pd
from tqdm import tqdm

from just_test.texts.books.prepare.direct_speech import reconstruct_direct_speech
from just_test.texts.books.prepare.english import prepare_english_book_text
from just_test.texts.books.prepare.paragraphs_reader import TextParagraphsReader
from just_test.util.ml.sample_distributor import SampleDistributor
from just_test.util.validate import validate_type


class EnglishBookCBOWDatasetCreator:
    """
    A class to create a CBOW (Continuous Bag of Words) dataset from English book text data.

    This class processes raw text data, tokenizes it into sentences, and generates CBOW data
    with context-target pairs for training, validation, and testing splits.

    Attributes:
        MASK_TOKEN (str): A token used to pad the context window.
        raw_text_paths (list[str]): Paths to the raw text files to be processed.
        output_csv_path (str): Path to the output CSV file where the dataset will be saved.
        window_size (int): Size of the context window around the target word. Defaults to 5.
        train_ratio (float): Ratio of data to be used for training. Defaults to 0.7.
        val_ratio (float): Ratio of data to be used for validation. Defaults to 0.15.
        test_ratio (float): Ratio of data to be used for testing. Defaults to 0.15.
        seed (int): Random seed for reproducibility. Defaults to 1719.

    Methods:
        create():
            Processes the raw text file and generates the CBOW dataset saved to the output CSV file.

    """

    MASK_TOKEN = "<MASK>"

    def __init__(
            self,
            raw_text_paths: list[str],
            output_csv_path: str,
            window_size: int = 5,
            train_ratio: float = 0.7,
            val_ratio: float = 0.15,
            test_ratio: float = 0.15,
            seed: int = 1719
    ):
        self.raw_text_paths = raw_text_paths
        self.output_csv_path = output_csv_path
        self.window_size = window_size
        self.train_ratio = train_ratio
        self.val_ratio = val_ratio
        self.test_ratio = test_ratio
        self.seed = seed

        # Init
        self.sample_distributor = self._create_sample_distributor()
        self._header_printed = False

    def create(self):
        # Init
        self.sample_distributor = self._create_sample_distributor()
        self._header_printed = False

        # Check output file path. Clears the file if it already exists
        self._create_empty_output_file(Path(self.output_csv_path))

        # Create sentence tokenizer
        tokenizer = nltk.data.load('tokenizers/punkt/english.pickle')
        tokenizer = validate_type(tokenizer, PunktSentenceTokenizer)

        def sent_tokenize(_text: str) -> list[str]:
            return tokenizer.tokenize(_text)

        with open(self.output_csv_path, 'w', encoding='UTF-8') as output_file:
            for raw_text_path in self.raw_text_paths:
                with open(raw_text_path, 'r', encoding='UTF-8') as input_file:
                    paragraph_reader = TextParagraphsReader(input_file)

                    for text in tqdm(paragraph_reader, unit=' paragraph', desc='Processing'):
                        self._process_text(text, output_file, sent_tokenize=sent_tokenize)
                        self._header_printed = True

    def _create_sample_distributor(self) -> SampleDistributor:
        return SampleDistributor(
            train_ratio=self.train_ratio,
            val_ratio=self.val_ratio,
            test_ratio=self.test_ratio,
            seed=self.seed
        )

    @staticmethod
    def _create_empty_output_file(file_path: Path) -> None:
        """
        Check output file path. Clears the file if it already exists.
        
        Checking that it is physically possible to create a file at the specified path.

        """
        direct_parent_path = file_path.parent
        if not direct_parent_path.exists():
            parent_path = direct_parent_path
            while not parent_path.exists() and parent_path.name:
                parent_path = parent_path.parent
            mode = stat.S_IMODE(parent_path.stat().st_mode)
            direct_parent_path.mkdir(mode=mode, parents=True, exist_ok=True)

        file_path.write_text('')

    @staticmethod
    def _preprocess_text(text: str) -> str:
        words = word_tokenize(text, preserve_line=True)
        text = ' '.join(words)
        return text.lower()

    def _process_text(
            self,
            text: str,
            output_file: TextIO,
            sent_tokenize: Callable[[str], list[str]]
    ) -> None:
        sample = self.sample_distributor.get_sample(len(text))

        # Prepare text
        text = prepare_english_book_text(text)
        text = text.replace(';', '.')
        text = text.replace(':', '.')
        text = reconstruct_direct_speech(text, sent_tokenize=sent_tokenize)

        # Split into sentences
        sentences = sent_tokenize(text)
        sentences = [self._preprocess_text(s) for s in sentences]

        # Create windows
        window_size = self.window_size
        ngrams = [
            list(nltk.ngrams(
                [self.MASK_TOKEN] * window_size + sentence.split(' ')
                + [self.MASK_TOKEN] * window_size, window_size * 2 + 1
            ))
            for sentence in sentences
        ]
        windows = list(chain(*ngrams))

        # Create CBOW data
        data = []
        for window in windows:
            target_token = window[window_size]
            context = []
            for i, token in enumerate(window):
                if token == self.MASK_TOKEN or i == window_size:
                    continue
                else:
                    context.append(token)
            data.append([' '.join(token for token in context), target_token, sample])

        # Convert to dataframe
        df = pd.DataFrame(data, columns=['context', 'target', 'split'])
        df.to_csv(output_file, index=False, header=not self._header_printed)
