def calculate_rpn(severity, occurrence, detection):
    values = (severity, occurrence, detection)
    if any(not isinstance(v, int) or not 1 <= v <= 10 for v in values):
        raise ValueError("Ratings must be integers from 1 to 10.")
    return severity * occurrence * detection


def test_rpn():
    assert calculate_rpn(7, 3, 5) == 105
    assert calculate_rpn(10, 10, 10) == 1000
    assert calculate_rpn(1, 1, 1) == 1


if __name__ == "__main__":
    test_rpn()
    print("Basic RPN tests passed.")
