import sys

# Powstrzymanie Pythona od tworzenia dodatkowych plików i katalogów przy wykonywaniu skryptu
sys.dont_write_bytecode = True

from enum import Enum
from bs4 import BeautifulSoup
from decimal import Decimal
from system_punktowy import points_to_positions
import re
import os

# Typy klasyfikacji
class Classification(Enum):
    DRIVERS = 1
    MANUFACTURERS = 2
    TEAMS = 3

# Tablica zawierająca wartości logiczne oznaczające czy przyznano pełne punkty
FULL_POINTS = []

# Słownik zawierający liczbę kolumn przed kolumnami z wynikami w typach klasyfikacji
points_offsets = {
	Classification.DRIVERS: 3,
	Classification.MANUFACTURERS: 3,
	Classification.TEAMS: 4
}

# Usuwanie zer końcowych z części ułamkowej liczby typu Decimal
def remove_zeros(decimal):
	return (
		decimal.quantize(Decimal(1))
		if decimal == decimal.to_integral()
		else decimal.normalize()
	)

# Sprawdza prawidłowość podanych skal punktowych
def validate_scales(scales):
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

# Zlicza liczbę flag w pierwszym wierszu tabeli (czyli liczbę wyścigów)
def count_flags(table_row):
	return str(table_row).count('alt="flag"')

# Odczytanie typu klasyfikacji z pliku
def read_classification_type_file(html_second_row):
	row_string = str(html_second_row)

	if re.search('Team', row_string):
		return Classification.TEAMS
	elif re.search('Manufacturer', row_string):
		return Classification.MANUFACTURERS
	elif re.search('Driver', row_string):
		return Classification.DRIVERS
	else:
		print('Nie udało się ustalić typu klasyfikacji')

# Funkcja pomocnicza, która odpowiednio koloruje komórki z pozycjami na podstawie punktów
def print_positions(points_columns, points_scales):
	global FULL_POINTS

	for x in range(0, len(points_columns)):
		points = points_columns[x].find('div', class_='grid-2').find_all('div')
		scale = points_to_positions[str(points_scales[x])]
		full_points = FULL_POINTS[x]
		suffix = 'PP' if points[1].text.strip() == "1" else ""
		coloured_position = ''

		if full_points:
			coloured_position = scale[points[0].text.strip() + suffix]
		else:
			doubled = Decimal(points[0].text.strip()) * 2
			doubled = remove_zeros(doubled)
			coloured_position = scale[str(doubled) + suffix]
		
		print(coloured_position)

# Wypisanie tabeli z klasyfikacją punktową
def print_table(data_rows, races_count, points_scales, classification_type):
	global points_offsets
	points_offset = points_offsets[classification_type]

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

		position = str(tds[0].find('div').text).strip()
		name = str(tds[1].text).strip() if classification_type == Classification.MANUFACTURERS else str(tds[1].find('a').text).strip()
		
		if classification_type == Classification.DRIVERS:
			split = name.split(' ')
			if len(split) == 2:
				split[1] = split[1].capitalize()
				name = split[0] + ' ' + split[1]
			elif len(split) > 2:
				name = split[0] + ' ' + ' '.join(split[1:]).lower()

		number = str(tds[2].text).strip() if classification_type == Classification.TEAMS else ''
		flag = str(tds[3].text).strip() if classification_type == Classification.TEAMS else str(tds[2].text).strip()
		points = str(tds[points_offset + races_count].text).strip()

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
def read_classification_type_input():
	num = 0

	print('Wybierz typ klasyfikacji w podanym pliku HTML:')

	while True:
		try:
			print('1. Kierowcy')
			print('2. Zespoły')
			print('3. Producenci')
			
			num = int(input('Wybór (1-3): '))
		except ValueError:
			print('Podaj liczbę naturalną z przedziału 1-3.')

		if num == 1:
			return Classification.DRIVERS
		elif num == 2:
			return Classification.TEAMS
		elif num == 3:
			return Classification.MANUFACTURERS
		else:
			print('Liczba musi być w przedziale 1-3.')

# Odczytanie czy w wyścigach przydzielono pełne punkty
def read_were_half_points_awarded():
	num = 0
	were_half_points_awarded = False

	print('Czy w którymś z wyścigów przydzielono połowę punktów?')
	print('1. Tak')
	print('2. Nie')

	while True:
		try:
			num = int(input('Wybór (1-2): '))
		except ValueError:
			print('Podaj liczbę naturalną z przedziału 1-2.')

		if num == 1:
			were_half_points_awarded = True
			break
		elif num == 2:
			break
		else:
			print('Liczba musi być w przedziale 1-2.')
	
	if were_half_points_awarded is True:
		read_half_points_races()

# Odczytanie w których wyścigach przydzielono połowę punktów
def read_half_points_races():
	global FULL_POINTS

	num = 0
	races = 0

	while True:
		try:
			num = int(input('Liczba wyścigów z połową punktów: '))
		except ValueError:
			print('Podaj liczbę naturalną')
		
		if num <= 0:
			print('Podaj liczbę naturalną')
		else:
			races = num
			break

	for x in range(1, races + 1):
		race_num = 0
		
		while True:
			try:
				race_num = int(input(f'Którym w sezonie był {x}. wyścig z połową punktów: '))
			except ValueError:
				print('Podaj liczbę naturalną')
			
			if race_num <= 0:
				print('Podaj liczbę naturalną')
			else:
				FULL_POINTS[race_num - 1] = False
				break

# Odczytanie skali punktowych w poszczególnych wyścigach
def read_point_scales(races_number):
	scales_input = ''
	scales = []

	while True:
		try:
			scales_input = input('Podaj skale punktowe w wyścigach, liczby oddziel spacjami: ')
		except ValueError:
			print('Niewłaściwe dane na wejściu')
		
		scales = scales_input.split(' ')
		if len(scales) != races_number:
			print(f'Liczba podanych skali punktowych ({len(scales)}) nie jest równa liczbie wyścigów ({races_number})')
			continue
		
		if validate_scales(scales):
			break

	return scales

# Odczytanie ścieżki do pliku
def read_json_path():
	text = ''

	while True:
		text = input('Podaj ścieżkę do pliku HTML pobranego ze strony WEC:\n')

		if not os.path.isfile(text):
			print('Ścieżka nieprawidłowa, spróbuj ponownie.')
			continue
		else:
			return text

# Główna funkcja skryptu
def main():
	global FULL_POINTS

	file_path = read_json_path()

	with open(file_path, encoding='utf-8') as file:
		soup = BeautifulSoup(file, 'lxml')
		
		flag_count = count_flags(soup.find_all('tr', class_='tr1'))

		for x in range(0, flag_count):
			FULL_POINTS.append(True)

		classification_type = None

		classification_type = read_classification_type_file(soup.find_all('tr', class_='tr2'))

		if classification_type is None:
			classification_type = read_classification_type_input()

		points_scales = read_point_scales(flag_count)

		read_were_half_points_awarded()

		race_data = soup.find_all('tr', class_='tr-data')

		print_table(race_data, flag_count, points_scales, classification_type)

if __name__ == '__main__':
    main()