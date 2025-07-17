import random
import re
from dataclasses import dataclass
from pathlib import Path

RND = random.SystemRandom()


@dataclass
class Move:
    grade: float
    move: str

    def __post_init__(self):
        self.grade = round(self.grade, 2)


def find_move() -> Move:
    text = Path('/home/alex/tmp/tmp.txt').read_text()
    moves = []
    for m in re.finditer(r'\d+\s+([\-+]?[\d.]+)\s+\d+\.+([\wx+]+) ', text):
        moves.append(Move(float(m.group(1)), m.group(2)))

    sign = 0
    head = moves[0]
    tail = moves[-1]
    if len(moves) == 0:
        return Move(0, 'Not found')
    elif len(moves) == 1:
        return head
    elif len(moves) > 1:
        if head.grade == tail.grade:
            return RND.choice(moves)
        elif head.grade > tail.grade:
            sign = 1
        else:
            sign = -1

    bound = round(-sign * RND.choice([0, 0.5, 1, 1.5, 2]) * RND.random() + head.grade, 2)
    min_grade = min(head.grade, bound)
    max_grade = max(head.grade, bound)
    # print('range: ', min_grade, max_grade)
    choice = [m for m in moves if min_grade <= m.grade <= max_grade]
    return RND.choice(choice)


def main():
    m = find_move()
    # print(m.grade, m.move)
    print(m.move)


if __name__ == '__main__':
    main()
