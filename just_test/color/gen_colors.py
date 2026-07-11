import matplotlib.pyplot as plt
import random


def main():
    number_of_rows = 5
    number_of_columns = 10

    colors = [
        [
            "#" + ''.join([random.choice('0123456789ABCDEF') for j in range(6)]).lower()
            for i in range(number_of_columns)
        ]
        for i in range(number_of_rows)
    ]
    print('colors:')
    for el in colors:
        print(el)

    for r in range(number_of_rows):
        for c in range(number_of_columns):
            plt.scatter(c + 1, r + 1, c=colors[r][c], s=800)

    plt.show()


if __name__ == "__main__":
    main()
