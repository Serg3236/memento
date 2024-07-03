from typing import Self
from datetime import date as datetime_Date
from re import split as rsplit

DataTuple = tuple[int, int, int]
FoundDateTuple = DataTuple | None

MONTHS_NAMES_ENG: list[str] = ["january", "february", "march", "april", "may",
                               "june", "july", "august", "september",
                               "october", "november", "december"]
MONTHS_NAMES_RUS: list[str] = ["январь", "февраль", "март", "апрель", "май",
                               "июнь", "июль", "август", "сентябрь", "октябрь",
                               "ноябрь", "декабрь"]
MONTHS_LNGTH: list[int] = [31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
TODAY: datetime_Date = datetime_Date.today()


class MyDateException(Exception):

    def __init__(self, id_: int, *args):
        self.id: int = id_
        
        if args:
            self.message = args[0]
        else:
            self.message = None

    def __str__(self) -> str:
        if self.message:
            return f"[id={self.id}] {self.message} "
        else:
            return f"[id={self.id}] No comments"

class Infinity:

    def __lt__(self, other) -> bool:
        return False

    def __gt__(self, other) -> bool:
        return True

class MyDate:
    
    def __init__(self, year: int, month: int, day: int):
        self.year: int = year
        self.month: int = month
        self.day: int = day

        self.is_completed: bool = not -1 in (year, month, day)
        if self.is_completed:
            self.date: datetime_Date = datetime_Date(year, month, day)
    
    def __lt__(self, other: Self) -> bool:
        if self.year < other.year: return True
        if self.year > other.year: return False

        if self.month < other.month: return True
        if self.month > other.month: return False

        if self.day < other.day: return True
        return False

    def __iter__(self):
        return (self.__dict__[item] for item in ('year', 'month', 'day'))
    
    def to_date(self) -> datetime_Date:
        return self.date if self.is_completed else False
    
    def to_str(self, size: list[int] = [2, 2, 4]) -> str:
        year = "*" * size[2] if self.year == -1 else str(self.year)
        month = "*" * size[1] if self.month == -1 else str(self.month)
        day = "*" * size[0] if self.day == -1 else str(self.day)

        return f"{day.zfill(size[0])}.{month.zfill(size[1])}.{year.zfill(size[2])}"
    
    def days_to(self) -> int:
        return (self.date - TODAY).days if self.is_completed else False
    
    def is_suit(self, mask: Self) -> bool:
        if mask.year != -1 and mask.year != self.year: return False
        if mask.month != -1 and mask.month != self.month: return False
        if mask.day != -1 and mask.day != self.day: return False
        return True

    def next_suit(self) -> Self | None:
        date: DataTuple = nearest_suit(*self)
        if date: return MyDate(*date)
        return None

    def prev_suit(self) -> Self | None:
        date = nearest_suit(*self, -1)
        if date: return MyDate(*date)
        return None

    def get_nearest(self) -> Self:
        n_date = self.next_suit()
        p_date = self.prev_suit()

        if not p_date: return n_date
        if not n_date: return p_date
        
        if n_date.days_to() <= -p_date.days_to(): return n_date
        return p_date

def is_leap_year(year: int) -> bool:
    return (year % 4 == 0 and year % 100 != 0) or year % 400 == 0

def get_days_count(month: int, year: int = -1) -> int:
    day_in_month = MONTHS_LNGTH[month - 1]
    
    if year != -1 and month == 2 and not is_leap_year(year):
        day_in_month -= 1

    return day_in_month

def pars_date(date: str) -> MyDate:
    date = rsplit("\.|-| |_", date)
    if not (1 < len(date) < 4 and all(map(lambda s: s.isdigit() or s in {"", "*"}, date))):
        raise MyDateException(1, "Неправельный формат даты.\nФормат: [D].[M][.[Y]]\nВ качестве разделителя можно использовать символы: .-_<пробел>.")
    
    if len(date) == 2: date.append('*')
    
    def str_to_int(x: str, y: int = 0) -> int:
        if x == "": return y
        elif x == "*": return -1
        else: return int(x)
    
    day = str_to_int(date[0], TODAY.day)
    month = str_to_int(date[1], TODAY.month)
    year = str_to_int(date[2], TODAY.year)
    
    if month != -1:
        if not 0 < int(month) < 13:
            raise MyDateException(2, f"Нет месяца с номером {month}")

        day_in_month = get_days_count(month, year)
    
        if day != -1 and (not 0 < day <= day_in_month):
            month_name = MONTHS_NAMES_RUS[month - 1]
            if month_name[-1] in ('й', 'ь'): month_name = month_name[:-1]
            month_name += 'е'
            raise MyDateException(3, f"В{f' {year}' if year != -1 else ''} году в {month_name} нет {day}-ого числа.")
    
    return MyDate(year, month, day)

def nearest_suit(year: int, month: int, day: int, direct: int = 1) -> FoundDateTuple:
    if (year, month, day) == (-1, 2, 29):
        if (is_leap_year(TODAY.year) and
            (0 < direct and TODAY.month <= 2) or
            (direct < 0 and TODAY.month >= 2)):
            year = TODAY.year
        else:
            year = TODAY.year - TODAY.year % 4
            if 0 < direct: year += 4
            if year % 100 == 0 and year % 400 != 0: year += 4 * direct
        return (year, month, day)
    
    elif year == -1:
        res = nearest_suit(TODAY.year, month, day, direct)
        
        if not res:
            res = nearest_suit(TODAY.year + direct, month, day, direct)
        
        return res
    
    elif month == -1:
        month = TODAY.month
        res = nearest_suit(year, month, day, direct)
        
        attempt = 0
        while not res and attempt < 2:
            attempt += 1
            month += direct
            if not 0 < month < 13: return -1
            res = nearest_suit(year, month, day, direct)
        
        return res
    
    elif day == -1:
        if (0 < direct and
            (year < TODAY.year or year == TODAY.year and month < TODAY.month) or
            direct < 0 and
            (TODAY.year < year or year == TODAY.year and TODAY.month < month)):
            return -1
        
        if year == TODAY.year and month == TODAY.month:
            day = TODAY.day
        else:
            day = 1 if 0 < direct else get_days_count(month, year)
        
        return (year, month, day)
    
    else:
        if direct * MyDate(year, month, day).days_to() >= 0:
            return (year, month, day)
        else:
            return None

def main():
    date1 = pars_date("29.*.*")
    date2 = pars_date("29.10.*")
    date3 = pars_date("29.08.2024")

    print(date1.to_str())
    print(date2.to_str())
    print(date3.to_str())

    print(date2.is_suit(date1))
    print(date3.is_suit(date2))

    print(date1.next_suit().to_str())
    print(date2.prev_suit().to_str())

    pars_date("")

if __name__ == "__main__":
    main()
