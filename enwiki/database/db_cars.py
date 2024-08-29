import sys

# Prevents creating __pycache__ directory
sys.dont_write_bytecode = True

if True:  # noqa: E402
    import os
    import csv
    from csv import DictReader, writer as CsvWriter
    import re
    from pathlib import Path

    project_path = str(Path(__file__).parent.parent.parent)
    if project_path not in sys.path:
        sys.path.append(project_path)

    from common.db_queries.wikipedia_table import get_wiki_id
    from common.models.car import Car

# Message when script must stop its execution
script_cannot_continue = "Script cannot continue and it's going to stop its execution."


# Saves cars data into .csv file
def write_cars_csv(cars: list[Car]) -> None:
    from datetime import datetime

    timestamp: str = datetime.now().strftime("%Y-%m-%dT%H-%M-%S")
    filename: str = f'cars_{timestamp}.csv'

    headers: list[str] = ['codename', 'link']

    with open(filename, mode='w', encoding='utf-8-sig') as csv_file:
        csv_writer: CsvWriter = CsvWriter(
            csv_file,
            delimiter=',',
            quoting=csv.QUOTE_NONNUMERIC,
            lineterminator='\n'
        )

        csv_writer.writerow(headers)

        for c in cars:  # type: Car
            csv_writer.writerow(list(c))

    print(f'\nNumer of cars saves into {filename}: {len(cars)}')


# Reads cars data from results .csv file
def read_results_csv(path: str, wiki_id: int) -> list[Car]:
    from common.db_queries.car_tables import check_car_exists

    cars: list[Car] = list()

    with open(path, mode='r', encoding='utf-8-sig') as csv_file:
        csv_reader: DictReader[str] = DictReader(csv_file, delimiter=';')
        line_count: int = 0
        checked: set[str] = set()

        print('')

        for row in csv_reader:  # type: dict[str]
            line_count += 1

            codename: str | None = row.get('VEHICLE')

            if type(codename) is not str:
                continue

            if codename in checked:
                continue

            checked.add(codename)

            if check_car_exists(codename, wiki_id):
                print(f'{codename} is already in database')
                continue

            cars.append(
                Car(
                    codename=codename,
                    link=f'[[{codename}]]'
                )
            )

        print(f'\nProcessed lines: {line_count}\nNumer of new cars found: {len(cars)}')

    return cars


# Checks headers of results .csv file
def verify_results_csv(path: str) -> bool:
    with open(path, mode='r', encoding='utf-8-sig') as csv_file:
        csv_reader = csv.DictReader(csv_file, delimiter=';')
        csv_dict = dict(list(csv_reader)[0])
        headers = list(csv_dict.keys())

        return 'VEHICLE' in headers


# Reads path to results .csv file
def read_path_to_results_csv() -> str:
    while True:
        text = input('\nPlease enter path to a results .csv file downloaded from an Alkamelsystems website:\n').strip()

        if not os.path.isfile(text):
            print('\nInvalid path, please try again.')
            continue
        if not text.lower().endswith('.csv'):
            print("\nFile under given path doesn't have .csv extension.")
            continue
        if not verify_results_csv(text):
            print("\nFile under given path doesn't have VEHICLE in its header.")
            continue
        else:
            return text


# Saves cars data into .csv file
def dump_cars_data_to_csv() -> None:
    global script_cannot_continue

    enwiki_id: int | None = get_wiki_id('enwiki')

    if enwiki_id is None:
        print(f'\n{script_cannot_continue}')
        return

    if enwiki_id == -1:
        print(f"\nCouldn't find English Wikipedia in database. {script_cannot_continue}")
        return

    path: str = read_path_to_results_csv()

    cars: list[Car] = read_results_csv(path, enwiki_id)

    if len(cars) == 0:
        print("\nNo new cars found. Script's going to stop its execution.")
        return

    write_cars_csv(cars)


# Checks headers in cars data .csv file
def verify_cars_csv(path: str) -> bool:
    with open(path, mode='r', encoding='utf-8-sig') as csv_file:
        csv_reader = csv.DictReader(csv_file, delimiter=',')
        csv_dict = dict(list(csv_reader)[0])
        headers = list(csv_dict.keys())

        return (
            'codename' in headers and
            'link' in headers
        )


