# """
# Создать класс Angle для хранения углов
#  - хранить внутреннее состояние угла в радианах
#  - возможность создания угла в радианах и градусах
#  - реализовать присваивание и получение угла в радианах и градусах
#  - реализовать сравнение углов с учетом, что 2 Pi*N + x = x, где Pi=3.14.1529..., N-целое
#  - реализовать преобразование угла в строку, float, int, str
#  - реализовать сравнение углов
#  - реализовать сложение (в том числе с float и int, считая, что они заданы в радианах), вычитание (считая, что они заданы в радианах), умножение и деление на число
#  - реализовать строковое представление объекта (str, repr)

# Создать класс AngleRange для хранения промежутка для углов
#  - Реализовать механизм создания объекта через задание начальной и конечной точки промежутка в виде углов float, int или Angle
#  - Предусмотреть возможность использования включающих и исключающих промежутков
#  - реализовать возможность сравнения объектов на эквивалентность (eq)
#  - реализовать строковое представление объекта (str, repr)
#  - реализовать получение длины промежутка (abs или отдельны метод)
#  - реализовать сравнение промежутков
#  - реализовать операцию in для проверки входит один промежуток в другой или угол в промежуток
#  - реализовать операции сложения, вычитания (результат в общем виде - список промежутков)
# """


from math import pi, isclose
from operator import truediv
from typing import Self
# from typing import TypeVar, Type

# T = TypeVar("T", bound="ClassName")

class Angle:
    def __init__(self, angle: float) -> None:
        self.angle = angle
    
    @classmethod
    def from_degree(cls, degree: float) -> Self:
        return cls(degree * (pi / 180))
    
    @property
    def degree(self) -> float:
        return self.angle * (180 / pi)
    
    @degree.setter
    def degree(self, angle: float) -> None:
        self.angle = angle * (pi / 180)

    @property
    def radian(self) -> float:
        return self.angle
    
    @radian.setter
    def radian(self, angle: float) -> None:
        self.angle = angle

    
    def __int__(self) -> int:
        return int(self.angle)
    
    def __float__(self) -> float:
        return float(self.angle)
    
    def __str__(self) -> str:
        return str(self.angle)
    
    def __repr__(self) -> str:
        return f"Angle({self.angle})"
    

    # Перегрузка операторов сравнения
    def __eq__(self, other: Self) -> bool:
        return isclose((self.angle % (2*pi)), (other.angle % (2*pi)))
    
    def __ne__(self, other: Self) -> bool:
        return not self.__eq__(other)
    
    def __lt__(self, other: Self) -> bool:
        return (self.angle % (2*pi)) < (other.angle % (2*pi))
    
    def __le__(self, other: Self) -> bool:
        return self.__lt__(other) or self.__eq__(other)
    
    def __gt__(self, other: Self) -> bool:
        return (self.angle % (2*pi)) > (other.angle % (2*pi))
    
    def __ge__(self, other: Self) -> bool:
        return self.__gt__(other) or self.__eq__(other) 
    
    # Прегрузка математических операторов
    def __add__(self, other: Self | float | int) -> Self:
        if isinstance(other, Angle):
            return Angle(self.angle + other.angle)
        elif isinstance(other, (int, float)):
            return Angle(self.angle + other)
        else:
            return NotImplemented
    
    def __radd__(self, other: int | float) -> Self:
        return self.__add__(other)

    def __sub__(self, other: Self | float | int) -> Self:
        if isinstance(other, Angle):
            return Angle(self.angle - other.angle)
        elif isinstance(other, (int, float)):
            return Angle(self.angle - other)
        else:
            return NotImplemented
    
    def __rsub__(self, other: int | float) -> Self:
        return Angle(other - self.angle)
    
    def __mul__(self, other: int | float) -> Self:
        if isinstance(other, (int, float)):
            return Angle(self.angle * other)
        else:
            return NotImplemented
    
    def __rmul__(self, other: int | float) -> Self:
        return self.__mul__(other)

    def __truediv__(self, other: int | float) -> Self:
        if isinstance(other, (int, float)):
            return Angle(self.angle / other)
        else:
            return NotImplemented
        
    def __rtruediv__(self, other: int | float) -> Self:
        if isinstance(other, (int, float)):
            return Angle(other / self.angle)
        else:
            return NotImplemented


