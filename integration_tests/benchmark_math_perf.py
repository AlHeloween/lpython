from math import ceil, factorial, floor, frexp, sqrt
from lpython import i16, i32, f64


FACTORIAL_REPEAT_ITERS: i32 = 1000000
SQRT_REPEAT_ITERS: i32 = 2000000
FLOOR_CEIL_REPEAT_ITERS: i32 = 2000000
FREXP_REPEAT_ITERS: i32 = 2000000


def factorial_repeat(iters: i32) -> f64:
    acc: f64 = 0.0
    i: i32 = 0
    while i < iters:
        acc += f64(factorial(i32(10)))
        i += 1
    return acc


def sqrt_repeat(iters: i32) -> f64:
    acc: f64 = 0.0
    i: i32 = 1
    while i <= iters:
        acc += sqrt(144.0)
        i += 1
    return acc


def floor_ceil_repeat(iters: i32) -> f64:
    acc: f64 = 0.0
    i: i32 = 1
    while i <= iters:
        acc += f64(floor(10.02)) + f64(ceil(-13.31))
        i += 1
    return acc


def frexp_repeat(iters: i32) -> f64:
    acc: f64 = 0.0
    i: i32 = 1
    mantissa: f64
    exponent: i16
    while i <= iters:
        mantissa, exponent = frexp(19.74)
        acc += mantissa + f64(exponent)
        i += 1
    return acc


def main() -> i32:
    print("checksum_factorial_repeat=", factorial_repeat(FACTORIAL_REPEAT_ITERS))
    print("checksum_sqrt_repeat=", sqrt_repeat(SQRT_REPEAT_ITERS))
    print("checksum_floor_ceil_repeat=", floor_ceil_repeat(FLOOR_CEIL_REPEAT_ITERS))
    print("checksum_frexp_repeat=", frexp_repeat(FREXP_REPEAT_ITERS))
    return 0


main()
