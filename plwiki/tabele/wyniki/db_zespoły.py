import sys

# Powstrzymanie Pythona od tworzenia dodatkowych plików i katalogów przy wykonywaniu skryptu
sys.dont_write_bytecode = True

import os
import csv
from db import countries_ACO as countries

# Odczytanie nazw zespołów i wypisanie ich w formacie do zapisania w pliku db.py
def read_csv(file):
	with open(file, mode='r', encoding='utf-8-sig') as csv_file:
		csv_reader = csv.DictReader(csv_file, delimiter=';')
		line_count = 0
		teams = []

		for row in csv_reader:
			country = ''
			try:
				country_id = row["ECM Country Id"]
				country = countries[country_id]
			except:
				country = '?'

			team = '"#%s %s": {"country": "%s", "link": "#%s [[%s]]"}' % (
				row["NUMBER"],
				row["TEAM"],
				country,
				row["NUMBER"],
				row["TEAM"]
			)

			teams.append(team)

			line_count += 1

		print(',\n'.join(teams) + ',')

		print(f'Przetworzone linie: {line_count}')

# Sprawdzenie czy podany plik ma wymagane kolumny
def verify_csv(file):
	with open(file, mode='r', encoding='utf-8-sig') as csv_file:
		csv_reader = csv.DictReader(csv_file, delimiter=';')
		csv_dict = dict(list(csv_reader)[0])
		headers = list(csv_dict.keys())

		return 'NUMBER' in headers and 'TEAM' in headers

# Odczytanie ścieżki do pliku
def read_csv_path():
	text = ''

	while True:
		text = input('Podaj ścieżkę do pliku .CSV pobranego ze strony Alkamelsystems:\n')

		if not os.path.isfile(text):
			print('Ścieżka nieprawidłowa, spróbuj ponownie.')
			continue
		elif not verify_csv(text):
			print('Plik nie posiada wymaganych kolumn.')
			continue
		else:
			return text

def main():
	file = read_csv_path()

	read_csv(file)

if __name__ == '__main__':
	main()