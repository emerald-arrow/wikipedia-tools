import sys

# Prevents creating __pycache__ directory
sys.dont_write_bytecode = True

if True:  # noqa: E402
	import os
	import json
	from decimal import Decimal
	from enum import Enum


# Classification types
class ClassificationData(Enum):
	DRIVERS = 1
	TEAMS = 2


# Table containing bools regarding whether full points were awarded in races.
# There is a maximum of 6 ELMS races per season.
FULL_POINTS = [True, True, True, True, True, True]

# Points system with correct colouring for tables
points_to_positions: dict[str, str] = {
	'25': '| style="background:#FFFFBF;" | 1',
	'25PP': '| style="background:#FFFFBF; font-weight: bold;" | 1',
	'18': '| style="background:#DFDFDF;" | 2',
	'18PP': '| style="background:#DFDFDF; font-weight: bold;" | 2',
	'15': '| style="background:#FFDF9F;" | 3',
	'15PP': '| style="background:#FFDF9F; font-weight: bold;" | 3',
	'12': '| style="background:#DFFFDF;" | 4',
	'12PP': '| style="background:#DFFFDF; font-weight: bold;" | 4',
	'10': '| style="background:#DFFFDF;" | 5',
	'10PP': '| style="background:#DFFFDF; font-weight: bold;" | 5',
	'8': '| style="background:#DFFFDF;" | 6',
	'8PP': '| style="background:#DFFFDF; font-weight: bold;" | 6',
	'6': '| style="background:#DFFFDF;" | 7',
	'6PP': '| style="background:#DFFFDF; font-weight: bold;" | 7',
	'4': '| style="background:#DFFFDF;" | 8',
	'4PP': '| style="background:#DFFFDF; font-weight: bold;" | 8',
	'2': '| style="background:#DFFFDF;" | 9',
	'2PP': '| style="background:#DFFFDF; font-weight: bold;" | 9',
	'1': '| style="background:#DFFFDF;" | 10',
	'1PP': '| style="background:#DFFFDF; font-weight: bold;" | 10',
	'0.5': '| style="background:#DFFFDF;" | >10',
	'0.5PP': '| style="background:#DFFFDF; font-weight: bold;" | >10',
	'0': '| style="background:#CFCFFF;" |',
	'0PP': '| style="background:#CFCFFF; font-weight: bold;" |',
	'NC': '| style="background:#CFCFFF;" | NC',
	'NCPP': '| style="background:#CFCFFF; font-weight: bold;" | NC'
}


# Removes trailing zeros from a Decimal number
def remove_zeros(decimal: Decimal) -> Decimal:
	return (
		decimal.quantize(Decimal(1))
		if decimal == decimal.to_integral()
		else decimal.normalize()
	)


# Colours cells and writes positions based on points
def print_points(points_columns) -> None:
	for x in range(len(points_columns)):
		session = points_columns[x]
		if session['race_points_valid_for_net_points']:
			if session['status'] == '':
				suffix: str = ''
				if session['pole_points'] == 1:
					suffix = 'PP'

				if FULL_POINTS[x] is False:
					doubled: Decimal = Decimal(session['race_points']) * 2
					doubled = remove_zeros(doubled)

					print(points_to_positions[str(doubled) + suffix])
				else:
					try:
						print(points_to_positions[str(session['race_points']) + suffix])
					except KeyError:
						print(' ')

			elif session['status'] == 'not_classified':
				nc_suffix: str = ''

				if session['pole_points'] == 1:
					nc_suffix = 'PP'

				print(points_to_positions['NC' + nc_suffix])
			elif session['status'] == 'did_not_race':
				print('| –')
			else:
				print('|')
		else:
			print('|')