# Searches this directory for cars data .csv files
def get_cars_csv_files_in_dir() -> list[str]:
    csv_files: list[str] = []
    files = [f for f in os.listdir() if os.path.isfile(f)]

    for f in files:
        if re.search('cars_.*\\.([Cc][Ss][Vv])', f) is not None:
            if verify_cars_csv(f):
                csv_files.append(f)

    return csv_files


# Chooses cars data .csv file
def choose_car_csv_file() -> str:
    csv_files: list[str] = get_cars_csv_files_in_dir()

    if len(csv_files) > 1:
        while True:
            for x in range(0, len(csv_files)):
                print(f'{x + 1}. {csv_files[x]}')

            try:
                num = int(input(f'Choice (1-{len(csv_files)}): ').strip())
            except ValueError:
                print('\nPlease enter a number shown before file name.')
                continue

            if num - 1 in range(0, len(csv_files)):
                return csv_files[num - 1]
            else:
                print('\nWrong number, please try again.')
                continue
    elif len(csv_files) == 1:
        options = {
            1: 'Yes',
            2: 'No'
        }

        while True:
            msg: list[str] = [
                f'\nThe only found file was {csv_files[0]}.',
                'Do you want to save its contents into database?'
            ]
            print(*msg, sep=' ')

            for x in options:
                print(f'{x}. {options[x]}')

            try:
                num = int(input('Choice (1-2): ').strip())
            except ValueError:
                print('\nPlease enter number 1 or 2.')
                continue

            if num == 1:
                return csv_files[0]
            elif num == 2:
                return ''
            else:
                print('\nPlease enter number 1 or 2.')
                continue

    while True:
        text = input('\nPlease enter path to cars data .csv file:\n').strip()

        if not os.path.isfile(text):
            print('\nInvalid path, please try again.')
            continue
        if not text.lower().endswith('.csv'):
            print("\nFile under given path doesn't have .csv extension.")
            continue
        if not verify_cars_csv(text):
            print("\nFile under given path doesn't have required columns.")
            continue

        return text


# Reads cars data .csv file
def read_cars_csv(path: str) -> list[Car]:
    cars: list[Car] = list()

    with open(path, mode='r', encoding='utf-8-sig') as csv_file:
        csv_reader: DictReader[str] = DictReader(csv_file, delimiter=',')
        line_count: int = 0

        for row in csv_reader:  # type: dict[str]
            line_count += 1

            codename: str | None = row.get('codename')
            link: str | None = row.get('link')

            if codename is not None and link is not None:
                cars.append(
                    Car(
                        codename=codename,
                        link=link
                    )
                )

        print(f'\nProcessed lines: {line_count}\nNumber of cars found: {len(cars)}')

    return cars


# Saves cars data into database
def save_cars_data_to_db() -> None:
    from common.db_queries.car_tables import add_cars
    global script_cannot_continue

    enwiki_id: int | None = get_wiki_id('enwiki')

    if enwiki_id is None:
        print(f'\n{script_cannot_continue}')
        return

    if enwiki_id == -1:
        print(f"\nCouldn't find English Wikipedia in database. {script_cannot_continue}")
        return

    chosen_file: str = choose_car_csv_file()

    if chosen_file == '':
        print(f'\n{script_cannot_continue}')
        return

    cars: list[Car] = read_cars_csv(chosen_file)

    if len(cars) == 0:
        print("\nNo cars found. Script's going to stop its execution.")
        return

    print()

    add_cars(cars, enwiki_id)


# Chooses script's working mode
def choose_mode() -> None:
    options = {
        1: 'Generate cars data .csv file',
        2: 'Save cars data into database',
        3: 'Exit'
    }

    while True:
        print('\nWhat would you like to do?')

        for o in options:
            print(f'{o}. {options[o]}')

        try:
            num = int(input(f'Choice (1-{len(options)}): ').strip())
        except ValueError:
            print('\nPlease enter a natural number between 1 and 3.')
            continue

        if num in options:
            match num:
                case 1:
                    dump_cars_data_to_csv()
                    break
                case 2:
                    save_cars_data_to_db()
                    break
                case 3:
                    return
        else:
            print('\nPlease enter a natural number between 1 and 3.')
            continue


if __name__ == "__main__":
    choose_mode()
