from dataclasses import dataclass

import matplotlib.pyplot as plt


@dataclass
class RGB:
    r: int
    g: int
    b: int

    def __post_init__(self):
        if not (0 <= self.r <= 255):
            raise ValueError('Red in incorrect range')
        if not (0 <= self.g <= 255):
            raise ValueError('Green in incorrect range')
        if not (0 <= self.b <= 255):
            raise ValueError('Blue in incorrect range')

    def to_hex(self) -> str:
        return '#%02x%02x%02x' % (self.r, self.g, self.b)

    @classmethod
    def from_hex(cls, h):
        return cls(int(h[1:3], 16), int(h[3:5], 16), int(h[5:7], 16))

    def mix(self, other: 'RGB') -> 'RGB':
        b = 4
        d = b + 1
        return RGB((b * self.r + other.r) // d, (b * self.g + other.g) // d, (b * self.b + other.b) // d)

    def shift(self, r: int, g: int, b: int) -> 'RGB':
        return RGB(
            max(0, min(255, self.r + r)),
            max(0, min(255, self.g + g)),
            max(0, min(255, self.b + b))
        )


def main():
    grey_cs = ["#626c6c", "#7f8c8d", "#8c9a9b", "#9aaaab", "#aabbbc", "#bbcecf"]
    color_cs = ["#107b66", "#16a085", "#18b092", "#1ac2a1", "#1cd6b1", "#1eecc3", "#25ffd4"]
    colors = [
        [
            RGB.from_hex(rc).mix(RGB.from_hex(cc)).to_hex()
            for cc in color_cs
        ]
        for rc in grey_cs
    ]
    print('colors:')
    for el in colors:
        print(el)

    for r in range(len(colors)):
        for c in range(len(colors[r])):
            plt.scatter(c + 1, r + 1, c=colors[r][c], s=800)

    plt.show()


def just():
    cg = RGB.from_hex('#8d8d8d')
    cc = RGB.from_hex('#16a085')
    print(cc.r - cg.r, cc.g - cg.g, cc.b - cg.b, )


if __name__ == "__main__":
    main()
    # just()
