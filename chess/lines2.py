from collections import defaultdict
import hashlib
import re

INPUT_PATH = '/home/alex/data/chess/lines.pgn'
OUTPUT_PATH = '/home/alex/data/chess/lines-flat.pgn'
OUTPUT_PATH_SHORT = '/home/alex/data/chess/lines-short.pgn'


def get_letter(s: str) -> str:
    vocab = 'BARCELONA'
    h = hashlib.new('sm3', s.encode())
    idx = sum(h.digest()[-4:]) % len(vocab)
    return vocab[idx]


def get_bar_code(text_line):
    moves = re.findall(r'\S+', text_line)
    letters = []
    step = 4
    i = 0
    while i < len(moves) // step:
        parts = moves[i * step:(i + 1) * step]
        i += 1
        if parts:
            letters.append(get_letter(''.join(parts)))

    return ''.join(letters) or '0'


def form_line(stack):
    moves = []
    for i, chunk in enumerate(stack):
        if i == len(stack) - 1:
            moves.extend(chunk)
        else:
            moves.extend(chunk[:-1])

    moves.append('*')
    return ' '.join(moves)


def get_moves_part(line: str) -> str:
    m = re.search(r'(?P<moves>((\s+)?(\d+)?\w+\S?)+)\s*(?P<suffix>.*)?', line)
    return m.group('moves')


def trim_line(line: str) -> str:
    m = re.search(r'(?P<moves>((\s+)?(\d+)?\w+\S?)+)\s*(?P<suffix>.*)?', line)
    parts = re.findall(r'\S+', m.group('moves'))
    trim = 24 if len(parts) % 2 == 0 else 23
    parts = parts[:trim]
    suffix = m.group('suffix')
    if suffix:
        parts.append(suffix)

    return ' '.join(parts)


def prepare_variation_text(lines: list[str]) -> str:
    text = ' '.join(lines)
    text = re.sub(r'\{[^}]*}', '', text)
    text = re.sub(r'\d+\.{3}', '', text)
    text = re.sub(r'\s\s+', ' ', text)
    text = re.sub(r'\.\s+', '.', text)
    text = re.sub(r'\(\s+', '(', text)
    text = re.sub(r'\s+\)', ')', text)
    return text


def traverse_variation_text(text: str) -> list[str]:
    res = []
    stack = [[]]
    it = re.finditer(r'([^()]*)([()]?)', text)
    for m in it:
        items = re.findall(r'\S+', m.group(1))
        closing = m.group(2) == ')'
        stack[-1].extend(items)

        if closing:
            line = form_line(stack)
            res.append(line)
            stack.pop()
        else:
            stack.append([])

    if stack:
        line = form_line(stack)
        res.append(line)

    return res


def process(headers: dict[str, str], sep_lines: list[str], is_first: bool) -> None:
    if not sep_lines:
        return

    text = prepare_variation_text(sep_lines)
    lines = traverse_variation_text(text)

    lines_map = defaultdict(list)
    for line in lines:
        short_line = trim_line(line)
        lines_map[short_line].append(line)

    if is_first:
        mode = 'w'
    else:
        mode = 'a'

    with open(OUTPUT_PATH, mode, encoding='UTF-8') as f:
        for text_line in sorted(lines):
            bar_code = get_bar_code(get_moves_part(text_line))

            _headers = dict(headers)
            _headers['White'] = f'{headers.get('White')} {bar_code}'
            for k, v in _headers.items():
                f.write(f'[{k} "{v}"]\n')

            f.write('\n')
            f.write(text_line)
            f.write('\n\n')

    with open(OUTPUT_PATH_SHORT, mode, encoding='UTF-8') as f:
        for short_line in sorted(lines_map.keys()):
            bar_code = get_bar_code(get_moves_part(short_line))

            long_lines = lines_map[short_line]
            if len(long_lines) == 1:
                short_line = long_lines[0]

            _headers = dict(headers)
            _headers['White'] = f'{headers.get('White')} {bar_code}'
            for k, v in _headers.items():
                f.write(f'[{k} "{v}"]\n')

            f.write('\n')
            f.write(short_line)
            f.write('\n\n')


def main() -> None:
    headers = {}
    lines = []
    is_first = True
    with open(INPUT_PATH, 'r', encoding='UTF-8') as input_file:
        while True:
            line = input_file.readline()
            if not line:
                if lines:
                    process(headers, lines, is_first)
                break

            line = line.rstrip('\n\r')
            if not re.search(r'\S', line):
                # blank string
                if lines:
                    process(headers, lines, is_first)
                    headers = {}
                    lines = []
                    is_first = False
            else:
                m = re.match(r'\[(\w+)\s*"(.*)"]', line)
                if m:
                    # header line
                    headers[m.group(1)] = m.group(2)
                else:
                    # variant line
                    lines.append(line)


if __name__ == '__main__':
    main()
