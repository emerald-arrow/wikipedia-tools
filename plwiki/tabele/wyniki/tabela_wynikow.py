import sys

# Powstrzymanie Pythona od tworzenia dodatkowych plików i katalogów przy wykonywaniu skryptu
sys.dont_write_bytecode = True

import os
import csv
from enum import Enum
from db import cars
from db import drivers
from db import teams

# Typy sesji
class Session(Enum):
	FP = 1
	QUALI = 2
	RACE = 3

# Organizatorzy
class Organiser(Enum):
	ACO = 1
	IMSA = 2

# Odczyanie pliku .CSV i wypisanie kodu tabeli dla wyników wyścigu
def print_race_table(organiser, filename):
	with open(filename, mode='r', encoding='utf-8-sig') as csv_file:
		csv_reader = csv.DictReader(csv_file, delimiter=';')
		line_count = 0
		class_winners = set()

		print('{| class="wikitable" style="font-size:95%;"')
		print('|+ Klasyfikacja<ref>{{Cytuj | url =  | tytuł =  | data =  | opublikowany =  | język = en | data dostępu =  | archiwum =  | zarchiwizowano = }}</ref>')
		print('! {{Tooltip|Poz.|Pozycja}}')
		print('! Klasa')
		print('! Zespół')
		print('! Kierowcy')
		print('! Samochód')
		print('! Opony')
		print('! {{Tooltip|Okr.|Okrążenia}}')
		print('! Czas/Strata')

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
				print(f'| {{{{Flaga|{team_data["country"]}}}}} {team_data["link"]}')
			except KeyError:
				print(f'| {{{{Flaga|}}}} #{row["NUMBER"]} [[{row["TEAM"]}]]')

			try:
				driver1_data = None
				if organiser == Organiser.ACO:
					driver1_data = drivers[row["DRIVER_1"].lower()]
				elif organiser == Organiser.IMSA:
					driver1_name = row["DRIVER1_FIRSTNAME"] + " " + row["DRIVER1_SECONDNAME"]
					driver1_data = drivers[driver1_name.lower()]

				driver1 = '{{Flaga|%s}} %s' % (
					driver1_data["country"],
					driver1_data["link"]
				)
			except KeyError:
				driver1_name = None
				if organiser == Organiser.ACO:
					driver1_name = row["DRIVER_1"].split(" ", 1)
				elif organiser == Organiser.IMSA:
					driver1_name = [row["DRIVER1_FIRSTNAME"], row["DRIVER1_SECONDNAME"]]

				driver1 = '{{Flaga|}} [[%s %s]]' % (
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

				driver2 = '<br />{{Flaga|%s}} %s' % (
					driver2_data["country"],
					driver2_data["link"]
				)
			except KeyError:
				driver2_name = None
				if organiser == Organiser.ACO:
					driver2_name = row["DRIVER_2"].split(" ", 1)
				elif organiser == Organiser.IMSA:
					driver2_name = [row["DRIVER2_FIRSTNAME"], row["DRIVER2_SECONDNAME"]]

				driver2 = '<br />{{Flaga|}} [[%s %s]]' % (
					driver2_name[0],
					driver2_name[1].capitalize()
				)

			if organiser == Organiser.ACO and row["DRIVER_3"] != "":
				try:
					driver3_data = drivers[row["DRIVER_3"].lower()]
					driver3 = '<br />{{Flaga|%s}} %s' % (
						driver3_data["country"],
						driver3_data["link"]
					)
				except KeyError:
					driver3_name = row["DRIVER_3"].split(" ", 1)
					driver3 = '<br />{{Flaga|}} [[%s %s]]' % (
						driver3_name[0],
						driver3_name[1].capitalize()
					)
					
				print(f'| {driver1 + driver2 + driver3}')
			elif organiser == Organiser.IMSA and row["DRIVER3_FIRSTNAME"] != "":
				try:
					driver3_name = row["DRIVER3_FIRSTNAME"] + " " + row["DRIVER3_SECONDNAME"]
					driver3_data = drivers[driver3_name.lower()]
					driver3 = '<br />{{Flaga|%s}} %s' % (
						driver3_data["country"],
						driver3_data["link"]
					)
				except KeyError:
					driver3 = '<br />{{Flaga|}} [[%s %s]]' % (
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

			if organiser == Organiser.ACO:
				tyres = '{{Opony|%s}}' % (row["TYRES"])
			elif organiser == Organiser.IMSA:
				tyres = '{{Opony|%s}}' % (row["TIRES"])

			print(f'| align="center" | {tyres}')

			print(f'| align="center" | {row["LAPS"]}')
			
			if row["STATUS"] == 'Classified':
				if line_count > 0:
					gap = row["GAP_FIRST"].replace('.',',').replace('\'',':')

					if gap.startswith("+"):
						print(f'| {gap}')
					else:
						print(f'| +{gap}')

				elif line_count == 0:
					total_time = row["TOTAL_TIME"].replace('.',',').replace('\'',':')
					print(f'| align="center" | {total_time}')
			else:
				print(f'| {row["STATUS"]}')

			line_count += 1
		
		print('|-')
		print('|}')

		print(f'Przetworzone linie: {line_count}')

# Odczyanie pliku .CSV i wypisanie kodu tabeli dla wyników kwalifikacji
def print_quali_table(organiser, filename):
	with open(filename, mode='r', encoding='utf-8-sig') as csv_file:
		csv_reader = csv.DictReader(csv_file, delimiter=';')
		line_count = 0
		class_polesitters = set()

		print('{| class="wikitable sortable" style="font-size: 90%;"')
		print('! {{Tooltip|Poz.|Pozycja}}')
		print('! class="unsortable" | Klasa')
		print('! class="unsortable" | Zespół')
		print('! class="unsortable" | Kierowca')
		print('! class="unsortable" | Czas')
		print('! class="unsortable" | Strata')
		print('! {{Tooltip|Poz. s.|Pozycja startowa}}')

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

			try:
				teams_data = teams['#%s %s' % (row["NUMBER"], row["TEAM"])]
				print(f'| {{{{Flaga|{teams_data["country"]}}}}} {teams_data["link"]}')
			except:
				print(f'| {{{{Flaga|}}}} #{row["NUMBER"]} [[{row["TEAM"]}]]')

			try:
				driver1_name = '%s %s' % (
					row["DRIVER1_FIRSTNAME"].lower(),
					row["DRIVER1_SECONDNAME"].lower()
				)
				
				driver1_data = drivers['%s' % (driver1_name)]
				
				driver1 = '{{Flaga|%s}} %s' % (
					driver1_data["country"],
					driver1_data["link"]
				)
			except:
				driver1 = '{{Flaga|%s}} %s %s' % (
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
				
				driver2 = '<br />{{Flaga|%s}} %s' % (
					driver2_data["country"],
					driver2_data["link"]
				)
			except:
				driver2 = '<br />{{Flaga|%s}} %s %s' % (
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
					
					driver3 = '<br />{{Flaga|%s}} %s' % (
						driver3_data["country"],
						driver3_data["link"]
					)
				except:
					driver3 = '<br />{{Flaga|%s}} %s %s' % (
						row["DRIVER3_COUNTRY"],
						row["DRIVER3_FIRSTNAME"].capitalize(),
						row["DRIVER3_SECONDNAME"].capitalize()
					)

				print(f'| {driver1 + driver2 + driver3}')
			else:
				print(f'| {driver1 + driver2}')

			if row["TIME"] != "":
				time = row["TIME"].replace('.',',')
				print(f'| {time}')
				
				gap = row["GAP_FIRST"].replace('.',',').replace('\'',':')
				
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
		print('! colspan="7" | Źródła<ref>{{Cytuj | url =  | tytuł =  | data =  | opublikowany =  | język = en | data dostępu =  | archiwum =  | zarchiwizowano = }}</ref><ref>{{Cytuj | url =  | tytuł =  | data =  | opublikowany = fiawec.alkamelsystems.com | język = en | data dostępu =  | archiwum =  | zarchiwizowano = }}</ref>')
		print('|-')
		print('|}')

		print(f'Przetworzone linie: {line_count}')

# Odczyanie pliku .CSV i wypisanie kodu fragmentu tabeli dla wyników sesji treningowych
def print_fp_table(organiser, filename):
	with open(filename, mode='r', encoding='utf-8-sig') as csv_file:
		csv_reader = csv.DictReader(csv_file, delimiter=';')
		line_count = 0
		classes = set()

		print('{| class="wikitable" style="font-size:95%"')
		print('|-')
		print('! Klasa')
		print('! Zespół')
		print('! Samochód')
		print('! Czas')
		print('! {{Tooltip|Okr.|Liczba pokonanych okrążeń}}')
		print('|-')
		print('! colspan="5" | Sesja<!--<ref>{{Cytuj | url =  | tytuł =  | data =  | opublikowany =  | język = en | data dostępu =  | archiwum =  | zarchiwizowano = }}</ref>-->')

		for row in csv_reader:
			if row["CLASS"] not in classes:
				classes.add(row["CLASS"])

				print('|-')
	
				print(f'! {row["CLASS"]}')

				try:
					teams_data = teams['#%s %s' % (row["NUMBER"], row["TEAM"])]
					print(f'| {{{{Flaga|{teams_data["country"]}}}}} {teams_data["link"]}')
				except:
					print(f'| #{row["NUMBER"]} [[{row["TEAM"]}]]')

				try:
					car = cars[row["VEHICLE"]]
				except KeyError:
					car = '%s' % (row["VEHICLE"])

				print(f'| {car}')

				if row["TIME"] != "":
					time = row["TIME"].replace('.',',')
					print(f'| {time}')
				else:
					print(f'|')

				print(f'| align="center" | {row[" LAPS"]}')

			line_count += 1
		
		print('|-')
		print('|}')

		print(f'Przetworzone linie: {line_count}')

# Odczytanie ścieżki do pliku
def read_csv_path():
	text = ''

	while True:
		text = input('Podaj ścieżkę do pliku .CSV pobranego ze strony Alkamelsystems:\n')

		if not os.path.isfile(text):
			print('Ścieżka nieprawidłowa, spróbuj ponownie.')
			continue
		if not text.lower().endswith('.csv'):
			print('Ścieżka nie prowadzi do pliku z rozszerzeniem .CSV.')
			continue
		else:
			return text

# Odczytanie sesji której wyniki zawiera plik
def read_session():
	num = 0

	print('Wybierz sesję, która jest w podanym pliku .CSV:')
	print('1. Treningowa/testowa')
	print('2. Kwalifikacyjna')
	print('3. Wyścig')

	while True:
		try:
			num = int(input('Wybór: '))
		except ValueError:
			print('Podaj liczbę naturalną z przedziału 1-3')

		if num == 1:
			return Session.FP
		elif num == 2:
			return Session.QUALI
		elif num == 3:
			return Session.RACE
		else:
			print('Liczba musi być w przedziale 1-3')

# Odczytanie organizatora wyścigu, różni organizatorzy mogą inaczej nazywać kolumny w plikach .CSV
def read_organiser():
	num = 0

	print('Podaj organizatora wyścigu:')
	print('1. ACO/FIA')
	print('2. IMSA')

	while True:
		try:
			num = int(input('Wybór: '))
		except ValueError:
			print('Podaj liczbę naturalną z przedziału 1-2')

		if num == 1:
			return Organiser.ACO
		elif num == 2:
			return Organiser.IMSA
		else:
			print('Liczba musi być w przedziale 1-2')

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
		print('Typ sesji nieobsługiwany')

if __name__ == "__main__":
	main()