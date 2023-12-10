import sys

# Preventing Python from creating any additional files/catalogues during script's execution
sys.dont_write_bytecode = True

import os
import csv
from db import countries_ACO as countries

# Reading teams data from a file and priting them in console window in
# a format suitable to paste into teams dictionary in db.py
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

			team = '"#%s %s": {"country": "%s", "link": "%s"}' % (
				row["NUMBER"],
				row["TEAM"],
				country,
				row["TEAM"]
			)

			teams.append(team)

			line_count += 1

		print(',\n'.join(teams) + ',')

		print(f'Processed lines: {line_count}')

# Checking columns in given .CSV file
def verify_csv(file):
	with open(file, mode='r', encoding='utf-8-sig') as csv_file:
		csv_reader = csv.DictReader(csv_file, delimiter=';')
		csv_dict = dict(list(csv_reader)[0])
		headers = list(csv_dict.keys())

		return 'NUMBER' in headers and 'TEAM' in headers

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
if __name__ == '__main__':
	main()