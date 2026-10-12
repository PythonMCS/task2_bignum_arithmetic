from collections.abc import Callable


def normalize(digits: list[int]) -> list[int]:
    digits = digits.copy()

    while len(digits) > 1 and digits[-1] == 0:
        digits.pop()

    return digits


def compare_abs(num1: list[int], num2: list[int]):
    num1 = normalize(num1)
    num2 = normalize(num2)

    if len(num1) > len(num2):
        return 1
    if len(num1) < len(num2):
        return -1

    for i in range(len(num1) -1, -1, -1):
        if num1[i] == num2[i]:
            continue
        if num1[i] > num2[i]:
            return 1
        if num1[i] < num2[i]:
            return -1
    return 0

    
def add_abs(num1: list[int], num2: list[int], base: int) -> list[int]:
    new_num = []
    carry = 0
    max_len = max(len(num1), len(num2))

    for i in range(max_len):
        dig_a = num1[i] if i < len(num1) else 0
        dig_b = num2[i] if i < len(num2) else 0
        cur_sum = dig_a + dig_b + carry
        new_num.append(cur_sum % base)
        carry = cur_sum // base
    if carry != 0:
        new_num.append(carry)
    return new_num


def sub_abs(num1: list[int], num2: list[int], base: int) -> list[int]:
    new_num = []
    anti_carry = 0
    for i in range(len(num1)):
        dig_a = num1[i]
        dig_b = num2[i] if i < len(num2) else 0
        cur_sub = dig_a - dig_b - anti_carry
        if cur_sub < 0:
            cur_sub += base
            anti_carry = 1
        else:
            anti_carry = 0
        new_num.append(cur_sub)
    return normalize(new_num)


def add(num1: list[int], sign1: int, num2: list[int], sign2: int, base: int) -> tuple[list[int], int]:
    if sign1 == sign2:
        new_num = add_abs(num1, num2, base)
        return new_num, sign1

    comp = compare_abs(num1, num2)

    if comp == 0:
        return [0], 1
    elif comp > 0:
        new_num = sub_abs(num1, num2, base)
        return new_num, sign1
    else:
        new_num = sub_abs(num2, num1, base)
        return new_num, sign2


def sub(num1: list[int], sign1: int, num2: list[int], sign2: int, base: int) -> tuple[list[int], int]:
    return add(num1, sign1, num2, -sign2, base)


def mul_abs(num1: list[int], num2: list[int], base: int) -> list[int]:
    new_num = [0] * (len(num1) + len(num2) + 1)
    for i in range(len(num1)):
        carry = 0
        for j in range(len(num2)):
            pos = i + j
            curr = new_num[pos] + num1[i] * num2[j] + carry
            new_num[pos] = curr % base
            carry = curr // base
        pos = i + len(num2)
        while carry > 0:
            curr = new_num[pos] + carry
            new_num[pos] = curr % base
            carry = curr // base
            pos += 1
    return normalize(new_num)


def mul(num1: list[int], sign1: int, num2: list[int], sign2: int, base: int) -> tuple[list[int], int]:
    result = mul_abs(num1, num2, base)
    if result == [0]:
        return [0], 1
    sign_result = sign1 * sign2
    return result, sign_result


def div_abs(num1: list[int], num2: list[int], base: int) -> tuple[list[int], list[int]]:
    num1 = normalize(num1)
    num2 = normalize(num2)
    if num2 == [0]:
        raise ZeroDivisionError("Деление на ноль")

    if compare_abs(num1, num2) < 0:
        return [0], num1
    rem = [0]
    new_num = []
    for i in range(len(num1) - 1, -1, -1):
        rem = normalize([num1[i]] + rem)
        left = 0
        right = base - 1
        digit = 0
        while left <= right:
            middle = (left + right) // 2
            prod = mul_abs(num2, [middle], base)
            if compare_abs(prod, rem) <= 0:
                digit = middle
                left = middle + 1
            else:
                right = middle - 1

        new_num.append(digit)
        if digit != 0:
            prod = mul_abs(num2, [digit], base)
            rem = sub_abs(rem, prod, base)
    quot = list(reversed(new_num))
    return normalize(quot), normalize(rem)