class AngleRange():
    def __init__(self, start_point: int | float, end_point: int | float, include_start: bool = True, include_end: bool = True) -> None:
        self.start_point    = start_point
        self.end_point      = end_point
        self.include_start  = include_start
        self.include_end    = include_end

    @classmethod
    def from_angle(cls, range: Angle) -> Self:
        return cls(0, range.angle)
    
    def __abs__(self) -> float:
        if self.start_point <= self.end_point:
            return self.end_point - self.start_point
        else:
            return 2*pi - (self.start_point - self.end_point)

    def cut_range(self):
        if (self.end_point - self.start_point) % (2*pi) == 0 and (self.start_point != self.end_point):
            start = self.start_point % (2*pi)
            end = self.end_point % (2*pi) + (2*pi)
        else:
            start = self.start_point % (2*pi)
            end = self.end_point % (2*pi)
        return start, end
        
    def __eq__(self, other: Self) -> bool:
        s_start, s_end = self.cut_range()
        o_start, o_end = other.cut_range()
        return (s_start == o_start) and \
            (s_end == o_end) and \
            (self.__abs__() == other.__abs__())
    
    def __ne__(self, other: Self) -> bool:
        return not self.__eq__(other)
    
    def __lt__(self, other: Self) -> bool:
        return self.__abs__() < other.__abs__()
    
    def __le__(self, other: Self) -> bool:
        return self.__lt__(other) or self.__eq__(other)
    
    def __gt__(self, other: Self) -> bool:
        return self.__abs__() > other.__abs__()
    
    def __ge__(self, other: Self) -> bool:
        return self.__gt__(other) or self.__eq__(other)
    
    def __repr__(self) -> str:
        open_bracket = "[" if self.include_start else "("
        close_bracket = "]" if self.include_end else ")"
        return f"AngleRange({open_bracket}{self.start_point}, {self.end_point}{close_bracket})"
    
    def __str__(self):
        return self.__repr__()
    
        
    # Вспомогательный метод
    def split_range(self):
        if (self.end_point - self.start_point) % (2*pi) == 0 and (self.start_point != self.end_point):
            start = self.start_point % (2*pi)
            end = self.end_point % (2*pi) + (2*pi)
        else:
            start = self.start_point % (2*pi)
            end = self.end_point % (2*pi)

        if start <= end:
            return [((start, self.include_start), (end, self.include_end))]
        
        return [((start, self.include_start), (2*pi, True)),
                ((0, True), (end, self.include_end))]
    
    # Проверка in
    def __contains__(self, other: Self | Angle) -> bool:
        if isinstance(other, type(self)):
            if other > self:
                return False
        

            def segment_contains(segA, segB):
                (a1, a1_include), (a2, a2_include) = segA
                (b1, b1_include), (b2, b2_include) = segB

                start_points_check  = (a1 < b1) or ((a1 == b1) and (a1_include or not b1_include))
                end_points_check    = (a2 > b2) or ((a2 == b2) and (a2_include or not b2_include))

                return start_points_check and end_points_check
            
            # s1, e1, = self.start_point % (2*pi), self.end_point % (2*pi)
            self_parts = self.split_range()

            # s2, e2, = other.start_point % (2*pi), other.end_point % (2*pi)
            other_parts = other.split_range()

            return all(
                any(segment_contains(seg_self, seg_other) for seg_self in self_parts) \
                for seg_other in other_parts
            )


        else:
            return self.__contains__(Self.from_angle(other))


    def __add__(self, other: Self) -> list[Self]:
        parts = self.split_range() + other.split_range()

        flat = []
        for (s, s_inc), (e, e_inc) in parts:
            flat.append((s, s_inc, e, e_inc))

        flat.sort(key=lambda x: x[0])

        merged = []
        cs, cs_inc, ce, ce_inc = flat[0]

        for s, s_inc, e, e_inc in flat[1:]:
            if s < ce or (s == ce and (s_inc or ce_inc)):
                if e > ce:
                    ce = e
                    ce_inc = e_inc
                elif e == ce:
                    ce_inc = ce_inc or e_inc
            else:
                merged.append((cs, cs_inc, ce, ce_inc))
                cs, cs_inc, ce, ce_inc = s, s_inc, e, e_inc

        merged.append((cs, cs_inc, ce, ce_inc))

        # Анализ результата
        if len(merged) == 1:
            s, s_inc, e, e_inc = merged[0]
            return AngleRange(s, e, s_inc, e_inc)
        elif len(merged) == 2:
            # r1, r2 = merged
            s1, s1_inc, e1, e1_inc = merged[0]
            s2, s2_inc, e2, e2_inc = merged[1]
            if e1 == 2*pi and s2 == 0:
                return AngleRange(s1, e2, s1_inc, e2_inc)
            elif e2 == 2*pi and s1 == 0:
                return AngleRange(s2, e1, s2_inc, e1_inc)
        
        return [
            AngleRange(s, e, s_inc, e_inc) for (s, s_inc, e, e_inc) in merged
        ]
            
    def subtract_segment(self, segA, segB):
        (a1, a1_inc), (a2, a2_inc) = segA
        (b1, b1_inc), (b2, b2_inc) = segB

        result = []

        # Пересечения нет
        if b2 < a1 or b1 > a2 or (b2 == a1 and not (b2_inc and a1_inc)) or (b1 == a2 and not (b1_inc and a2_inc)):
            return [segA]
        
        # Пересечение в одной точке
        if (b1 == a2 and (b1_inc and a2_inc)):
            return [((a1, a1_inc), (a2, False))]
        elif (b2 == a1 and (b2_inc and a1_inc)):
            return  [((a1, False), (a2, a2_inc))]
        
        # Полное пересечение
        full_left = (b1 < a1) or (b1 == a1 and b1_inc >= a1_inc)
        full_right = (b2 > a2) or (b2 == a2 and b2_inc >= a2_inc)

        if full_left and full_right:
            endpoints = []

            if (b1 == a1) and (a1_inc > b1_inc):
                endpoints.append(((a1, True), (a1, True)))

            if (b2 == a2) and (a2_inc > b2_inc):
                endpoints.append(((a2, True), (a2, True)))

            return endpoints
        
        # Частичное перекрытие справа
        # --- 2. Частичное пересечение слева ---
        if b1 <= a1 and b2 < a2:
            if (b1 == a1) and (a1_inc > b1_inc):
                result.append(((a1, True), (a1, True)))
            new_start = (b2, not b2_inc)
            new_end   = (a2, a2_inc)
            result.append((new_start, new_end))
            return result

        # --- 3. Частичное пересечение справа ---
        if b1 > a1 and b2 >= a2:
            new_start = (a1, a1_inc)
            new_end   = (b1, not b1_inc)
            result.append((new_start, new_end))
            if (b2 == a2) and (a2_inc > b2_inc):
                result.append(((a2, True), (a2, True)))
            return result

        # --- 4. B внутри A — разрезаем на два ---
        if a1 < b1 < a2 and a1 < b2 < a2:
            left  = ((a1, a1_inc), (b1, not b1_inc))
            right = ((b2, not b2_inc), (a2, a2_inc))
            return [left, right]

        # --- 5. Граничные случаи (равные значения с разной включённостью) ---
        # left boundary only
        if b1 == a1 and not b1_inc and a1_inc:
            return [((a1, a1_inc), (a1, a1_inc)),  # left point survives
                    ((b2, not b2_inc), (a2, a2_inc))]

        # right boundary only
        if b2 == a2 and not b2_inc and a2_inc:
            return [((a1, a1_inc), (b1, not b1_inc)),\
                    ((a2, a2_inc), (a2, a2_inc))]

        return result

            

    def __sub__(self, other: Self) -> Self:
        self_segs  = self.split_range()
        other_segs = other.split_range()

        res_segs = []

        for self_seg in self_segs:
            temp = [self_seg]
            for other_seg in other_segs:
                new_temp = []
                for t in temp:
                    new_temp += self.subtract_segment(t, other_seg)
                temp = new_temp
            res_segs += temp
        
        final_ranges = [
            AngleRange(s[0][0], s[1][0], s[0][1], s[1][1])
            for s in res_segs
        ]

        if len(final_ranges) == 1:
            return final_ranges[0]
        return final_ranges








