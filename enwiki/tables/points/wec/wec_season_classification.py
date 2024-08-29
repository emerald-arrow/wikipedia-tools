import sys

# Prevents creating __pycache__ directory
sys.dont_write_bytecode = True

if True:  # noqa: E402
	from enum import Enum
	from bs4 import BeautifulSoup, ResultSet
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
FULL_POINTS: list[bool] = []


# Number of columns before results columns in HTML table start
points_offsets: dict[Classification, int] = {
	Classification.DRIVERS: 3,
	Classification.MANUFACTURERS: 3,
	Classification.TEAMS: 4
}


# Removes trailing zeros from a Decimal number
def remove_zeros(decimal: Decimal) -> Decimal:
	return (
		decimal.quantize(Decimal(1))
		if decimal == decimal.to_integral()
		else decimal.normalize()
	)


# Checks whether given points scale is valid
def validate_scales(scales: list[str]) -> bool:
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
def count_flags(table_row) -> int:
	return str(table_row).count('alt="flag"')


# Extracts classification type from the second row of an HTML table
def read_classification_type_file(html_second_row) -> Classification | None:
	row_string: str = str(html_second_row)

	if re.search('Team', row_string, re.IGNORECASE):
		return Classification.TEAMS
	elif re.search('Manufacturer', row_string, re.IGNORECASE):
		return Classification.MANUFACTURERS
	elif re.search('Driver', row_string, re.IGNORECASE):
		return Classification.DRIVERS
	else:
		return None


# Prints results cell with correct colouring based on scored points
def print_positions(points_columns, points_scales) -> None:
	global FULL_POINTS

	for x in range(0, len(points_columns)):
		points = points_columns[x].find('div', class_='grid-2').find_all('div')
		scale: dict[str, str] = points_to_positions[str(points_scales[x])]
		full_points: bool = FULL_POINTS[x]
		suffix: str = 'PP' if points[1].text.strip() == '1' else ''

		if full_points:
			coloured_position: str = scale[points[0].text.strip() + suffix]
		else:
			doubled: Decimal = Decimal(points[0].text.strip()) * 2
			doubled = remove_zeros(doubled)
			coloured_position: str = scale[str(doubled) + suffix]
		
		print(coloured_position)


# Prints classification table
def print_table(
	data_rows: ResultSet, races_count: int, points_scales: list[str],
	classification_type: Classification
):
	global points_offsets
	points_offset: int = points_offsets[classification_type]

	print("\nTable's code:\n")
	print('{| class="wikitable" style="font-size:85%; text-align:center;"')
	print('! {{Tooltip|Pos.|Position}}')

	if classification_type == Classification.DRIVERS:
		print('! Driver')
	elif classification_type == Classification.TEAMS:
		print('! Car')
		print('! Team')
	elif classification_type == Classification.MANUFACTURERS:
		print('! Manufacturer')

	print(f'! colspan="{races_count}" | Rounds')
	print('! Points')
	print('|-')

	for row in data_rows:
		tds = row.find_all('td')

		position: str = str(tds[0].find('div').text).strip()

		if classification_type == Classification.MANUFACTURERS:
			name: str = str(tds[1].text).strip()
		else:
			name: str = str(tds[1].find('a').text).strip()
		
		if classification_type == Classification.DRIVERS:
			split_name: list[str] = name.split(' ')
			if len(split_name) == 2:
				split_name[1] = split_name[1].capitalize()
				name = f'{split_name[0]} {split_name[1]}'
			elif len(split_name) > 2:
				name = f'{split_name[0]} {' '.join(split_name[1:]).lower()}'

		number: str = str(tds[2].text).strip() if classification_type == Classification.TEAMS else ''
		flag: str = str(tds[3].text).strip() if classification_type == Classification.TEAMS else str(tds[2].text).strip()
		points: str = str(tds[points_offset + races_count].text).strip()

		print('! %s ' % re.sub('[a-z]', '', position))

		if classification_type == Classification.TEAMS:
			if number.startswith('#'):
				number = number[1:]

			print(f'| align="center" | {number}')

		print('| align="left" | {{flagicon|%s}} [[%s]]' % (flag, name))

		print_positions(
			tds[points_offset:points_offset + races_count],
			points_scales
		)

		print(f'! {points}')

		print('|-')
	
	print('|}')


