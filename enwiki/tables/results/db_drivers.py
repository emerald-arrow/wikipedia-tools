import sys

# Preventing Python from creating any additional files/catalogues during script's execution
sys.dont_write_bytecode = True

import os
import csv

# Reading drivers data from a file and priting them in console window in
# a format suitable to paste into drivers dictionary in db.py
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

		print(f'Processed lines: {line_count}')

# Checking columns in given .CSV file
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

# Reading a path to a .CSV file
def read_csv_path():
	text = ''

	while True:
		text = input('Please enter a path to a .CSV file downloaded from a Alkamelsystems website:\n')

		if not os.path.isfile(text):
			print('Invalid path, please try again.')
			continue
		if not text.lower().endswith('.csv'):
			print('The path does not lead to a .CSV file.')
			continue
		elif not verify_csv(text):
			print('The file does not have required columns.')
			continue
		else:
			return text

# Main function that starts other fuctions
def main():
	file = read_csv_path()
	read_csv(file)

# Autorun
if __name__ == "__main__":
	main()