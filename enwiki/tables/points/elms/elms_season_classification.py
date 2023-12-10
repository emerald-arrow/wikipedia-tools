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

# Dictionary with points system and colouring for tables
points_to_positions = {
		25 : '| style="background:#FFFFBF;" | 1',
	'25PP' : '| style="background:#FFFFBF; font-weight: bold;" | 1',
		18 : '| style="background:#DFDFDF;" | 2',
	'18PP' : '| style="background:#DFDFDF; font-weight: bold;" | 2',
		15 : '| style="background:#FFDF9F;" | 3',
	'15PP' : '| style="background:#FFDF9F; font-weight: bold;" | 3',
		12 : '| style="background:#DFFFDF;" | 4',
	'12PP' : '| style="background:#DFFFDF; font-weight: bold;" | 4',
		10 : '| style="background:#DFFFDF;" | 5',
	'10PP' : '| style="background:#DFFFDF; font-weight: bold;" | 5',
	 	 8 : '| style="background:#DFFFDF;" | 6',
	 '8PP' : '| style="background:#DFFFDF; font-weight: bold;" | 6',
	 	 6 : '| style="background:#DFFFDF;" | 7',
	 '6PP' : '| style="background:#DFFFDF; font-weight: bold;" | 7',
	 	 4 : '| style="background:#DFFFDF;" | 8',
	 '4PP' : '| style="background:#DFFFDF; font-weight: bold;" | 8',
	 	 2 : '| style="background:#DFFFDF;" | 9',
	 '2PP' : '| style="background:#DFFFDF; font-weight: bold;" | 9',
	 	 1 : '| style="background:#DFFFDF;" | 10',
	 '1PP' : '| style="background:#DFFFDF; font-weight: bold;" | 10',
	   0.5 : '| style="background:#DFFFDF;" | >10',
   '0.5PP' : '| style="background:#DFFFDF; font-weight: bold;" | >10',
	 	 0 : '| style="background:#CFCFFF;" |',
	 '0PP' : '| style="background:#CFCFFF; font-weight: bold;" |',
	  'NS' : '| style="background:#CFCFFF;" | NS',
	'NSPP' : '| style="background:#CFCFFF; font-weight: bold;" | NS'
}

# Removes trailing zeros from a Decimal number
def remove_zeros(decimal):
	return (
		decimal.quantize(Decimal(1))
		if decimal == decimal.to_integral()
		else decimal.normalize()
	)

# Colours cells and writes positions based on points
def print_points(points_columns):
	for x in range(len(points_columns)):
		session = points_columns[x]
		if session['race_points_valid_for_net_points'] == True:
			if session['status'] == '':
				suffix = ''
				if session['pole_points'] == 1:
					suffix = 'PP'

				if FULL_POINTS[x] is False:
					doubled = Decimal(session['race_points']) * 2
					doubled = remove_zeros(doubled)
					if suffix == '':
						print("%s" % (points_to_positions[doubled]))
					elif suffix == 'PP':
						print("%s" % (points_to_positions[str(doubled)+'PP']))
				else:
					try:
						if suffix == '':
							print("%s" % (points_to_positions[session['race_points']]))
						elif suffix == 'PP':
							print("%s" % (points_to_positions[str(session['race_points'])+'PP']))
					except KeyError:
						print('NN')

			elif session['status'] == 'not_classified':
				if session['pole_points'] == 1:
					print('%s' % (points_to_positions['NSPP']))
				else:
					print('%s' % (points_to_positions['NS']))
			elif session['status'] == 'did_not_race':
				print('| –')
			else:
				print('|')

# Reads a file and prints table
def read_json(file, value_type):
	with open(file, 'r', encoding='UTF-8') as read_file:
		data = json.load(read_file)

		championship_info = data['championship']

		print('{| class="wikitable" style="font-size:85%; text-align:center;"')
		print('! {{Tooltip|Pos.|Position}}')
		if value_type == ClassificationData.DRIVERS:
			print('! Driver')
		elif value_type == ClassificationData.TEAMS:
			print('! Team')
		else:
			print('!')

		print(f'! colspan="{len(championship_info["sessions"])}" | Rounds')
		print('! Points')
		print('|-')

		for node in data['classification']:
			print('! %i' % (node['position']))

			if value_type == ClassificationData.DRIVERS:
				firstnameFailed = False

				try:
					print('| align="left" | {{flagicon|%s}} [[%s %s]]' % 
						(node['country'], node['driver_first_name'], node['driver_secondname'].capitalize()))
				except:
					firstnameFailed = True

				if firstnameFailed == True:
					try:
						print('| align="left" | {{flagicon|%s}} [[%s %s]]' % 
							(node['country'], node['driver_firstname'], node['driver_secondname'].capitalize()))
					except:
						print('| align="left" | Name Surname')

			elif value_type == ClassificationData.TEAMS:
				try:
					print('| align="left" | {{flagicon|%s}} #%s [[%s]]' %
						(node['nat'], node['key'], node['team']))
				except:
					print('| align="left" | {{flagicon|}} # Team name')

			print_points(node['points_by_session'])

			if type(node['total_points']) is int:
				print(f'! {node["total_points"]}')
			else:
				print(f'! {str(node["total_points"])}')

			print('|-')

		print('|}')

# Reads path to a .json file
def read_json_path():
	text = ''

	while True:
		text = input('Enter path to a .json file downloaded from ELMS website:\n')

		if not os.path.isfile(text):
			print('Invalid path, please try again.')
			continue
		else:
			return text

# Reads type of classification in a .json file
def read_json_type():
	num = 0

	print('Choose classification type in downloaded .json file:')
	print('1. Driver\'s classification')
	print('2. Teams\'s classification')

	while True:
		try:
			num = int(input('Choice (1-2): '))
		except ValueError:
			print('Please enter 1 or 2.')

		if num == 1:
			return ClassificationData.DRIVERS
		elif num == 2:
			return ClassificationData.TEAMS
		else:
			print('The number has to be 1 or 2.')

# Reads whether half points were awarded in any of races
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
			print('Please enter number 1 or 2.')

		if num == 1:
			were_half_points_awarded = True
			break
		elif num == 2:
			break
		else:
			print('Please enter number 1 or 2.')
	
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

# Main function of the script
def main():
	file = read_json_path()
	value_type = read_json_type()

	read_were_half_points_awarded()

	read_json(file, value_type)

# Runs main function
if __name__ == "__main__":
	main()