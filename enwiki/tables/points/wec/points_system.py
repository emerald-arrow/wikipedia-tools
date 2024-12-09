# WEC points system from 2022 onwards with Wikipedia's table colouring
# 0 or dash (-) results in printing empty cell
points_to_positions: dict[str, dict[str, str]] = {
	'-': {
		'0': '| '
	},
	'0': {
		'0': '| '
	},
	'1': {
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
		'0': '| style="background:#CFCFFF;" | >10',
		'0PP': '| style="background:#CFCFFF; font-weight: bold;" | >10',
		'NS': '| style="background:#CFCFFF;" | NC',
		'NSPP': '| style="background:#CFCFFF; font-weight: bold;" | NC'
	},
	'1.5': {
		'38': '| style="background:#FFFFBF;" | 1',
		'38PP': '| style="background:#FFFFBF; font-weight: bold;" | 1',
		'27': '| style="background:#DFDFDF;" | 2',
		'27PP': '| style="background:#DFDFDF; font-weight: bold;" | 2',
		'23': '| style="background:#FFDF9F;" | 3',
		'23PP': '| style="background:#FFDF9F; font-weight: bold;" | 3',
		'18': '| style="background:#DFFFDF;" | 4',
		'18PP': '| style="background:#DFFFDF; font-weight: bold;" | 4',
		'15': '| style="background:#DFFFDF;" | 5',
		'15PP': '| style="background:#DFFFDF; font-weight: bold;" | 5',
		'12': '| style="background:#DFFFDF;" | 6',
		'12PP': '| style="background:#DFFFDF; font-weight: bold;" | 6',
		'9': '| style="background:#DFFFDF;" | 7',
		'9PP': '| style="background:#DFFFDF; font-weight: bold;" | 7',
		'6': '| style="background:#DFFFDF;" | 8',
		'6PP': '| style="background:#DFFFDF; font-weight: bold;" | 8',
		'3': '| style="background:#DFFFDF;" | 9',
		'3PP': '| style="background:#DFFFDF; font-weight: bold;" | 9',
		'2': '| style="background:#DFFFDF;" | 10',
		'2PP': '| style="background:#DFFFDF; font-weight: bold;" | 10',
		'0': '| style="background:#CFCFFF;" | >10',
		'0PP': '| style="background:#CFCFFF; font-weight: bold;" | >10',
		'NS': '| style="background:#CFCFFF;" | NC',
		'NSPP': '| style="background:#CFCFFF; font-weight: bold;" | NC'
	},
	'2': {
		'50': '| style="background:#FFFFBF;" | 1',
		'50PP': '| style="background:#FFFFBF; font-weight: bold;" | 1',
		'36': '| style="background:#DFDFDF;" | 2',
		'36PP': '| style="background:#DFDFDF; font-weight: bold;" | 2',
		'30': '| style="background:#FFDF9F;" | 3',
		'30PP': '| style="background:#FFDF9F; font-weight: bold;" | 3',
		'24': '| style="background:#DFFFDF;" | 4',
		'24PP': '| style="background:#DFFFDF; font-weight: bold;" | 4',
		'20': '| style="background:#DFFFDF;" | 5',
		'20PP': '| style="background:#DFFFDF; font-weight: bold;" | 5',
		'16': '| style="background:#DFFFDF;" | 6',
		'16PP': '| style="background:#DFFFDF; font-weight: bold;" | 6',
		'12': '| style="background:#DFFFDF;" | 7',
		'12PP': '| style="background:#DFFFDF; font-weight: bold;" | 7',
		'8': '| style="background:#DFFFDF;" | 8',
		'8PP': '| style="background:#DFFFDF; font-weight: bold;" | 8',
		'4': '| style="background:#DFFFDF;" | 9',
		'4PP': '| style="background:#DFFFDF; font-weight: bold;" | 9',
		'2': '| style="background:#DFFFDF;" | 10',
		'2PP': '| style="background:#DFFFDF; font-weight: bold;" | 10',
		'0': '| style="background:#CFCFFF;" | >10',
		'0PP': '| style="background:#CFCFFF; font-weight: bold;" | >10',
		'NS': '| style="background:#CFCFFF;" | NC',
		'NSPP': '| style="background:#CFCFFF; font-weight: bold;" | NC'
	}
}