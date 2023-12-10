import sys

# Preventing Python from creating any additional files/catalogues during script's execution
sys.dont_write_bytecode = True

import os
import csv

# Reading cars names from a file and priting them in console window in
# a format suitable to paste into cars dictionary in db.py
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
		print(f'Processed lines: {line_count}')

# Checking columns in given .CSV file
def verify_csv(file):
	with open(file, mode='r', encoding='utf-8-sig') as csv_file:
		csv_reader = csv.DictReader(csv_file, delimiter=';')
		csv_dict = dict(list(csv_reader)[0])
		headers = list(csv_dict.keys())

		return 'VEHICLE' in headers

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
		if not verify_csv(text):
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