import sys

# Preventing Python from creating any additional files/catalogues during script's execution
sys.dont_write_bytecode = True

import os
import csv
from enum import Enum
from db import cars
from db import drivers
from db import teams

# Sessions types
class Session(Enum):
	FP = 1
	QUALI = 2
	RACE = 3

# Races organisers
class Organiser(Enum):
	ACO = 1
	IMSA = 2

# Tyres manufacturers
class Tyres(Enum):
	G = 'Goodyear'
	M = 'Michelin'
	D = 'Dunlop'
	P = 'Pirelli'
	C = 'Continental'
	H = 'Hankook'

# Reading data from a .CSV file and printing table for race results
def print_race_table(organiser, filename):
	with open(filename, mode='r', encoding='utf-8-sig') as csv_file:
		csv_reader = csv.DictReader(csv_file, delimiter=';')
		line_count = 0
		class_winners = set()

		print('{| class="wikitable" style="font-size:95%;"')
		print('|+ Classification')
		print('! {{Tooltip|Pos|Position}}')
		print('! Class')
		print('! {{Tooltip|No|Car number}}')
		print('! Team')
		print('! Drivers')
		print('! Car')
		print('! Tyres')
		print('! Laps')
		print('! Time/Gap')

		for row in csv_reader:
			category = row["CLASS"]
			
			if category not in class_winners:
				print('|- style="font-weight: bold;')
				class_winners.add(category)
			else:
				print('|-')
			
			print(f'! {row["POSITION"]}')

			if row["GROUP"] != "":
				print(f'| align="center" | {category}<br />{row["GROUP"]}')
			else:
				print(f'| align="center" | {category}')

			try:
				team_data = teams['#%s %s' % (row["NUMBER"], row["TEAM"])]
				print(f'| align="center" | {row["NUMBER"]}')
				print(f'| {{{{flagicon|{team_data["country"]}}}}} {team_data["link"]}')
			except KeyError:
				print(f'| align="center" | {row["NUMBER"]}')
				print(f'| {{{{flagicon|_}}}} {row["TEAM"]}')

			try:
				driver1_data = None
				if organiser == Organiser.ACO:
					driver1_data = drivers[row["DRIVER_1"].lower()]
				elif organiser == Organiser.IMSA:
					driver1_name = row["DRIVER1_FIRSTNAME"] + " " + row["DRIVER1_SECONDNAME"]
					driver1_data = drivers[driver1_name.lower()]

				driver1 = '{{flagicon|%s}} %s' % (
					driver1_data["country"],
					driver1_data["link"]
				)
			except KeyError:
				driver1_name = None
				if organiser == Organiser.ACO:
					driver1_name = row["DRIVER_1"].split(" ", 1)
				elif organiser == Organiser.IMSA:
					driver1_name = [row["DRIVER1_FIRSTNAME"], row["DRIVER1_SECONDNAME"]]

				driver1 = '{{flagicon|_}} [[%s %s]]' % (
					driver1_name[0],
					driver1_name[1].capitalize()
				)

			try:
				driver2_data = None
				if organiser == Organiser.ACO:
					driver2_data = drivers[row["DRIVER_2"].lower()]
				elif organiser == Organiser.IMSA:
					driver2_name = row["DRIVER2_FIRSTNAME"] + " " + row["DRIVER2_SECONDNAME"]
					driver2_data = drivers[driver2_name.lower()]

				driver2 = '<br />{{flagicon|%s}} %s' % (
					driver2_data["country"],
					driver2_data["link"]
				)
			except KeyError:
				driver2_name = None
				if organiser == Organiser.ACO:
					driver2_name = row["DRIVER_2"].split(" ", 1)
				elif organiser == Organiser.IMSA:
					driver2_name = [row["DRIVER2_FIRSTNAME"], row["DRIVER2_SECONDNAME"]]

				driver2 = '<br />{{flagicon|_}} [[%s %s]]' % (
					driver2_name[0],
					driver2_name[1].capitalize()
				)

			if organiser == Organiser.ACO and row["DRIVER_3"] != "":
				try:
					driver3_data = drivers[row["DRIVER_3"].lower()]
					driver3 = '<br />{{flagicon|%s}} %s' % (
						driver3_data["country"],
						driver3_data["link"]
					)
				except KeyError:
					driver3_name = row["DRIVER_3"].split(" ", 1)
					driver3 = '<br />{{flagicon|_}} [[%s %s]]' % (
						driver3_name[0],
						driver3_name[1].capitalize()
					)
					
				print(f'| {driver1 + driver2 + driver3}')
			elif organiser == Organiser.IMSA and row["DRIVER3_FIRSTNAME"] != "":
				try:
					driver3_name = row["DRIVER3_FIRSTNAME"] + " " + row["DRIVER3_SECONDNAME"]
					driver3_data = drivers[driver3_name.lower()]
					driver3 = '<br />{{flagicon|%s}} %s' % (
						driver3_data["country"],
						driver3_data["link"]
					)
				except KeyError:
					driver3 = '<br />{{flagicon|_}} [[%s %s]]' % (
						row["DRIVER3_FIRSTNAME"],
						row["DRIVER3_SECONDNAME"]
					)

				print(f'| {driver1 + driver2 + driver3}')
			else:
				print(f'| {driver1 + driver2}')

			try:
				car = cars[row["VEHICLE"]]
			except KeyError:
				car = '[[%s]]' % (row["VEHICLE"])

			print(f'| {car}')

			tyres = None
			if organiser == Organiser.ACO:
				tyres = Tyres[row["TYRES"]].value
			elif organiser == Organiser.IMSA:
				tyres = Tyres[row["TIRES"]].value

			print(f'| align="center" | {{{{{tyres}}}}}')

			print(f'| align="center" | {row["LAPS"]}')
			
			if row["STATUS"] == 'Classified':
				if line_count > 0:
					gap = row["GAP_FIRST"].replace('\'',':')

					if gap.startswith("+"):
						print(f'| {gap}')
					else:
						print(f'| +{gap}')

				elif line_count == 0:
					total_time = row["TOTAL_TIME"].replace('\'',':')
					print(f'| align="center" | {total_time}')
			else:
				print(f'| {row["STATUS"]}')

			line_count += 1
		
		print('|-')
		print('|}')

		print(f'Processed lines: {line_count}')

