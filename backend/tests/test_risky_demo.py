from samples.risky_demo import divide_numbers


def test_intentional_failure():
    result = divide_numbers(10, 2)

    # Intentionally wrong assertion
    # This should make CI fail.
    assert result == 999