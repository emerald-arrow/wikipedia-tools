import sys

# Stopping Python from creating additional catalogues and files during script's execution
sys.dont_write_bytecode = True

from enum import Enum
from bs4 import BeautifulSoup
from decimal import Decimal
from points_system import points_to_positions
import re
import os

# Classification types
class Classification(Enum):
    DRIVERS = 1
    MANUFACTURERS = 2
    TEAMS = 3

# Bool list storing information whether full points were awarded in races
FULL_POINTS = []

# Dictionary storing number of columns before results columns in HTML table
points_offsets = {
	Classification.DRIVERS: 3,
	Classification.MANUFACTURERS: 3,
	Classification.TEAMS: 4
}

# Removes trailing zeros from a Decimal number
def remove_zeros(decimal):
	return (
		decimal.quantize(Decimal(1))
		if decimal == decimal.to_integral()
		else decimal.normalize()
	)

# Checks whether given points scale is valid
def validate_scales(scales):
	for x in range(0, len(scales)):
		if scales[x] not in points_to_positions.keys():
			if ',' not in scales[x]:
				print(f'{scales[x]} scale is invalid')
				return False
			else:
				comma_convert = scales[x].replace(',', '.')
				if comma_convert not in points_to_positions.keys():
					print(f'{scales[x]} is invalid')
					return False
				else:
					scales[x] = comma_convert
	
	return True

# Counts number of flags in the first row of a table (therefore - number of races)
def count_flags(table_row):
	return str(table_row).count('alt="flag"')

# Extracts classification type from the second row of a HTML table
def read_classification_type_file(html_second_row):
	row_string = str(html_second_row)

	if re.search('Team', row_string):
		return Classification.TEAMS
	elif re.search('Manufacturer', row_string):
		return Classification.MANUFACTURERS
	elif re.search('Driver', row_string):
		return Classification.DRIVERS
	else:
		print('Could not find what type of classification is in the file.')

# Colours cells and writes positions based on points
def print_positions(points_columns, points_scales):
	global FULL_POINTS

	for x in range(0, len(points_columns)):
		points = points_columns[x].find('div', class_='grid-2').find_all('div')
		scale = points_to_positions[str(points_scales[x])]
		full_points = FULL_POINTS[x]
		suffix = 'PP' if points[1].text.strip() == "1" else ""
		coloured_position = ''

		if full_points:
			coloured_position = scale[points[0].text.strip() + suffix]
		else:
			doubled = Decimal(points[0].text.strip()) * 2
			doubled = remove_zeros(doubled)
			coloured_position = scale[str(doubled) + suffix]
		
		print(coloured_position)

# Prints classification table
def print_table(data_rows, races_count, points_scales, classification_type):
	global points_offsets
	points_offset = points_offsets[classification_type]

	print('{| class="wikitable" style="font-size:85%; text-align:center;"')
	print('! {{Tooltip|Pos.|Position}}')

	if classification_type == Classification.DRIVERS:
		print('! Driver')
	elif classification_type == Classification.TEAMS:
		print('! Team')
	elif classification_type == Classification.MANUFACTURERS:
		print('! Manufacturer')

	print(f'! colspan="{races_count}" | Rounds')
	print('! Points')
	print('|-')

	for row in data_rows:
		tds = row.find_all('td')

		position = str(tds[0].find('div').text).strip()
		name = str(tds[1].text).strip() if classification_type == Classification.MANUFACTURERS else str(tds[1].find('a').text).strip()
		
		if classification_type == Classification.DRIVERS:
			split = name.split(' ')
			if len(split) == 2:
				split[1] = split[1].capitalize()
				name = split[0] + ' ' + split[1]
			elif len(split) > 2:
				name = split[0] + ' ' + ' '.join(split[1:]).lower()

		number = str(tds[2].text).strip() if classification_type == Classification.TEAMS else ''
		flag = str(tds[3].text).strip() if classification_type == Classification.TEAMS else str(tds[2].text).strip()
		points = str(tds[points_offset + races_count].text).strip()

		print('! %s ' % re.sub('[a-z]', '', position))
        
		if classification_type == Classification.TEAMS:
			print('| align="left" | {{flagicon|%s}} %s [[%s]]' % (flag, number, name))
		else:
			print('| align="left" | {{flagicon|%s}} [[%s]]' % (flag, name))

		print_positions(
			tds[points_offset:points_offset + races_count],
			points_scales
		)

		print(f'! {points}')

		print('|-')
	
	print('|}')

