def nested_loop():
    total = 0

    for i in range(100):
        for j in range(100):
            total += i + j

    return total