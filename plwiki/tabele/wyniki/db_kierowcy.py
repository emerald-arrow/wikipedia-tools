import sys

# Powstrzymanie Pythona od tworzenia dodatkowych plików i katalogów przy wykonywaniu skryptu
sys.dont_write_bytecode = True

import os
import csv

# Odczytanie kierowców i wypisanie ich w formacie do zapisania w pliku db.py
def read_csv(file):
	with open(file, mode='r', encoding='utf-8-sig') as csv_file:
		csv_reader = csv.DictReader(csv_file, delimiter=';')
		line_count = 0
		drivers = []

		for row in csv_reader:
			driver1 = '"%s %s": {"country": "%s", "link": "[[%s %s]]"}' % (
				row["DRIVER1_FIRSTNAME"].lower(),
				row["DRIVER1_SECONDNAME"].lower(),
				row["DRIVER1_COUNTRY"],
				row["DRIVER1_FIRSTNAME"].capitalize(),
				row["DRIVER1_SECONDNAME"].capitalize(),
			)
			drivers.append(driver1)

			driver2 = '"%s %s": {"country": "%s", "link": "[[%s %s]]"}' % (
				row["DRIVER2_FIRSTNAME"].lower(),
				row["DRIVER2_SECONDNAME"].lower(),
				row["DRIVER2_COUNTRY"],
				row["DRIVER2_FIRSTNAME"].capitalize(),
				row["DRIVER2_SECONDNAME"].capitalize(),
			)
			drivers.append(driver2)

			if row["DRIVER3_COUNTRY"] != "":
				driver3 = '"%s %s": {"country": "%s", "link": "[[%s %s]]"}' % (
					row["DRIVER3_FIRSTNAME"].lower(),
					row["DRIVER3_SECONDNAME"].lower(),
					row["DRIVER3_COUNTRY"],
					row["DRIVER3_FIRSTNAME"].capitalize(),
					row["DRIVER3_SECONDNAME"].capitalize(),
				)
				drivers.append(driver3)

			line_count += 1

		print(',\n'.join(drivers)+',')

		print(f'Przetworzne linie: {line_count}')

# Sprwadzenie czy podany plik ma wymagane nazwy kolumn
def verify_csv(file):
	with open(file, mode='r', encoding='utf-8-sig') as csv_file:
		csv_reader = csv.DictReader(csv_file, delimiter=';')
		csv_dict = dict(list(csv_reader)[0])
		headers = list(csv_dict.keys())

		return ('DRIVER1_FIRSTNAME' in headers
	  			and 'DRIVER1_SECONDNAME' in headers
				and 'DRIVER1_COUNTRY' in headers
				and 'DRIVER2_FIRSTNAME' in headers
				and 'DRIVER2_SECONDNAME' in headers
				and 'DRIVER2_COUNTRY' in headers)

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

if __name__ == "__main__":
	main()