from math import ceil, factorial, floor, frexp, sqrt


FACTORIAL_REPEAT_ITERS = 1000000
SQRT_REPEAT_ITERS = 2000000
FLOOR_CEIL_REPEAT_ITERS = 2000000
FREXP_REPEAT_ITERS = 2000000


def factorial_repeat(iters: int) -> float:
    acc = 0.0
    i = 0
    while i < iters:
        acc += float(factorial(10))
        i += 1
    return acc


def sqrt_repeat(iters: int) -> float:
    acc = 0.0
    i = 1
    while i <= iters:
        acc += sqrt(144.0)
        i += 1
    return acc


def floor_ceil_repeat(iters: int) -> float:
    acc = 0.0
    i = 1
    while i <= iters:
        acc += float(floor(10.02)) + float(ceil(-13.31))
        i += 1
    return acc


def frexp_repeat(iters: int) -> float:
    acc = 0.0
    i = 1
    while i <= iters:
        mantissa, exponent = frexp(19.74)
        acc += mantissa + float(exponent)
        i += 1
    return acc


def main() -> int:
    print(f"checksum_factorial_repeat={factorial_repeat(FACTORIAL_REPEAT_ITERS):.17e}")
    print(f"checksum_sqrt_repeat={sqrt_repeat(SQRT_REPEAT_ITERS):.17e}")
    print(f"checksum_floor_ceil_repeat={floor_ceil_repeat(FLOOR_CEIL_REPEAT_ITERS):.17e}")
    print(f"checksum_frexp_repeat={frexp_repeat(FREXP_REPEAT_ITERS):.17e}")
    return 0


main()
