from itertools import cycle
import random


class SampleDistributor:
    """Helper class to distribute samples into training, validation, and testing sets."""

    TRAIN = 'train'
    VAL = 'val'
    TEST = 'test'
    SAMPLES = (TRAIN, VAL, TEST)

    def __init__(self, train_ratio: float, val_ratio: float, test_ratio: float, seed: int):
        self.train_ratio = train_ratio
        self.val_ratio = val_ratio
        self.test_ratio = test_ratio

        self.train_length = 0
        self.val_length = 0
        self.test_length = 0
        self.sum_length = 0

        self.sample_cycle = cycle(self.SAMPLES)
        self.rnd = random.Random(seed)

    def _check_ratio(self, sample: str) -> bool:
        if self.sum_length < 1:
            return True

        if sample == self.TRAIN:
            return self.train_length / self.sum_length < self.train_ratio
        elif sample == self.VAL:
            return self.val_length / self.sum_length < self.val_ratio
        elif sample == self.TEST:
            return self.test_length / self.sum_length < self.test_ratio
        else:
            raise ValueError("Unknown sample type")

    def _update_ratio(self, sample: str, length: int) -> None:
        if sample == self.TRAIN:
            self.train_length += length
        elif sample == self.VAL:
            self.val_length += length
        elif sample == self.TEST:
            self.test_length += length
        else:
            raise ValueError("Unknown sample type")

        self.sum_length += length

    def get_sample(self, length) -> str:
        samp_length = len(self.SAMPLES)

        # Shift by random number
        for _ in range(self.rnd.randint(0, samp_length - 1)):
            next(self.sample_cycle)

        for i in range(samp_length):
            is_last = i == samp_length - 1
            sample = next(self.sample_cycle)
            if is_last or self._check_ratio(sample):
                self._update_ratio(sample, length)
                return sample

        raise ValueError("No sample available for the given ratios")
