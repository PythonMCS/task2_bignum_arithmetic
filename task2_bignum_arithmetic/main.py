def normalize(sp):
    sp = sp.copy()

    while len(sp) > 1 and sp[-1] == 0:
        sp.pop()

    return sp

def compare_abs(a, b):
    a = normalize(a)
    b = normalize(b)

    if len(a) > len(b):
        return 1
    elif len(a) < len(b):
        return -1
    else:
        for i in range(len(a) -1, -1, -1):
            if a[i] == b[i]:
                continue
            elif a[i] > b[i]:
                return 1
            elif a[i] < b[i]:
                return -1
        return 0
def add_abs(a, b, M):
    new_sp = []
    carry = 0
    max_len = max(len(a), len(b))

    for i in range(max_len):
        dig_a = a[i] if i < len(a) else 0
        dig_b = b[i] if i < len(b) else 0
        cur_sum = dig_a + dig_b + carry
        new_sp.append(cur_sum % M)
        carry = cur_sum // M
    if carry != 0:
        new_sp.append(carry)
    return new_sp

def sub_abs(a, b, M):
    new_sp = []
    anti_carry = 0
    for i in range(len(a)):
        dig_a = a[i]
        dig_b = b[i] if i < len(b) else 0
        cur_sub = dig_a - dig_b - anti_carry
        if cur_sub < 0:
            cur_sub += M
            anti_carry = 1
        else:
            anti_carry = 0
        new_sp.append(cur_sub)
    return normalize(new_sp)

def add(a, sign_a, b, sign_b, M):
    if sign_a == sign_b:
        new_sp = add_abs(a, b, M)
        return new_sp, sign_a

    comp = compare_abs(a, b)

    if comp == 0:
        return [0], 1
    elif comp > 0:
        new_sp = sub_abs(a, b, M)
        return new_sp, sign_a
    else:
        new_sp = sub_abs(b, a, M)
        return new_sp, sign_b

def sub(a, sign_a, b, sign_b, M):
    return add(a, sign_a, b, -sign_b, M)


def mul_abs(a, b, M):
    new_sp = [0] * (len(a) + len(b) + 1)
    for i in range(len(a)):
        carry = 0
        for j in range(len(b)):
            pos = i + j
            curr = new_sp[pos] + a[i] * b[j] + carry
            new_sp[pos] = curr % M
            carry = curr // M
        pos = i + len(b)
        while carry > 0:
            curr = new_sp[pos] + carry
            new_sp[pos] = curr % M
            carry = curr // M
            pos += 1
    return normalize(new_sp)

def mul(a, sign_a, b, sign_b, M):
    result = mul_abs(a, b, M)
    if result == [0]:
        return [0], 1
    sign_result = sign_a * sign_b
    return result, sign_result


def div_abs(a, b, M):
    a = normalize(a)
    b = normalize(b)
    if b == [0]:
        raise ZeroDivisionError("Деление на ноль")

    if compare_abs(a, b) < 0:
        return [0], a
    rem = [0]
    new_sp = []
    for i in range(len(a) - 1, -1, -1):
        rem = normalize([a[i]] + rem)
        left = 0
        right = M - 1
        digit = 0
        while left <= right:
            middle = (left + right) // 2
            prod = mul_abs(b, [middle], M)
            if compare_abs(prod, rem) <= 0:
                digit = middle
                left = middle + 1
            else:
                right = middle - 1

        new_sp.append(digit)
        if digit != 0:
            prod = mul_abs(b, [digit], M)
            rem = sub_abs(rem, prod, M)
    quot = list(reversed(new_sp))
    return normalize(quot), normalize(rem)


def div_big(a, sign_a, b, sign_b, M):
    quot, rem = div_abs(a, b, M)
    if sign_a == sign_b:
        return quot, 1
    if rem == [0]:
        if quot == [0]:
            return [0], 1
        return quot, -1
    quot = add_abs(quot, [1], M)
    return quot, -1

def from_string(s, M):
    s = s.strip()
    if not s:
        raise ValueError("Пустая строка")
    sign = 1
    if s[0] in "+-":
        if s[0] == "-":
            sign = -1
        s = s[1:]
    if not s:
        raise ValueError("Нет разрядов")

    parts = s.split(":")
    parts = list(reversed(parts))

    digits = []
    for part in parts:
        if not part or not part.isdigit():
            raise ValueError(f"Некорректный разряд: {part}")
        digit = int(part)
        if digit >= M:
            raise ValueError(f"Каждый разряд должен быть < {M}")
        digits.append(digit) 

    digits = normalize(digits)
    if digits == [0]:
        sign = 1
    return digits, sign

def to_string(a, sign):
    a = normalize(a)
    if a == [0]:
        return "0"
    order = list(reversed(a))
    order_list = (str(s) for s in order)
    result = ":".join(order_list)
    if sign < 0:
        result = "-" + result
    return result



def check_capacity(a, N):
    a = normalize(a)
    if len(a) > N:
        raise OverflowError(
            f"Число превышает максимально допустимые {N} разрядов"
        )
    return a

def main():
    print("Длинная арифметика")
    while True:
        try:
            M = int(input("Введите основание системы счисления M (>= 2): "))
            N = int(input("Введите максимальное количество разрядов N (>= 1): "))
            if M < 2 or N < 1:
                print("M должно быть >= 2, а N >= 1")
                continue
            break
        except ValueError:
            print("Введите целые числа.")
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
            first = input(f"Введите первое число (разряды через ':', каждый < {M}): ")
            second = input(f"Введите второе число (разряды через ':', каждый < {M}): ")

            a, sign_a = from_string(first, M)
            b, sign_b = from_string(second, M)
            check_capacity(a, N)
            check_capacity(b, N)
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