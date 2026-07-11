import random as rnd

class RandomPool:
    def __init__(self):
        self.x: dict[str, list[int]] = {}
    def pick(self, key: str, num: int) -> int:
        try:
            return self.x[key].pop()
        except IndexError:
            return rnd.randint(1, num)
        except KeyError:
            self.x[key] = list(range(1, num + 1))
            rnd.shuffle(self.x[key])
            return self.pick(key, num)

pick = RandomPool().pick
