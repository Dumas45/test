import hashlib
import re

INPUT_PATH = '/home/alex/data/chess/lines.pgn'
OUTPUT_PATH = '/home/alex/data/chess/lines-flat.pgn'


def get_letter(s: str) -> str:
    vocab = 'barceiona'
    h = hashlib.new('sm3', s.encode())
    idx = sum(h.digest()[-4:]) % len(vocab)
    return vocab[idx]


def get_bar_code(text_line):
    moves = re.findall(r'\S+', text_line)
    bar = []
    i = 0
    while i < 5:
        parts = moves[i * 4:(i + 1) * 4]
        i += 1
        if parts:
            bar.append(get_letter(''.join(parts)))

    return ''.join(bar) or '0'


def form_line(stack):
    moves = []
    for i, chunk in enumerate(stack):
        if i == len(stack) - 1:
            moves.extend(chunk)
        else:
            moves.extend(chunk[:-1])

    moves.append('*')
    return ' '.join(moves)


def process(headers: dict[str, str], lines: list[str], is_first: bool) -> None:
    if not lines:
        return

    print()
    for k, v in headers.items():
        print(k, v)
    text = ' '.join(lines)
    text = re.sub(r'\{[^}]*}', '', text)
    text = re.sub(r'\d+\.{3}', '', text)
    text = re.sub(r'\s\s+', ' ', text)
    text = re.sub(r'\.\s+', '.', text)
    text = re.sub(r'\(\s+', '(', text)
    text = re.sub(r'\s+\)', ')', text)
    print(text)

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

    if is_first:
        mode = 'w'
    else:
        mode = 'a'

    with open(OUTPUT_PATH, mode) as f:
        for i, text_line in enumerate(res):
            print(text_line)
            _headers = dict(headers)
            # _headers['White'] = '%s %02d' % (headers.get('White'), i + 1)
            _headers['White'] = '%s %s' % (headers.get('White'), get_bar_code(text_line))
            for k, v in _headers.items():
                f.write('[%s "%s"]\n' % (k, v))

            f.write('\n')
            f.write(text_line)
            f.write('\n\n')


def main() -> None:
    headers = {}
    lines = []
    is_first = True
    with open(INPUT_PATH, 'r') as input_file:
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
