def n_log_n_example(n):
    count = 0

    for i in range(n):
        x = n

        while x > 1:
            x //= 2
            count += 1

    return count