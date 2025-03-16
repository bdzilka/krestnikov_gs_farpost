from collections.abc import Sequence


def check_fibonacci(data: Sequence[int]) -> bool:
    # минимальное для последовательности
    if len(data) < 2:
        return False

# проверка, что первые два числа это реально последовательность Фибоначчи
    if data[0] != 0 or data[1] != 1:
        return False

# проверка, что все последующие - сумма двух предыдущих
    for i in range(2, len(data)):
        if data[i] != data[i - 1] + data[i - 2]:
            return False

    return True


# пример
print(check_fibonacci([0, 1, 1]))
print(check_fibonacci([0, 1, 4]))
print(check_fibonacci([0, 1]))
print(check_fibonacci([1, 3]))
print(check_fibonacci([0, 1, 1, 2, 3, 10]))
