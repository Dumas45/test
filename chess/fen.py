import argparse
import re


def draw_fen(fen: str):
    m = re.search(r'(?P<fen>\w+(/\w+)+)(\s(?P<side>\w))?', fen)
    if not m:
        raise ValueError('Invalid FEN')
    else:
        fen = m.group('fen')
        side = m.group('side')

    res = []
    parts = fen.split('/')
    for row_idx, line in enumerate(parts):
        top_row = row_idx == 0
        bottom_row = row_idx == len(parts) - 1
        row = '|'
        for c in line:
            if c in '123456789':
                row += ' .' * int(c)
            else:
                row += ' '
                row += c

        row += ' |'
        if top_row and side in ('b', 'B') or bottom_row and side in ('w', 'W'):
            row += ' *'

        res.append(row)

    return res


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'fen', type=str
    )

    args = parser.parse_args()

    print()
    for el in draw_fen(args.fen):
        print(el)
    print()
