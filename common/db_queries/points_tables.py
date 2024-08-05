import sys

# Prevents creating __pycache__ directory
sys.dont_write_bytecode = True

if True:  # noqa: E402
	from sqlite3 import Connection
	from common.db_connect import db_connection
	from common.models.sessions import DbSession
	from common.models.styles import Style, StyledStatus, StyledPosition, LocalisedAbbreviation


# Gets points scales of championship under given id
def get_points_scales(championship_id: int) -> list[float] | None:
	db: Connection | None = db_connection()

	if db is None:
		print("Couldn't connect to the database.")
		return None

	with db:
		query = '''
			SELECT DISTINCT points_scale
			FROM points_system
			WHERE championship_id = :ch_id;
		'''
		params = {'ch_id': championship_id}

		result = db.execute(query, params).fetchall()

		points_scales = list()

		if len(result) > 0:
			for r in result:
				points_scales.append(float(r[0]))

		return points_scales


# Gets sessions that award points in points system
def get_scoring_sessions(championship_id: int, scale: float) -> list[DbSession] | None:
	db: Connection | None = db_connection()

	if db is None:
		print("Couldn't connect to the database.")
		return None

	with db:
		query = '''
			SELECT DISTINCT session_id, s.name
			FROM points_system ps
			JOIN "session" s
			ON ps.session_id = s.id
			WHERE championship_id = :ch_id
			AND points_scale = :scale;
		'''
		params = {'ch_id': championship_id, 'scale': scale}

		result = db.execute(query, params).fetchall()

		sessions: list[DbSession] = list()

		if len(result) > 0:
			for res in result:
				sessions.append(
					DbSession(
						db_id=int(res[0]),
						name=res[1]
					)
				)

		return sessions


# Gets Wikipedia table-styled nonscoring statuses (retired, not classified, etc.)
def get_styled_nonscoring_statuses() -> list[StyledStatus] | None:
	db: Connection | None = db_connection()

	if db is None:
		print("Couldn't connect to the database.")
		return

	with db:
		styled_statuses: list[StyledStatus] = list()

		query = '''
			SELECT status, background_hex, text_colour_hex, bold, id
			FROM result_styling
			WHERE status != "Classified, scoring"
			AND status != "P1"
			AND status != "P2"
			AND status != "P3"
			AND status != "PP";
		'''

		result = db.execute(query).fetchall()

		if len(result) > 0:
			for res in result:
				styled_statuses.append(
					StyledStatus(
						status=res[0],
						style=Style(
							db_id=int(res[4]),
							background=res[1],
							text=res[2],
							bold=bool(res[3])
						)
					)
				)

		return styled_statuses


# Gets styled points system
def get_styled_points_system(championship_id: int, scale: float, session_id: int) -> list[StyledPosition] | None:
	db: Connection | None = db_connection()

	if db is None:
		print("Couldn't connect to the database.")
		return

	with db:
		points_system: list[StyledPosition] = list()

		query = '''
			SELECT ps.place, ps.points, rs.background_hex, rs.text_colour_hex, rs.bold, ps.id, rs.id 
			FROM points_system ps
			JOIN result_styling rs
			ON rs.id = ps.result_style_id
			WHERE championship_id = :champ_id
			AND points_scale = :scale
			AND session_id = :s_id
		'''
		params = {
			'champ_id': championship_id,
			'scale': scale,
			's_id': session_id
		}

		result = db.execute(query, params).fetchall()

		if len(result) > 0:
			for res in result:
				points_system.append(
					StyledPosition(
						db_id=int(res[5]),
						position=int(res[0]),
						points=float(res[1]),
						style=Style(
							db_id=int(res[6]),
							background=res[2],
							text=res[3] if type(res[3]) is str else None,
							bold=bool(res[4])
						)
					)
				)

		return points_system


# Gets localised abbreviations of nonscoring statuses
def get_nonscoring_abbreviations(wiki_id: int) -> list[LocalisedAbbreviation] | None:
	db: Connection | None = db_connection()

	if db is None:
		print("Couldn't connect to the database.")
		return

	with db:
		query = '''
			SELECT rs.status, ls.code 
			FROM localised_status ls
			JOIN result_styling rs
			ON rs.id = ls.style_id
			WHERE ls.wikipedia_id = :wiki;
		'''
		params = {
			'wiki': wiki_id
		}

		result = db.execute(query, params).fetchall()

		abbreviations: list[LocalisedAbbreviation] = list()

		if len(result) > 0:
			for res in result:
				abbreviations.append(
					LocalisedAbbreviation(
						status=res[0],
						abbr=res[1]
					)
				)

		return abbreviations


# Gets number of races held in given classification
def get_races_held(classification_id: int) -> int | None:
	db: Connection | None = db_connection()

	if db is None:
		print("Couldn't connect to the database.")
		return

	with db:
		query = '''
			SELECT MAX(round_number)
			FROM score
			WHERE classification_id = :cl_id;
		'''

		result = db.execute(query, {'cl_id': classification_id}).fetchone()

		return -1 if result[0] is None else int(result[0])
