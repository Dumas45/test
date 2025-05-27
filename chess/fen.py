import argparse


def draw_fen(fen: str):
    res = []
    for line in fen.split('/'):
        row = '|'
        for c in line:
            if c in '123456789':
                row += ' .' * int(c)
            else:
                row += ' '
                row += c

        res.append(row + ' |')

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