# Reads classification type from user's input
def read_classification_type_input() -> Classification:
	options: list[dict[str, Classification]] = [
		{'name': 'Drivers', 'enum': Classification.DRIVERS},
		{'name': 'Manufacturers', 'enum': Classification.MANUFACTURERS},
		{'name': 'Teams', 'enum': Classification.TEAMS}
	]

	print('Pick classification type in given HTML file:')

	while True:
		try:
			for x in range(0, len(options)):
				print(f'{x+1}. {options[x]["name"]}')
			
			num: int = int(input(f'Choice (1-{len(options)}): ').strip())
		except ValueError:
			print(f'Please enter a natural number from 1-{len(options)} range')
			continue
		
		if num - 1 not in range(0, len(options)):
			print(f'Please enter a natural number from 1-{len(options)} range')
			continue
		else:
			return options[num]['enum']


# Reads whether there's been a race with half points awarded.
def read_were_half_points_awarded(season_races: int) -> None:
	were_half_points_awarded = False

	options: list[dict[str, bool]] = [
		{'option': 'Yes', 'bool': True},
		{'option': 'No', 'bool': False}
	]

	print('Has there been a race with half points awarded?')

	while True:
		try:
			for x in range(0, len(options)):
				print(f'{x+1}. {options[x]["option"]}')

			num: int = int(input('Choice (1-2): ').strip())
		except ValueError:
			print('Please enter 1 or 2.')
			continue

		if num - 1 not in range(0, len(options)):
			print('Please enter 1 or 2.')
			continue
		else:
			were_half_points_awarded = options[num - 1]['bool']
			break
	
	if were_half_points_awarded:
		read_half_points_races(season_races)


# Reads which races had half points awarded
def read_half_points_races(season_races: int) -> None:
	global FULL_POINTS

	num: int = 0

	while True:
		try:
			num = int(input('Please enter the number of races with half points awarded: ').strip())
		except ValueError:
			print('Please enter a natural number.')
			continue
		
		if num <= 0:
			print('Please enter a natural number.')
		else:
			break

	for x in range(1, num + 1):
		while True:
			try:
				race_num: int = int(input(f'Enter the number of {x}. race with half points awarded: ').strip())
			except ValueError:
				print('Please enter a natural number.')
				continue
			
			if race_num <= 0:
				print('Please enter a natural number.')
				continue
			elif race_num > season_races:
				print("Race number can't be bigger than number of races in season.")
				continue
			else:
				FULL_POINTS[race_num - 1] = False
				break


# Reads points scales used in particular rounds
def read_point_scales(races_number: int):
	msg: list[str] = [
		'Please enter points scales in races (1/1.5/2),',
		"enter 0 or dash (-) if race hasn't happened yet."
		'Use spaces to split points scales.'
	]

	print(*msg, sep=' ')

	while True:
		try:
			scales_input: str = input('Points scales: ').strip()
		except ValueError:
			print('Invalid input data.')
			continue
		
		scales: list[str] = scales_input.split(' ')
		if len(scales) != races_number:
			print(f"Number of given points scales ({len(scales)}) isn't equal to number of races in season ({races_number})")
			continue
		
		if validate_scales(scales):
			return scales
		else:
			print("Some of given scales are invalid.")
			continue


# Reads path to the classification .html file
def read_html_path() -> str:
	while True:
		text = input("Enter path to a HTML file downloaded from WEC website:\n")

		if not os.path.isfile(text):
			print('Invalid path, please try again.')
			continue
		if not text.lower().endswith('.html'):
			print("File under given path doesn't have .html extension.")
			continue
		else:
			return text


# Script's main function
def main() -> None:
	global FULL_POINTS

	file_path: str = read_html_path()

	with open(file_path, encoding='utf-8') as file:
		soup: BeautifulSoup = BeautifulSoup(file, 'lxml')
		
		flag_count: int = count_flags(soup.find_all('tr', class_='tr1'))

		for x in range(0, flag_count):
			FULL_POINTS.append(True)

		classification_type: Classification | None = read_classification_type_file(
														soup.find_all('tr', class_='tr2')
													)

		if classification_type is None:
			classification_type = read_classification_type_input()

		points_scales: list[str] = read_point_scales(flag_count)

		read_were_half_points_awarded(flag_count)

		race_data: ResultSet = soup.find_all('tr', class_='tr-data')

		print_table(race_data, flag_count, points_scales, classification_type)


if __name__ == '__main__':
	main()
