import hashlib
import random
import re
import secrets
from collections import Counter
from pathlib import Path
from typing import Optional

IGNORED_WORDS = (
)

STOP_CHARS = (
    '.',
    '!',
    '?',
)


class SentenceGenerator:
    def __init__(self):
        text = Path('/home/alex/Downloads/text-books/11-0.txt').read_text(encoding='UTF-8')
        it = re.finditer(r'(\w+)|([.!?])', text)
        counter = Counter()
        stop = True
        first = Counter()
        data = {}
        prev_word = None
        while True:
            m = next(it, None)
            if not m:
                break
            else:
                word = m.group().lower()
                word = word.replace('_', '')
                if word in STOP_CHARS or word in IGNORED_WORDS or len(word) > 77 or len(word) < 1:
                    prev_word = None
                    if word in STOP_CHARS:
                        stop = True
                else:
                    if stop:
                        first[word] += 1
                        stop = False

                    counter[word] += 1
                    if word not in data:
                        data[word] = Counter()
                    if prev_word:
                        data[prev_word][word] += 1
                    prev_word = word

        self.counter = Counter({
            m: c for m, c in counter.items() if len(data.get(m, {})) > 2
        })
        self.first = first
        self.data = data

    @staticmethod
    def dig_sum(string):
        h = hashlib.sha1()
        h.update(string.encode('UTF-8'))
        return random.Random(sum(h.digest())).randint(0, 171181191)

    def get_word(self, mark: str, prev: Optional[str] = None) -> str:
        if prev:
            counter = self.data.get(prev, None)
            if counter:
                counter = Counter({
                    m: c for m, c in counter.items() if m in self.counter
                })
            if not counter:
                counter = self.counter
        else:
            counter = self.first

        length = len(counter)
        length = min(length, max(4, length // 4))

        if length == 0:
            return 'none'

        checksum = self.dig_sum(mark)
        mc = list(counter.most_common()[:length])
        idx = checksum % len(mc)
        return mc[idx][0]

    def get_sentence(self, marks: list[str]) -> str:
        res = []
        word = None
        for mark in marks:
            word = self.get_word(mark=mark, prev=word)
            res.append(word)

        return ' '.join(res)


def just():
    gen = SentenceGenerator()

    for i in range(20):
        marks = [secrets.token_urlsafe(6) for _ in range(random.randint(3, 15))]
        print(gen.get_sentence(marks))


if __name__ == '__main__':
    just()
