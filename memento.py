from sys import argv
from os.path import exists
from time import time

from my_date import *
from memento_ui import *

SEP = chr(17)
FILE = "C:\CmdPath\memento_v2\events.mem"
ENCODING = "UTF-8"
INF = Infinity()

def args_pars(args: list[str]) -> tuple[list[str], list[str]]:
    attributs = []
    args_ = []
    for i in range(len(args)):
        if args[i].startswith('-'): attributs.append(args[i])
        else: args_.append(args[i])

    return (args_, attributs)
    
def event_add(args: list[str], attr: list[str]) -> None:
    if len(args) not in {2, 3}:
        print("Невернй формат команды.\nФормат: <дата> <название> [<описание>] [<атрибуты>]")
        exit(2)

    if len(args) == 2: args.append('-')
    
    try:
        date = pars_date(args[0]).to_str([1, 1, 1])
    except MyDateException as exp:
        exp.id += 100
        print(f"MyDateException:", exp)
        exit(exp.id)
        
    name = args[1]
    description = args[2]
    pined = "1" if "-p" in attr else "0"
    
    with open(FILE, 'a', encoding=ENCODING) as file:
        file.write('\n' + SEP.join([date, name, description, pined]))

    print(f"Событие добавленно на дату {date}.")

def get_events() -> list[list]:
    #event format: [0] - id [1] - date [2] - name [3] - disc. [4] - attr
    
    with open(FILE, 'r', encoding=ENCODING) as file:
        readed_events = list(map(lambda l: list(l.rstrip().split(SEP)),
                                 file.readlines()))[1:]

    events = [None] * len(readed_events)
    for i in range(len(events)):
        events[i] = [i,
                     pars_date(readed_events[i][0]),
                     readed_events[i][1],
                     readed_events[i][2],
                     {"pin": readed_events[i][3] == '1'},]
    
    events.sort(key=lambda x: x[1])
    
    return events

def class_events(events: list[list]) -> tuple[list, list, list]:
    eventsLists = ([], [], []) # last, today, next
    
    events = get_events()
    for event in events:
        event[1] = event[1].get_nearest()
        if -7 <= event[1].days_to() < 0: eventsLists[0].append(event)
        elif event[1].days_to() == 0: eventsLists[1].append(event)
        elif 0 < event[1].days_to() <= 7: eventsLists[2].append(event)

    eventsLists[2].sort(key=lambda x: x[1])
    eventsLists[0].sort(key=lambda x: x[1], reverse=True)

    return eventsLists

def events_info(args: list[str], attr: list[str]) -> None:
    if args:
        print("Команда не принимает аргументов.\nФормат: [<атрибуты>]")
        exit(3)

    eventsLists = class_events(get_events())
    titles = ["\nНедавно прошедшие события:",
              "\nСобытия сегодня:",
              "\nСобытия на следующей неделе:",]

    print(titles[1])
    for event in eventsLists[1]:
        print(f"{event[2]}: {event[3]}")
    
    for i in (2, 0):
        print(titles[i])
        for event in eventsLists[i]:
            print(f"[{event[1].to_str()}] {event[2]}: {event[3]}")

def events_list(args: list[str], attr: list[str]) -> None:
    if args:
        print("Команда не принимает аргументов.\nФормат: [<атрибуты>]")
        exit(3)

    print()
    events = get_events()
    for i in range(len(events)):
        ns = events[i][1].next_suit()
        if not ns:
            events[i].append(INF)
        else:
            events[i].append(ns.days_to())
    events.sort(key=lambda x: x[-1])
    
    for event in events:
        if isinstance(event[-1], Infinity):
            delta = "-"
        else:
            delta = event[-1]
        print(f"[{event[1].to_str()}] [{delta}] {event[2]}: {event[3]}")

def event_delet(args: list[str], attr: list[str]) -> None:
    if len(args) != 1:
        print("Невернй формат команды.\nФормат: <дата> [<атрибуты>]")
        exit(2)

    mask = pars_date(args[0])
    events = get_events()
    suit_events = []

    print()
    for event in events:
        if event[1].is_suit(mask):
            suit_events.append(event)
            print(f"[{len(suit_events)}] [{event[1].to_str()}] {event[2]}: {event[3]}")
    print()

    if len(suit_events) == 0:
        print("Подходящие события не найдены")
        return
    
    ind = "not"
    while not ind.isdigit() or not (-1 < int(ind) <= len(suit_events)):
        ind = input("Выберите номер события: ")
        
    if ind == "0":
        print("Удаление отмененно.")
        return
        
    with open(FILE, 'r', encoding=ENCODING) as file:
        lines = file.readlines()

    ind = suit_events[int(ind)-1][0] + 1
    lines = lines[:ind] + lines[ind+1:]
    if len(lines) != 0:
        lines[-1] = lines[-1].rstrip()

    with open(FILE, 'w', encoding=ENCODING) as file:
        file.writelines(lines)
    
    print("Событие удалён.")

def start_ui(args, attr):
    if args:
        print("Команда не принимает аргументов.\nФормат: [<атрибуты>]")
        exit(3)

    eventsList = get_events()
    eventsLists = class_events(eventsList)

    root = creat_window()

    headers = ["События сегодя:", "События на следующей неделе:", "Недавно прошедшие события:", "Закрепленные события:"]
    scrolls = []
    for i in range(len(headers)):
        scrolls.append(ScrollList(root, 5, headers[i]))
        scrolls[-1].pack()

    if len(eventsLists[1]):
        for event in eventsLists[1]:
            scrolls[0].append(event[1], event[2])
    else:
        scrolls[0].append("Сегодня ничего нет.")
    
    for i, j in zip([1, 2], [2, 0]):
        if len(eventsLists[j]):
            for event in eventsLists[j]:
                scrolls[i].append(f"[{event[1].to_str()}] {event[2]}", event[3])
        else:
            scrolls[i].append("Тут пусто.")
        scrolls[i].update()

    for event in eventsList:
        if event[4]["pin"]:
            ns = event[1].next_suit()
            if not ns: delta = "-"
            else: delta = ns.days_to()
            scrolls[3].append(f"[{delta}] [{event[1].to_str()}] {event[2]}", event[3])

    for i in [0, 1, 3]:
        scrolls[i].update()
        scrolls[i]._expand_event()

    def root_rescale(event=None):
        heigh = 25
        for i in range(len(headers)):
            heigh += scrolls[i].winfo_height()
        root.geometry(f"{WIDTH}x{heigh}")
    
    root.bind("<ButtonRelease-1>", root_rescale)

    root_rescale()
    root.mainloop()

start = time()

if not exists(FILE):
    with open(FILE, 'w', encoding=ENCODING) as file:
        file.write(f"Start at {TODAY.isoformat()}")

if len(argv) == 1:
    print("\n".join(["Доступные команды:",
                     "add - добавление события,",
                     "del - удалени события,",
                     "info - информация о ближайших событиях,",
                     "list - список всех событий,",
                     "ui - запуск графической оболочки",]))
    exit(1)

command = argv[1]
args, attr = args_pars(argv[2:])

match command:
    case 'add': event_add(args, attr)
    case 'info': events_info(args, attr)
    case 'list': events_list(args, attr)
    case 'del': event_delet(args, attr)
    case 'ui': start_ui(args, attr)
    case _: print("Команда не распознанна")

end = time()

print('\n', end - start, sep='')
