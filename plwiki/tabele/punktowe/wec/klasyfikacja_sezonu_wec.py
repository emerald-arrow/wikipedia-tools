import sys

# Powstrzymanie Pythona od tworzenia dodatkowych plików i katalogów przy wykonywaniu skryptu
sys.dont_write_bytecode = True

if True:  # noqa: E402
	from enum import Enum
	from bs4 import BeautifulSoup, ResultSet
	from decimal import Decimal
	from system_punktowy import points_to_positions
	import re
	import os


# Typy klasyfikacji
class Classification(Enum):
	DRIVERS = 1
	MANUFACTURERS = 2
	TEAMS = 3


# Wartości logiczne oznaczające czy przyznano pełne punkty w wyścigach
FULL_POINTS: list[bool] = []


# Liczby kolumn przed kolumnami z wynikami w zależności od typu klasyfikacji
points_offsets: dict[Classification, int] = {
	Classification.DRIVERS: 3,
	Classification.MANUFACTURERS: 3,
	Classification.TEAMS: 4
}


# Usuwanie zer końcowych z części ułamkowej liczby typu Decimal
def remove_zeros(decimal: Decimal) -> Decimal:
	return (
		decimal.quantize(Decimal(1))
		if decimal == decimal.to_integral()
		else decimal.normalize()
	)


# Sprawdzenie prawidłowości podanych skal punktowych
def validate_scales(scales: list[str]) -> bool:
	for x in range(0, len(scales)):
		if scales[x] not in points_to_positions.keys():
			if ',' not in scales[x]:
				print(f'Skala {scales[x]} jest nieprawidłowa')
				return False
			else:
				comma_convert = scales[x].replace(',', '.')
				if comma_convert not in points_to_positions.keys():
					print(f'Skala {scales[x]} jest nieprawidłowa')
					return False
				else:
					scales[x] = comma_convert
	
	return True


# Zliczenie liczby flag w pierwszym wierszu tabeli (czyli liczby wyścigów)
def count_flags(table_row) -> int:
	return str(table_row).count('alt="flag"')


# Odczytanie typu klasyfikacji z pliku
def read_classification_type_file(html_second_row) -> Classification | None:
	row_string: str = str(html_second_row)

	if re.search('Team', row_string, re.IGNORECASE):
		return Classification.TEAMS
	elif re.search('Manufacturer', row_string, re.IGNORECASE):
		return Classification.MANUFACTURERS
	elif re.search('Driver', row_string, re.IGNORECASE):
		return Classification.DRIVERS
	else:
		return None


# Wypisanie odpowiednio pokolorowanych komórek z pozycjami na podstawie punktów
def print_positions(points_columns, points_scales) -> None:
	global FULL_POINTS

	for x in range(0, len(points_columns)):
		points = points_columns[x].find('div', class_='grid-2').find_all('div')
		scale: dict[str, str] = points_to_positions[str(points_scales[x])]
		full_points: bool = FULL_POINTS[x]
		suffix: str = 'PP' if points[1].text.strip() == '1' else ''

		if full_points:
			coloured_position: str = scale[points[0].text.strip() + suffix]
		else:
			doubled: Decimal = Decimal(points[0].text.strip()) * 2
			doubled = remove_zeros(doubled)
			coloured_position: str = scale[str(doubled) + suffix]
		
		print(coloured_position)


# Wypisanie tabeli z klasyfikacją punktową
def print_table(
	data_rows: ResultSet, races_count: int, points_scales: list[str],
	classification_type: Classification
):
	global points_offsets
	points_offset: int = points_offsets[classification_type]

	print('{| class="wikitable" style="font-size:85%; text-align:center;"')
	print('! {{Tooltip|Poz.|Pozycja}}')

	if classification_type == Classification.DRIVERS:
		print('! Kierowca')
	elif classification_type == Classification.TEAMS:
		print('! Zespół')
	elif classification_type == Classification.MANUFACTURERS:
		print('! Producent')

	print(f'! colspan="{races_count}" | Rundy')
	print('! Punkty')
	print('|-')

	for row in data_rows:
		tds = row.find_all('td')

		position: str = str(tds[0].find('div').text).strip()

		if classification_type == Classification.MANUFACTURERS:
			name: str = str(tds[1].text).strip()
		else:
			name: str = str(tds[1].find('a').text).strip()
		
		if classification_type == Classification.DRIVERS:
			split_name: list[str] = name.split(' ')
			if len(split_name) == 2:
				split_name[1] = split_name[1].capitalize()
				name = f'{split_name[0]} {split_name[1]}'
			elif len(split_name) > 2:
				name = f'{split_name[0]} {' '.join(split_name[1:]).lower()}'

		number: str = str(tds[2].text).strip() if classification_type == Classification.TEAMS else ''
		flag: str = str(tds[3].text).strip() if classification_type == Classification.TEAMS else str(tds[2].text).strip()
		points: str = str(tds[points_offset + races_count].text).strip()

		print('! %s ' % re.sub('[a-z]', '', position))

		if classification_type == Classification.TEAMS:
			print('| align="left" | {{Flaga|%s}} %s [[%s]]' % (flag, number, name))
		else:
			print('| align="left" | {{Flaga|%s}} [[%s]]' % (flag, name))

		print_positions(
			tds[points_offset:points_offset + races_count],
			points_scales
		)

		print(f'! {points}')

		print('|-')
	
	print('|}')