# Reads a .json file and prints classification table
def read_json(file_path: str, value_type: ClassificationData):
	with open(file_path, 'r', encoding='UTF-8') as read_file:
		data = json.load(read_file)

		championship_info = data['championship']

		print('{| class="wikitable" style="font-size:85%; text-align:center;"')
		print('! {{Tooltip|Pos.|Position}}')

		if value_type == ClassificationData.DRIVERS:
			print('! Driver')
		elif value_type == ClassificationData.TEAMS:
			print('! Car')
			print('! Team')

		print(f'! colspan="{len(championship_info["sessions"])}" | Rounds')
		print('! Points',)
		print('|-')

		for node in data['classification']:  # type: dict
			print('! %i' % (node['position']))

			if value_type == ClassificationData.DRIVERS:
				if node.get('driver_first_name') is not None:
					firstname: str = node.get('driver_first_name')
				elif node.get('driver_firstname') is not None:
					firstname: str = node.get('driver_firstname')
				else:
					firstname: str = ''

				if firstname != '':
					print('| align="left" | {{{{flagicon|{flag}}}}} [[{firstname} {lastname}]]'.format(
						flag=node['country'],
						firstname=firstname,
						lastname=node['driver_secondname'].capitalize()
					))
				else:
					print('| align="left" | ')

			elif value_type == ClassificationData.TEAMS:
				try:
					print('| align="center" | {number}'.format(
						number=node['key']
					))
					print('| align="left" | {{{{flagicon|{flag}}}}} [[{team}]]'.format(
						flag=node['nat'],
						team=node['team']
					))
				except KeyError:
					print('| align="left" | ')

			print_points(node['points_by_session'])

			if type(node['total_points']) is int:
				print(f'! {node["total_points"]}')
			else:
				print(node["total_points"])

			print('|-')

		print('|}')


# Reads path to a .json results file
def read_json_path() -> str:
	while True:
		text: str = input('Enter path to a .json file downloaded from ELMS website:\n').strip()

		if not os.path.isfile(text):
			print('Invalid path, please try again.')
			continue
		if not text.lower().endswith('.json'):
			print("File under given path doesn't have .json extension, please try again.")
			continue
		else:
			return text


# Reads type of classification in results file
def read_data_type() -> ClassificationData:
	print('Choose classification type in downloaded .json file:')

	while True:
		print("1. Drivers' classification")
		print("2. Teams' classification")

		try:
			num: int = int(input('Choice (1-2): ').strip())
		except ValueError:
			print('Please enter number 1 or 2.')
			continue

		if num == 1:
			return ClassificationData.DRIVERS
		elif num == 2:
			return ClassificationData.TEAMS
		else:
			print('Please enter number 1 or 2.')
			continue


# Reads whether half points were awarded in any of races
def read_were_half_points_awarded() -> None:
	were_half_points_awarded = False

	print('Has there been a race with half points awarded?')

	while True:
		print('1. Yes')
		print('2. No')

		try:
			num: int = int(input('Choice (1-2): ').strip())
		except ValueError:
			print('Please enter number 1 or 2.')
			continue

		if num == 1:
			were_half_points_awarded = True
			break
		elif num == 2:
			break
		else:
			print('Please enter number 1 or 2.')
			continue

	if were_half_points_awarded:
		read_half_points_races()


# Reads which races had half points awarded
def read_half_points_races():
	global FULL_POINTS

	num: int = 0

	while True:
		try:
			num = int(input('Please enter the number of races with half points awarded: ').strip())
		except ValueError:
			print('Please enter a natural number')
			continue

		if num <= 0:
			print('Please enter a natural number')
			continue
		else:
			break

	for x in range(1, num + 1):
		while True:
			try:
				race_num: int = int(input(f'Please enter the number of {x}. race with half points awarded: '))
			except ValueError:
				print('Please enter a natural number')
				continue

			if race_num <= 0:
				print('Please enter a natural number')
				continue
			else:
				FULL_POINTS[race_num - 1] = False
				break


# Script's main function
def main() -> None:
	json_path: str = read_json_path()

	data_type: ClassificationData = read_data_type()

	read_were_half_points_awarded()

	read_json(json_path, data_type)


if __name__ == "__main__":
	main()
