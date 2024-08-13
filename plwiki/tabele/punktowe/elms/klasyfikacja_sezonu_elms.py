import sys

# Powstrzymanie Pythona od tworzenia dodatkowych plików i katalogów przy wykonywaniu skryptu
sys.dont_write_bytecode = True

if True:  # noqa: E402
	import os
	import json
	from decimal import Decimal
	from enum import Enum


# Typy danych w klasyfikacjach
class ClassificationData(Enum):
	DRIVERS = 1
	TEAMS = 2


# Czy przyznano pełne punkty, ELMS nie ma więcej niż 6 wyścigów w sezonie
FULL_POINTS = [True, True, True, True, True, True]

# Pozycje i kolory tła dla systemu punktowego
points_to_positions: dict[str, str] = {
	'25': '| style="background:#FFFFBF;" | 1',
	'25PP': '| style="background:#FFFFBF; font-weight: bold;" | 1',
	'18': '| style="background:#DFDFDF;" | 2',
	'18PP': '| style="background:#DFDFDF; font-weight: bold;" | 2',
	'15': '| style="background:#FFDF9F;" | 3',
	'15PP': '| style="background:#FFDF9F; font-weight: bold;" | 3',
	'12': '| style="background:#DFFFDF;" | 4',
	'12PP': '| style="background:#DFFFDF; font-weight: bold;" | 4',
	'10': '| style="background:#DFFFDF;" | 5',
	'10PP': '| style="background:#DFFFDF; font-weight: bold;" | 5',
	'8': '| style="background:#DFFFDF;" | 6',
	'8PP': '| style="background:#DFFFDF; font-weight: bold;" | 6',
	'6': '| style="background:#DFFFDF;" | 7',
	'6PP': '| style="background:#DFFFDF; font-weight: bold;" | 7',
	'4': '| style="background:#DFFFDF;" | 8',
	'4PP': '| style="background:#DFFFDF; font-weight: bold;" | 8',
	'2': '| style="background:#DFFFDF;" | 9',
	'2PP': '| style="background:#DFFFDF; font-weight: bold;" | 9',
	'1': '| style="background:#DFFFDF;" | 10',
	'1PP': '| style="background:#DFFFDF; font-weight: bold;" | 10',
	'0.5': '| style="background:#DFFFDF;" | >10',
	'0.5PP': '| style="background:#DFFFDF; font-weight: bold;" | >10',
	'0': '| style="background:#CFCFFF;" |',
	'0PP': '| style="background:#CFCFFF; font-weight: bold;" |',
	'NS': '| style="background:#CFCFFF;" | NS',
	'NSPP': '| style="background:#CFCFFF; font-weight: bold;" | NS'
}


# Usuwanie zer końcowych z części ułamkowej liczby typu Decimal
def remove_zeros(decimal: Decimal) -> Decimal:
	return (
		decimal.quantize(Decimal(1))
		if decimal == decimal.to_integral()
		else decimal.normalize()
	)


# Kolorowanie komórek z pozycjami na podstawie punktów
def print_points(points_columns) -> None:
	for x in range(len(points_columns)):
		session = points_columns[x]
		if session['race_points_valid_for_net_points']:
			if session['status'] == '':
				suffix: str = ''
				if session['pole_points'] == 1:
					suffix = 'PP'

				if FULL_POINTS[x] is False:
					doubled: Decimal = Decimal(session['race_points']) * 2
					doubled = remove_zeros(doubled)

					print(points_to_positions[str(doubled) + suffix])
				else:
					try:
						print(points_to_positions[str(session['race_points']) + suffix])
					except KeyError:
						print(' ')

			elif session['status'] == 'not_classified':
				nc_suffix: str = ''

				if session['pole_points'] == 1:
					nc_suffix = 'PP'

				print(points_to_positions['NS' + nc_suffix])
			elif session['status'] == 'did_not_race':
				print('| –')
			else:
				print('|')
		else:
			print('|')