def div_big(num1: list[int], sign1: int, num2: list[int], sign2: int, base: int) -> tuple[list[int], int]:
    quot, rem = div_abs(num1, num2, base)
    if sign1 == sign2:
        return quot, 1
    if rem == [0]:
        if quot == [0]:
            return [0], 1
        return quot, -1
    quot = add_abs(quot, [1], base)
    return quot, -1


def from_string(raw_input: str, base: int) -> tuple[list[int], int]:
    raw_input = raw_input.strip()
    if not raw_input:
        raise ValueError("Пустая строка")
    sign = 1
    if raw_input[0] in "+-":
        if raw_input[0] == "-":
            sign = -1
        raw_input = raw_input[1:]
    if not raw_input:
        raise ValueError("Нет разрядов")

    parts = raw_input.split(":")
    parts = list(reversed(parts))

    digits = []
    for part in parts:
        if not part or not part.isdigit():
            raise ValueError(f"Некорректный разряд: {part}")
        digit = int(part)
        if digit >= base:
            raise ValueError(f"Каждый разряд должен быть < {base}")
        digits.append(digit) 

    digits = normalize(digits)
    if digits == [0]:
        sign = 1
    return digits, sign


def to_string(num: list[int], sign: int) -> str:
    num = normalize(num)
    if num == [0]:
        return "0"
    order = list(reversed(num))
    order_list = (str(s) for s in order)
    result = ":".join(order_list)
    if sign < 0:
        result = "-" + result
    return result


def check_capacity(num: list[int], max_digits: int) -> list[int]:
    num = normalize(num)
    if len(num) > max_digits:
        raise OverflowError(
            f"Число превышает максимально допустимые {max_digits} разрядов"
        )
    return num


def input_integer(predicate: Callable[[int], bool], prompt_msg: str, warning_msg: str) -> int:
    while True:
        try:
            num = int(input(prompt_msg))
            if not predicate(num):
                print(warning_msg)
                continue
            return num
        except ValueError:
            print("Введите целое число.")


def input_operand(base: int, max_digits: int, prompt_msg: str) -> tuple[list[int], int]:
    raw_input = input(prompt_msg)
    num, sign = from_string(raw_input, base)
    check_capacity(num, max_digits)

    return num, sign


def main():
    print("Длинная арифметика")
    M = input_integer(lambda x: x >= 2, "Введите основание системы счисления M (>= 2): ", "M должно быть >= 2")
    N = input_integer(lambda x: x >= 1, "Введите максимальное количество разрядов N (>= 1): ", "N должно быть >= 1")
    
    while True:
        print()
        print("Выберите операцию:")
        print("1 - сложение")
        print("2 - вычитание")
        print("3 - умножение")
        print("4 - целочисленное деление")
        print("0 - выход")
        operation = input("> ").strip()
        if operation == "0":
            print("Выход.")
            break
        if operation not in ("1", "2", "3", "4"):
            print("Неизвестная операция.")
            continue
        try:
            a, sign_a = input_operand(M, N, f"Введите первое число (разряды через ':', каждый < {M}): ")
            b, sign_b = input_operand(M, N, f"Введите второе число (разряды через ':', каждый < {M}): ")

            if operation == "1":
                result, sign_result = add(a, sign_a, b, sign_b, M)
            elif operation == "2":
                result, sign_result = sub(a, sign_a, b, sign_b, M)
            elif operation == "3":
                result, sign_result = mul(a, sign_a, b, sign_b, M)
            else:
                result, sign_result = div_big(a, sign_a, b, sign_b, M)
            result = check_capacity(result, N)
            print(f"Результат: {to_string(result, sign_result)}")
        except ValueError as error:
            print("Ошибка:", error)
        except ZeroDivisionError as error:
            print("Ошибка:", error)
        except OverflowError as error:
            print("Переполнение:", error)


if __name__ == "__main__":
    main()