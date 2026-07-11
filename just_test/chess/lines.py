import random


class Lines:
    DEF_WEIGHT = 5

    def __init__(self, lines_number: int):
        self.seed = random.randint(111, 2333444555)
        self.rnd = random.Random(self.seed)
        self.lines_number = lines_number
        self.counter = 0
        self.weights = {}

    def __repr__(self):
        return (
            f'Lines: counter={repr(self.counter)}, weights={repr(self.weights)}, '
            f'lines_number={repr(self.lines_number)}, seed={repr(self.seed)}'
        )

    def variant(self, n=4):
        return self.rnd.randint(1, n)

    def weigh(self, variant: int, weight: int):
        self.weights[variant] = weight

    def line(self):
        base = []
        for variant in range(1, self.lines_number + 1, 1):
            weight = self.weights.get(variant, self.DEF_WEIGHT)
            base.extend(variant for _ in range(weight))

        line = self.rnd.choice(base)
        return f'Line: {line}   {("weight=%s" % self.weights[line] if line in self.weights else "NOT WEIGHED")}'

    def done(self):
        self.counter += 1
        return self.counter

    @staticmethod
    def help():
        print(
            "Commands:\n"
            "variant(n=4)\n"
            "weigh(variant: int, weight: int)\n"
            "line()\n"
            "done()"
        )