# Reading data from a .CSV file and printing table for qualifying results
def print_quali_table(organiser, filename):
	with open(filename, mode='r', encoding='utf-8-sig') as csv_file:
		csv_reader = csv.DictReader(csv_file, delimiter=';')
		line_count = 0
		class_polesitters = set()

		print('{| class="wikitable sortable" style="font-size: 90%;"')
		print('! {{Tooltip|Pos|Position}}')
		print('! class="unsortable" | Class')
		print('! class="unsortable" | {{Tooltip|No.|Car number}}')
		print('! class="unsortable" | Team')
		print('! class="unsortable" | Driver')
		print('! class="unsortable" | Time')
		print('! class="unsortable" | Gap')
		print('! {{Tooltip|Grid|Grid position}}')

		for row in csv_reader:
			position = None
			category = row["CLASS"]

			if category not in class_polesitters:
				print('|- style="font-weight: bold;"')
				class_polesitters.add(category)
			else:
				print('|-')
			
			try:
				position = row["POSITION"]
				print(f'! {position}')
			except KeyError:
				try:
					position = row["POS"]
					print(f'! {position}')
				except:
					position = ''
					print(f'!')

			print(f'| align="center" | {category}')
			print(f'| align="center" | {row["NUMBER"]}')
		 
			try:
				team_data = teams['#%s %s' % (row["NUMBER"], row["TEAM"])]
				print(f'| {{{{flagicon|{team_data["country"]}}}}} {team_data["link"]}')
			except:
				print(f'| {{{{flagicon|_}}}} {row["TEAM"]}')

			try:
				driver1_name = '%s %s' % (
					row["DRIVER1_FIRSTNAME"].lower(),
					row["DRIVER1_SECONDNAME"].lower()
				)
				
				driver1_data = drivers['%s' % (driver1_name)]
				
				driver1 = '{{flagicon|%s}} %s' % (
					driver1_data["country"],
					driver1_data["link"]
				)
			except:
				driver1 = '{{flagicon|%s}} %s %s' % (
					row["DRIVER1_COUNTRY"],
					row["DRIVER1_FIRSTNAME"].capitalize(),
					row["DRIVER1_SECONDNAME"].capitalize()
				)
			
			try:
				driver2_name = '%s %s' % (
					row["DRIVER2_FIRSTNAME"].lower(),
					row["DRIVER2_SECONDNAME"].lower()
				)
				
				driver2_data = drivers['%s' % (driver2_name)]
				
				driver2 = '<br />{{flagicon|%s}} %s' % (
					driver2_data["country"],
					driver2_data["link"]
				)
			except:
				driver2 = '<br />{{flagicon|%s}} %s %s' % (
					row["DRIVER2_COUNTRY"],
					row["DRIVER2_FIRSTNAME"].capitalize(),
					row["DRIVER2_SECONDNAME"].capitalize()
				)
				
			if row["DRIVER3_COUNTRY"] != "":
				try:
					driver3_name = '%s %s' % (
						row["DRIVER3_FIRSTNAME"].lower(),
						row["DRIVER3_SECONDNAME"].lower()
					)
					
					driver3_data = drivers['%s' % (driver3_name)]
					
					driver3 = '<br />{{flagicon|%s}} %s' % (
						driver3_data["country"],
						driver3_data["link"]
					)
				except:
					driver3 = '<br />{{flagicon|%s}} %s %s' % (
						row["DRIVER3_COUNTRY"],
						row["DRIVER3_FIRSTNAME"].capitalize(),
						row["DRIVER3_SECONDNAME"].capitalize()
					)

				print(f'| {driver1 + driver2 + driver3}')
			else:
				print(f'| {driver1 + driver2}')

			if row["TIME"] != "":
				print(f'| {row["TIME"]}')
				
				gap = row["GAP_FIRST"].replace('\'',':')
				
				if line_count > 0:
					if gap.startswith('+'):
						print(f'| {gap}')
					else:
						print(f'| +{gap}')

				elif line_count == 0:
					print('| align="center" | —')

			else:
				print("| colspan=\"2\" align=\"center\" | —")

			print(f'! {position}')

			line_count += 1

		print('|-')
		print('! colspan="8" | Sources:')
		print('|-')
		print('|}')

		print(f'Processed lines: {line_count}')