# Reads classification type from user's input
def read_classification_type_input():
	num = 0

	print('Pick classification type in given HTML file:')

	while True:
		try:
			print('1. Drivers')
			print('2. Teams')
			print('3. Manufacturers')
			
			num = int(input('Choice (1-3): '))
		except ValueError:
			print('Please enter a natural number in 1-3 range.')

		if num == 1:
			return Classification.DRIVERS
		elif num == 2:
			return Classification.TEAMS
		elif num == 3:
			return Classification.MANUFACTURERS
		else:
			print('The number has to be in 1-3 range')

# Reads whether there was a race with half points awarded.
def read_were_half_points_awarded():
	num = 0
	were_half_points_awarded = False

	print('Was there a race with half points awarded?')
	print('1. Yes')
	print('2. No')

	while True:
		try:
			num = int(input('Choice (1-2): '))
		except ValueError:
			print('Please enter a natural number in 1-2 range')

		if num == 1:
			were_half_points_awarded = True
			break
		elif num == 2:
			break
		else:
			print('The number has to be in 1-2 range')
	
	if were_half_points_awarded is True:
		read_half_points_races()

# Reads which races had half points awarded
def read_half_points_races():
	global FULL_POINTS

	num = 0
	races = 0

	while True:
		try:
			num = int(input('Enter the number of races with half points awarded: '))
		except ValueError:
			print('Please enter a natural number.')
		
		if num <= 0:
			print('Please enter a natural number.')
		else:
			races = num
			break

	for x in range(1, races + 1):
		race_num = 0
		
		while True:
			try:
				race_num = int(input(f'Enter the number of {x}. race with half points awarded: '))
			except ValueError:
				print('Please enter a natural number.')
			
			if race_num <= 0:
				print('Please enter a natural number.')
			else:
				FULL_POINTS[race_num - 1] = False
				break

# Reads point scales used in particular rounds
def read_point_scales(races_number):
	scales_input = ''
	scales = []

	while True:
		try:
			scales_input = input('Enter points scales used in races, separate each number by a space: ')
		except ValueError:
			print('Invalid input data')
		
		scales = scales_input.split(' ')
		if len(scales) != races_number:
			print(f'Number of given points scales ({len(scales)}) is not equal to number of races ({races_number})')
			continue
		
		if validate_scales(scales):
			break

	return scales

# Reads path to the file
def read_json_path():
	text = ''

	while True:
		text = input('Enter path to a HTML file downloaded from WEC\'s website:\n')

		if not os.path.isfile(text):
			print('Invalid path, please try again.')
			continue
		else:
			return text

# Main function of the script
def main():
	global FULL_POINTS

	file_path = read_json_path()

	with open(file_path, encoding='utf-8') as file:
		soup = BeautifulSoup(file, 'lxml')
		
		flag_count = count_flags(soup.find_all('tr', class_='tr1'))

		for x in range(0, flag_count):
			FULL_POINTS.append(True)

		classification_type = None

		classification_type = read_classification_type_file(soup.find_all('tr', class_='tr2'))

		if classification_type is None:
			classification_type = read_classification_type_input()

		points_scales = read_point_scales(flag_count)

		read_were_half_points_awarded()

		race_data = soup.find_all('tr', class_='tr-data')

		print_table(race_data, flag_count, points_scales, classification_type)

if __name__ == '__main__':
    main()