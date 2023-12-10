import sys

# Powstrzymanie Pythona od tworzenia dodatkowych plików i katalogów przy wykonywaniu skryptu
sys.dont_write_bytecode = True

import os
import csv

# Odczytanie nazw samochodów i wypisanie ich w formacie do zapisania w pliku db.py
def read_csv(file):
	with open(file, mode='r', encoding='utf-8-sig') as csv_file:
		csv_reader = csv.DictReader(csv_file, delimiter=';')
		line_count = 0
		cars = set()

		for row in csv_reader:
			try:
				car = row["VEHICLE"]
			except:
				car = ''

			carEntry = '"%s": "[[%s]]"' % (
				car,
				car
			)

			cars.add(carEntry)
			line_count += 1
		
		print(',\n'.join(cars) + ',')
		print(f'Przetworzone linie: {line_count}')

# Sprawdzenie czy podany plik ma wymagane kolumny
def verify_csv(file):
	with open(file, mode='r', encoding='utf-8-sig') as csv_file:
		csv_reader = csv.DictReader(csv_file, delimiter=';')
		csv_dict = dict(list(csv_reader)[0])
		headers = list(csv_dict.keys())

		return 'VEHICLE' in headers

# Odczytanie ścieżki do pliku
def read_csv_path():
	text = ''

	while True:
		text = input('Podaj ścieżkę do pliku .CSV pobranego ze strony Alkamelsystems:\n')

		if not os.path.isfile(text):
			print('Ścieżka nieprawidłowa, spróbuj ponownie.')
			continue
		if not verify_csv(text):
			print('Plik nie posiada wymaganych kolumn.')
			continue
		else:
			return text

def main():
	file = read_csv_path()

	read_csv(file)

if __name__ == "__main__":
	main()