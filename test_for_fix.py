from lpython import i32


def test_list_iter():
    lst: list[i32] = [1, 2, 3, 4, 5]
    total: i32 = 0
    for x in lst:
        total += x
    assert total == 15
    print("list iteration ok")


def test_string_iter():
    s: str = "hello"
    chars: list[str] = []
    for ch in s:
        chars.append(ch)
    assert chars == ["h", "e", "l", "l", "o"]
    print("string iteration ok")


def test_range_iter():
    sum1: i32 = 0
    for i in range(5):
        sum1 += i
    assert sum1 == 10
    print("range iteration ok")


def test_nested():
    mat: list[list[i32]] = [[1, 2], [3, 4]]
    total: i32 = 0
    for row in mat:
        for elem in row:
            total += elem
    assert total == 10
    print("nested iteration ok")


def test_empty():
    lst2: list[i32] = []
    count: i32 = 0
    for _ in lst2:
        count += 1
    assert count == 0
    print("empty iteration ok")


def test_single():
    lst3: list[i32] = [42]
    val: i32 = 0
    for x in lst3:
        val = x
    assert val == 42
    print("single iteration ok")


def test_step_range():
    sum2: i32 = 0
    for i in range(0, 10, 2):
        sum2 += i
    assert sum2 == 20
    print("step range ok")


def test_negative_step():
    sum3: i32 = 0
    for i in range(10, 0, -2):
        sum3 += i
    assert sum3 == 30
    print("negative step range ok")


def test_while_loop():
    i: i32 = 0
    total: i32 = 0
    while i < 5:
        total += i
        i += 1
    assert total == 10
    print("while loop ok")


# Main
test_list_iter()
test_string_iter()
test_range_iter()
test_nested()
test_empty()
test_single()
test_step_range()
test_negative_step()
test_while_loop()
print("All tests passed")