# Wczytanie pliku i wypisanie tabeli z klasyfikacją punktową
def read_json(file_path: str, value_type: ClassificationData):
	with open(file_path, 'r', encoding='UTF-8') as read_file:
		data = json.load(read_file)

		championship_info = data['championship']

		table_header: list[str] = [
			'{| class="wikitable" style="font-size:85%; text-align:center;"',
			'! {{Tooltip|Poz.|Pozycja}}',
			'! Kierowca' if value_type == ClassificationData.DRIVERS else '| Zespół',
			f'! colspan="{len(championship_info["sessions"])}" | Rundy',
			'! Punkty',
			'|-'
		]

		print(*table_header, sep='\n')

		for node in data['classification']:  # type: dict
			print('! %i' % (node['position']))

			if value_type == ClassificationData.DRIVERS:
				if node.get('driver_first_name') is not None:
					firstname: str = node.get('driver_first_name')
				elif node.get('driver_firstname') is not None:
					firstname: str = node.get('driver_firstname')
				else:
					firstname: str = ''

				if firstname != '':
					print('| align="left" | {{{{Flaga|{flag}}}}} [[{firstname} {lastname}]]'.format(
						flag=node['country'],
						firstname=firstname,
						lastname=node['driver_secondname'].capitalize()
					))
				else:
					print('| align="left" | ')

			elif value_type == ClassificationData.TEAMS:
				try:
					print('| align="left" | {{{{Flaga|{flag}}}}} #{number} [[{team}]]'.format(
						flag=node['nat'],
						number=node['key'],
						team=node['team']
					))
				except KeyError:
					print('| align="left" | ')

			print_points(node['points_by_session'])

			if type(node['total_points']) is int:
				print(f'! {node["total_points"]}')
			else:
				print(f'! {str(node["total_points"]).replace(".", ",")}')

			print('|-')

		print('|}')


# Odczytanie ścieżki do pliku
def read_json_path() -> str:
	while True:
		text: str = input('Podaj ścieżkę do pliku .json pobranego ze strony ELMS:\n').strip()

		if not os.path.isfile(text):
			print('Ścieżka nieprawidłowa, spróbuj ponownie.')
			continue
		if not text.lower().endswith('.json'):
			print('Ścieżka nie prowadzi do pliku .json, spróbuj ponownie.')
			continue
		else:
			return text


# Odczytanie typu klasyfikacji
def read_data_type() -> ClassificationData:
	print('Wybierz typ klasyfikacji w podanym pliku .json:')

	while True:
		print('1. Klasyfikacja kierowców')
		print('2. Klasyfikacja zespołów')

		try:
			num: int = int(input('Wybór (1-2): ').strip())
		except ValueError:
			print('Podaj liczbę 1 lub 2.')
			continue

		if num == 1:
			return ClassificationData.DRIVERS
		elif num == 2:
			return ClassificationData.TEAMS
		else:
			print('Dozwolone liczby to 1 lub 2.')
			continue


# Odczytanie czy w wyścigach przydzielono pełne punkty
def read_were_half_points_awarded() -> None:
	were_half_points_awarded = False

	print('Czy w którymś z wyścigów przydzielono połowę punktów?')

	while True:
		print('1. Tak')
		print('2. Nie')

		try:
			num: int = int(input('Wybór (1-2): ').strip())
		except ValueError:
			print('Podaj liczbę 1 lub 2.')
			continue

		if num == 1:
			were_half_points_awarded = True
			break
		elif num == 2:
			break
		else:
			print('Dozwolone liczby to 1 lub 2.')

	if were_half_points_awarded:
		read_half_points_races()


# Odczytanie, w których wyścigach przydzielono połowę punktów
def read_half_points_races():
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
			continue
		else:
			break

	for x in range(1, num + 1):
		while True:
			try:
				race_num: int = int(input(f'Którym w sezonie był {x}. wyścig z połową punktów: '))
			except ValueError:
				print('Podaj liczbę naturalną')
				continue

			if race_num <= 0:
				print('Podaj liczbę naturalną')
				continue
			else:
				FULL_POINTS[race_num - 1] = False
				break


# Główna funkcja skryptu
def main() -> None:
	json_path: str = read_json_path()

	data_type: ClassificationData = read_data_type()

	read_were_half_points_awarded()

	read_json(json_path, data_type)


# Uruchamia główną funkcję
if __name__ == "__main__":
	main()
