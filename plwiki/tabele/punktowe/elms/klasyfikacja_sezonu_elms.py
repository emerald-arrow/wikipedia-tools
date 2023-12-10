import os
import json
from decimal import Decimal
from enum import Enum

# Typy danych w klasyfikacjach
class ClassificationData(Enum):
	DRIVERS = 1
	TEAMS = 2

# Tablice określające czy przyznano pełne punkty, ELMS nie ma więcej niż 6 wyścigów w sezonie
FULL_POINTS = [True, True, True, True, True, True]

# Słownik zawierający odpowiednie pozycje i kolory tła dla systemu punktowego
points_to_positions = {
		25 : '| style="background:#FFFFBF;" | 1',
	'25PP' : '| style="background:#FFFFBF; font-weight: bold;" | 1',
		18 : '| style="background:#DFDFDF;" | 2',
	'18PP' : '| style="background:#DFDFDF; font-weight: bold;" | 2',
		15 : '| style="background:#FFDF9F;" | 3',
	'15PP' : '| style="background:#FFDF9F; font-weight: bold;" | 3',
		12 : '| style="background:#DFFFDF;" | 4',
	'12PP' : '| style="background:#DFFFDF; font-weight: bold;" | 4',
		10 : '| style="background:#DFFFDF;" | 5',
	'10PP' : '| style="background:#DFFFDF; font-weight: bold;" | 5',
	 	 8 : '| style="background:#DFFFDF;" | 6',
	 '8PP' : '| style="background:#DFFFDF; font-weight: bold;" | 6',
	 	 6 : '| style="background:#DFFFDF;" | 7',
	 '6PP' : '| style="background:#DFFFDF; font-weight: bold;" | 7',
	 	 4 : '| style="background:#DFFFDF;" | 8',
	 '4PP' : '| style="background:#DFFFDF; font-weight: bold;" | 8',
	 	 2 : '| style="background:#DFFFDF;" | 9',
	 '2PP' : '| style="background:#DFFFDF; font-weight: bold;" | 9',
	 	 1 : '| style="background:#DFFFDF;" | 10',
	 '1PP' : '| style="background:#DFFFDF; font-weight: bold;" | 10',
	   0.5 : '| style="background:#DFFFDF;" | >10',
   '0.5PP' : '| style="background:#DFFFDF; font-weight: bold;" | >10',
	 	 0 : '| style="background:#CFCFFF;" |',
	 '0PP' : '| style="background:#CFCFFF; font-weight: bold;" |',
	  'NS' : '| style="background:#CFCFFF;" | NS',
	'NSPP' : '| style="background:#CFCFFF; font-weight: bold;" | NS'
}

# Usuwanie zer końcowych z części ułamkowej liczby typu Decimal
def remove_zeros(decimal):
	return (
		decimal.quantize(Decimal(1))
		if decimal == decimal.to_integral()
		else decimal.normalize()
	)

# Funkcja pomocnicza, która odpowiednio koloruje komórki z pozycjami na podstawie punktów
def print_points(points_columns):
	for x in range(len(points_columns)):
		session = points_columns[x]
		if session['race_points_valid_for_net_points'] == True:
			if session['status'] == '':
				suffix = ''
				if session['pole_points'] == 1:
					suffix = 'PP'

				if FULL_POINTS[x] is False:
					doubled = Decimal(session['race_points']) * 2
					doubled = remove_zeros(doubled)
					if suffix == '':
						print("%s" % (points_to_positions[doubled]))
					elif suffix == 'PP':
						print("%s" % (points_to_positions[str(doubled)+'PP']))
				else:
					try:
						if suffix == '':
							print("%s" % (points_to_positions[session['race_points']]))
						elif suffix == 'PP':
							print("%s" % (points_to_positions[str(session['race_points'])+'PP']))
					except KeyError:
						print('NN')

			elif session['status'] == 'not_classified':
				if session['pole_points'] == 1:
					print('%s' % (points_to_positions['NSPP']))
				else:
					print('%s' % (points_to_positions['NS']))
			elif session['status'] == 'did_not_race':
				print('| –')
			else:
				print('|')

# Funkcja wczytuająca plik i wypisująca tabelę z klasyfikacją punktową
def read_json(file, value_type):
	with open(file, 'r', encoding='UTF-8') as read_file:
		data = json.load(read_file)

		championship_info = data['championship']

		print('{| class="wikitable" style="font-size:85%; text-align:center;"')
		print('! {{Tooltip|Poz.|Pozycja}}')
		print('! Kierowca')
		print(f'! colspan="{len(championship_info["sessions"])}" | Rundy')
		print('! Punkty')
		print('|-')

		for node in data['classification']:
			print('! %i' % (node['position']))

			if value_type == ClassificationData.DRIVERS:
				firstnameFailed = False

				try:
					print('| align="left" | {{Flaga|%s}} [[%s %s]]' % 
						(node['country'], node['driver_first_name'], node['driver_secondname'].capitalize()))
				except:
					firstnameFailed = True

				if firstnameFailed == True:
					try:
						print('| align="left" | {{Flaga|%s}} [[%s %s]]' % 
							(node['country'], node['driver_firstname'], node['driver_secondname'].capitalize()))
					except:
						print('| align="left" | Imię Nazwisko')

			elif value_type == ClassificationData.TEAMS:
				try:
					print('| align="left" | {{Flaga|%s}} #%s [[%s]]' %
						(node['nat'], node['key'], node['team']))
				except:
					print('| align="left" | {{Flaga|}} # Nazwa')

			print_points(node['points_by_session'])

			if type(node['total_points']) is int:
				print(f'! {node["total_points"]}')
			else:
				print(f'! {str(node["total_points"]).replace(".", ",")}')

			print('|-')

		print('|}')

# Odczytanie ścieżki do pliku
def read_json_path():
	text = ''

	while True:
		text = input('Podaj ścieżkę do pliku .json pobranego ze strony ELMS:\n')

		if not os.path.isfile(text):
			print('Ścieżka nieprawidłowa, spróbuj ponownie.')
			continue
		else:
			return text

# Odczytanie typu klasyfikacji
def read_json_type():
	num = 0

	print('Wybierz typ klasyfikacji w podanym pliku .json:')
	print('1. Klasyfikacja kierowców')
	print('2. Klasyfikacja zespołów')

	while True:
		try:
			num = int(input('Wybór (1-2): '))
		except ValueError:
			print('Podaj liczbę 1 lub 2.')

		if num == 1:
			return ClassificationData.DRIVERS
		elif num == 2:
			return ClassificationData.TEAMS
		else:
			print('Dozwolone liczby to 1 lub 2.')

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
			print('Podaj liczbę 1 lub 2.')

		if num == 1:
			were_half_points_awarded = True
			break
		elif num == 2:
			break
		else:
			print('Dozwolone liczby to 1 lub 2.')
	
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

# Główna funkcja skryptu
def main():
	file = read_json_path()
	value_type = read_json_type()

	read_were_half_points_awarded()

	read_json(file, value_type)

# Uruchamia główną funkcję
if __name__ == "__main__":
	main()