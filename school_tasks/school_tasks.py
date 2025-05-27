import random

seed = random.randint(111, 2333444555)
print('seed: ', seed)
rnd = random.Random(seed)

MINUS = 'minus'
PLUS = 'plus'
TEENS = 'teens'


def div(a):
    if not (0 <= a <= 99):
        raise ValueError('not (0 <= a <= 99)')

    d = a // 10
    e = a % 10
    return (d, e)


def just():
    tasks = []
    while len(tasks) < 20:
        op = rnd.choice([PLUS, MINUS, TEENS])
        if op == PLUS:
            task = None
            while task is None:
                n1 = rnd.randint(1, 99)
                n2 = rnd.randint(1, 99)
                if n1 + n2 < 100:
                    d1, e1 = div(n1)
                    d2, e2 = div(n2)
                    if d1 + d2 < 10 and e1 + e2 < 10:
                        task = f'{n1} + {n2} = '
            tasks.append(task)
        elif op == MINUS:
            task = None
            while task is None:
                a = rnd.randint(1, 99)
                b = rnd.randint(1, 99)
                n1 = min(a, b)
                n2 = max(a, b)
                if n1 != n2:
                    d1, e1 = div(n1)
                    d2, e2 = div(n2)
                    if d1 <= d2 and e1 <= e2:
                        task = f'{n2} - {n1} = '
            tasks.append(task)
        elif op == TEENS:
            task = None
            while task is None:
                a = rnd.randint(1, 19)
                b = rnd.randint(1, 19)
                if a != b:
                    n1 = min(a, b)
                    n2 = max(a, b)
                    if 10 <= n1 + n2 <= 20:
                        task = f'{n1} + {n2} = '
                    elif n2 > 10:
                        task = f'{n2} - {n1} = '
            tasks.append(task)

    for task in tasks:
        print(task)


if __name__ == '__main__':
    print()
    just()
