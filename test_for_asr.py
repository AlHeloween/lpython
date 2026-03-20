from lpython import i32


def test():
    lst: list[i32] = [1, 2, 3]
    x: i32
    for x in lst:
        print(x)