def test_add():
    def print_result(res):
        if isinstance(res, list):
            print([str(r) for r in res])
        else:
            print(res)

    # --- 1. Простое объединение нециклических диапазонов ---
    a1 = AngleRange(0, pi/2)
    a2 = AngleRange(pi/3, pi)
    res = a1 + a2
    print("Test 1:", end=" ")
    print_result(res)  # ожидание: [0, pi]

    # --- 2. Объединение двух смежных диапазонов ---
    b1 = AngleRange(0, pi)
    b2 = AngleRange(pi, 3*pi/2)
    res = b1 + b2
    print("Test 2:", end=" ")
    print_result(res)  # ожидание: [0, 3*pi/2]

    # --- 3. Объединение с циклическим диапазоном ---
    c1 = AngleRange(5*pi/3, pi/3)  # циклический: [300°, 60°]
    c2 = AngleRange(0, pi/2)       # [0°, 90°]
    res = c1 + c2
    print("Test 3:", end=" ")
    print_result(res)  # ожидание: [5*pi/3, pi/2] → полный циклический диапазон

    # --- 4. Разорванные диапазоны не объединяются в один ---
    d1 = AngleRange(pi, 3*pi/2)
    d2 = AngleRange(0, pi/4)
    res = d1 + d2
    print("Test 4:", end=" ")
    print_result(res)  # ожидание: список из двух AngleRange

    # --- 5. Полный круг ---
    e1 = AngleRange(0, 2*pi)
    e2 = AngleRange(pi/2, pi)
    res = e1 + e2
    print("Test 5:", end=" ")
    print_result(res)  # ожидание: [0, 2*pi]

