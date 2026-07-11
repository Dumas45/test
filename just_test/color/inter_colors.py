import matplotlib.pyplot as plt


def minmax(v):
    return max(0, min(255, v))


class RGB:
    def __init__(self, r: int, g: int, b: int):
        self.r = r
        self.g = g
        self.b = b
        if not (0 <= r <= 255):
            raise ValueError('Red in incorrect range')
        if not (0 <= g <= 255):
            raise ValueError('Green in incorrect range')
        if not (0 <= b <= 255):
            raise ValueError('Blue in incorrect range')

    def to_hex(self) -> str:
        return '#%02x%02x%02x' % (self.r, self.g, self.b)

    def __str__(self):
        return f'RGB: {self.to_hex()}'

    @classmethod
    def from_hex(cls, h):
        return cls(int(h[1:3], 16), int(h[3:5], 16), int(h[5:7], 16))

    def mix(self, other: 'RGB') -> 'RGB':
        b = 1
        d = b + 1
        return RGB((b * self.r + other.r) // d, (b * self.g + other.g) // d, (b * self.b + other.b) // d)

    def shift(self, r: int, g: int, b: int) -> 'RGB':
        return RGB(
            minmax(self.r + r),
            minmax(self.g + g),
            minmax(self.b + b)
        )

    def interpolate(self, color: 'RGB', factor: float) -> 'RGB':
        return RGB(
            minmax(self.r + round(factor * (color.r - self.r))),
            minmax(self.g + round(factor * (color.g - self.g))),
            minmax(self.b + round(factor * (color.b - self.b))),
        )


def main():
    light_color = RGB.from_hex('#eeeeee')
    grey_color = RGB.from_hex('#7f8c8d')
    # sentiment_color = RGB.from_hex('#128770')
    sentiment_color = RGB.from_hex('#c0392b')
    factors = [0, 0.05, 0.1, 0.15, 0.2, 0.25, 0.3, 0.35, 0.4, 0.45, 0.5, 0.55, 0.6, 0.65, 0.7, 0.75, 0.8, 0.85, 0.9, 0.95, 1.0]

    colors = [
        [
            grey_color.interpolate(light_color, grey_factor).interpolate(
                sentiment_color.interpolate(light_color, sentiment_factor),
                0.6
            ).to_hex()
            for sentiment_factor in reversed(factors)
        ]
        for grey_factor in factors
    ]
    print('colors:')
    for el in colors:
        print(el)

    for r in range(len(colors)):
        for c in range(len(colors[r])):
            plt.scatter(c + 1, r + 1, c=colors[r][c], s=400)

    plt.show()


if __name__ == "__main__":
    main()
    # just()