# Odczytanie typu klasyfikacji na podstawie wyboru użytkownika
def read_classification_type_input() -> Classification:
	options: list[dict[str, Classification]] = [
		{'name': 'Kierowcy', 'enum': Classification.DRIVERS},
		{'name': 'Producenci', 'enum': Classification.MANUFACTURERS},
		{'name': 'Zespoły', 'enum': Classification.TEAMS}
	]

	print('Wybierz typ klasyfikacji w podanym pliku HTML:')

	while True:
		try:
			for x in range(0, len(options)):
				print(f'{x+1}. {options[x]["name"]}')
			
			num: int = int(input(f'Wybór (1-{len(options)}): ').strip())
		except ValueError:
			print('Podaj liczbę naturalną z przedziału 1-3.')
			continue
		
		if num - 1 not in range(0, len(options)):
			print(f'Liczba musi być w przedziale 1-{len(options)}.')
			continue
		else:
			return options[num]['enum']


# Odczytanie czy w wyścigach przydzielono pełne punkty
def read_were_half_points_awarded(season_races: int) -> None:
	were_half_points_awarded = False

	options: list[dict[str, bool]] = [
		{'option': 'Tak', 'bool': True},
		{'option': 'Nie', 'bool': False}
	]

	print('Czy w którymś z wyścigów przydzielono połowę punktów?')

	while True:
		try:
			for x in range(0, len(options)):
				print(f'{x+1}. {options[x]["option"]}')

			num: int = int(input('Wybór (1-2): ').strip())
		except ValueError:
			print('Wybierz 1 lub 2.')
			continue

		if num - 1 not in range(0, len(options)):
			print('Wybierz 1 lub 2.')
			continue
		else:
			were_half_points_awarded = options[num - 1]['bool']
			break
	
	if were_half_points_awarded:
		read_half_points_races(season_races)


# Odczytanie, w których wyścigach przydzielono połowę punktów
def read_half_points_races(season_races: int) -> None:
	global FULL_POINTS

	num: int = 0

	while True:
		try:
			num = int(input('Liczba wyścigów z połową punktów: ').strip())
		except ValueError:
			print('Podaj liczbę naturalną')
			continue
		
		if num <= 0:
			print('Podaj liczbę naturalną')
		else:
			break

	for x in range(1, num + 1):
		while True:
			try:
				race_num: int = int(input(f'Którym w sezonie był {x}. wyścig z połową punktów: ').strip())
			except ValueError:
				print('Podaj liczbę naturalną')
				continue
			
			if race_num <= 0:
				print('Podaj liczbę naturalną')
				continue
			elif race_num > season_races:
				print('Numer wyścigu nie może być większy niż liczba wyścigów w sezonie')
				continue
			else:
				FULL_POINTS[race_num - 1] = False
				break


# Odczytanie skali punktowych w poszczególnych wyścigach
def read_point_scales(races_number: int):
	msg: list[str] = [
		'Podaj skale punktowe w wyścigach (1/1,5/2),',
		'wpisz 0jeśli wyścig jeszcze się nie odbył,',
		'liczby oddziel spacjami.'
	]

	print(*msg, sep=' ')

	while True:
		try:
			scales_input: str = input('Skale punktowe: ').strip()
		except ValueError:
			print('Niewłaściwe dane na wejściu')
			continue
		
		scales: list[str] = scales_input.split(' ')
		if len(scales) != races_number:
			print(f'Liczba podanych skali punktowych ({len(scales)}) nie jest równa liczbie wyścigów ({races_number})')
			continue
		
		if validate_scales(scales):
			return scales
		else:
			print('Któraś z podanych skali jest nieprawidłowa')
			continue


# Odczytanie ścieżki do pliku
def read_html_path() -> str:
	while True:
		text: str = input('Podaj ścieżkę do pliku HTML pobranego ze strony WEC:\n').strip()

		if not os.path.isfile(text):
			print('Ścieżka nieprawidłowa, spróbuj ponownie.')
			continue
		if not text.lower().endswith('.html'):
			print("Plik pod podaną ścieżka nie zawiera rozszerzenia .html.")
			continue
		else:
			return text


# Główna funkcja skryptu
def main() -> None:
	global FULL_POINTS

	file_path: str = read_html_path()

	with open(file_path, encoding='utf-8') as file:
		soup: BeautifulSoup = BeautifulSoup(file, 'lxml')
		
		flag_count: int = count_flags(soup.find_all('tr', class_='tr1'))

		for x in range(0, flag_count):
			FULL_POINTS.append(True)

		classification_type: Classification | None = read_classification_type_file(
														soup.find_all('tr', class_='tr2')
													)

		if classification_type is None:
			classification_type = read_classification_type_input()

		points_scales: list[str] = read_point_scales(flag_count)

		read_were_half_points_awarded(flag_count)

		race_data: ResultSet = soup.find_all('tr', class_='tr-data')

		print_table(race_data, flag_count, points_scales, classification_type)


if __name__ == '__main__':
	main()