def test_sub():
    print("\n=== TEST 1: No overlap ===")
    a = AngleRange(0, pi)
    b = AngleRange(pi, 2*pi)
    print("a - b =", a - b)


    print("\n=== TEST 2: Full cover ===")
    a = AngleRange(0, pi, True, True)
    b = AngleRange(0, pi, True, True)
    print("a - b =", a - b)   # ожидаем []


    print("\n=== TEST 3: Full cover but endpoints remain ===")
    a = AngleRange(0, pi, True, True)      # [0, π]
    b = AngleRange(0, pi, False, False)    # (0, π)
    res = a - b
    print("a - b =", res)                   # ожидаем 0 и π в виде точек
    if isinstance(res, list):
        for r in res:
            print("  part:", r)


    print("\n=== TEST 4: Partial left overlap ===")
    a = AngleRange(0, pi)
    b = AngleRange(0, pi/2)
    print("a - b =", a - b)


    print("\n=== TEST 5: Partial right overlap ===")
    a = AngleRange(0, pi)
    b = AngleRange(pi/2, pi)
    print("a - b =", a - b)


    print("\n=== TEST 6: Middle cut (split in two) ===")
    a = AngleRange(0, pi)
    b = AngleRange(pi/3, 2*pi/3)
    res = a - b
    print("a - b =", res)
    if isinstance(res, list):
        for r in res:
            print("  part:", r)


    print("\n=== TEST 7: Same left boundary, different inclusion ===")
    a = AngleRange(0, pi, True, True)
    b = AngleRange(0, pi/2, False, True)  # (0, π/2]
    print("a - b =", a - b)
    if isinstance(res, list):
        for r in res:
            print("  part:", r)

    print("\n=== TEST 8: Same right boundary, different inclusion ===")
    a = AngleRange(0, pi, True, True)
    b = AngleRange(pi/2, pi, True, False)  # [π/2, π)
    print("a - b =", a - b)
    if isinstance(res, list):
        for r in res:
            print("  part:", r)

    print("\n=== TEST 9: Subtract point ===")
    a = AngleRange(0, pi)
    b = AngleRange(pi/2, pi/2)     # точка
    res = a - b
    print("a - b =", res)
    if isinstance(res, list):
        for r in res:
            print("  part:", r)


    print("\n=== TEST 10: Other cyclic, fully covering ===")
    a = AngleRange(pi/2, 3*pi/2)
    b = AngleRange(3*pi/2, pi/2) 
    print("a - b =", a - b)


    print("\n=== TEST 11: Self cyclic, partial subtraction ===")
    a = AngleRange(3*pi/2, pi/2)   # циклический
    b = AngleRange(0, pi/4)
    res = a - b
    print("a - b =", res)
    if isinstance(res, list):
        for r in res:
            print("  part:", r)


    print("\n=== TEST 12: Both cyclic ===")
    a = AngleRange(3*pi/2, pi/2)   # циклический
    b = AngleRange(pi, 0)          # циклический
    res = a - b
    print("a - b =", res)
    if isinstance(res, list):
        for r in res:
            print("  part:", r)

# Запуск тестов
test_add()
test_sub()
print("=" * 10)
a1 = AngleRange(pi/4, pi/2)
a2 = AngleRange(3*pi/2, pi/2)
a3 = AngleRange(pi/6, 5*pi/6)
b = AngleRange(0, pi)
print(a1 in b)
print(a2 in b)
print(a3 in b)
e1 = AngleRange(pi/2, pi)
e2 = AngleRange(5*pi/2, 3*pi)
print(e1 == e2)
print("=" * 10)
c1 = Angle.from_degree(180)
c1 = AngleRange.from_angle(c1)
c2 = Angle.from_degree(270)
c2 = AngleRange.from_angle(c2)
q = AngleRange(3*pi/2, 5*pi/4)
print(c1 in q)
print(c2 in q)
print("="*10)

ang1 = Angle(pi/2)
ang2 = Angle(pi/2)
ang3 = Angle(pi)
print(ang1 + ang2)
print(ang1 + pi)
print(ang1 * 2)
print(ang3 - ang2)
print(ang3 > ang1)
print(ang1 == ang2)
print("="*10)
print(float(ang1))
print(int(ang1))
print(str(ang1))