# Reading data from a .CSV file and printing table for test/free practice results
def print_fp_table(organiser, filename):
	with open(filename, mode='r', encoding='utf-8-sig') as csv_file:
		csv_reader = csv.DictReader(csv_file, delimiter=';')
		line_count = 0
		classes = set()

		print('{| class="wikitable" style="font-size:90%;"')
		print('|-')
		print('! rowspan="5" | Practice Session')
		print('! Class')
		print('! {{Tooltip|No.|Number}}')
		print('! Entrant')
		print('! Time')

		for row in csv_reader:
			if row["CLASS"] not in classes:
				classes.add(row["CLASS"])

				print('|-')
	
				print(f'! {row["CLASS"]}')

				print(f'| align="center" | {row["NUMBER"]}')

				try:
					team_data = teams['#%s %s' % (row["NUMBER"], row["TEAM"])]
					print(f'| {{{{flagicon|{team_data["country"]}}}}} {team_data["link"]}')
				except:
					print(f'| {{{{flagicon|_}}}} {row["TEAM"]}')

				if row["TIME"] != "":
					print(f'| {row["TIME"]}')
				else:
					print(f'|')

			line_count += 1

		print('|- style="border-top:2px solid #808080"')
		print('! colspan="5" | Source:<!--<ref name="PracticeX_Results">{{cite web |title= |url= |website= |access-date= |date= |archive-url= |archive-date= }}</ref>-->')
		print('|-')
		print('|}')

		print(f'Processed lines: {line_count}')

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
		else:
			return text

# Reading what session data the .CSV file contains
def read_session():
	num = 0

	print('Please pick session that data is in given .CSV:')
	print('1. Test/Free practice session')
	print('2. Qualifying')
	print('3. Race')

	while True:
		try:
			num = int(input('Choice: '))
		except ValueError:
			print('Please enter a natural number in 1-3 interval.')

		if num == 1:
			return Session.FP
		elif num == 2:
			return Session.QUALI
		elif num == 3:
			return Session.RACE
		else:
			print('The number must be in 1-3 interval.')

# Reading organiser of the racing event
def read_organiser():
	num = 0

	print('Please enter organiser of the event:')
	print('1. ACO/FIA')
	print('2. IMSA')

	while True:
		try:
			num = int(input('Choice: '))
		except ValueError:
			print('Please enter a natural number in 1-2 interval.')

		if num == 1:
			return Organiser.ACO
		elif num == 2:
			return Organiser.IMSA
		else:
			print('The number must be in 1-2 interval')

def main():
	file = read_csv_path()
	session = read_session()
	organiser = read_organiser()

	if session == Session.FP:
		print_fp_table(organiser, file)
	elif session == Session.QUALI:
		print_quali_table(organiser, file)
	elif session == Session.RACE:
		print_race_table(organiser, file)
	else:
		print('Unsupported session type')

if __name__ == "__main__":
	main()