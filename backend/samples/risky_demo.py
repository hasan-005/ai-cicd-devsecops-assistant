# INTENTIONALLY BAD CODE FOR CI/CD DEMO ONLY
# Do not use in production.

FAKE_API_KEY = "ghp_FAKE1234567890123456789012345678901234"


def risky_function(n):
    data = []

    # High time complexity: O(n^3)
    for i in range(n):
        for j in range(n):
            for k in range(n):
                data.append(i + j + k)

    # Memory usage grows with n
    huge_list = [x for x in range(n * 1000)]

    return len(data) + len(huge_list)


def divide_numbers(a, b):
    # Intentionally unsafe for testing
    return a / b


if __name__ == "__main__":
    print(risky_function(20))