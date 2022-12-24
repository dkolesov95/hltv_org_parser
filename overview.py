import time
from requests_html import HTMLSession
from pymongo import MongoClient
from fake_useragent import UserAgent


def round_decode(src):
	src = src.split('/')[-1].replace('.svg', '')
	if src in ['bomb_defused', 'ct_win', 'stopwatch']:
		return 'ct', src
	elif src in ['bomb_exploded', 't_win']:
		return 't', src
	else:
		return '', src
		print('ERROR round_decode', src)


def round_history(round_history_team, team):
	team_name = round_history_team.find('.round-history-team', first=True).attrs['title']

	halfs = round_history_team.find('.round-history-half')
	tmp = []
	for index_h, h in enumerate(halfs):
		rounds = h.find('.round-history-outcome')
		for index_r, r in enumerate(rounds):
			title = r.attrs['title']
			src = r.attrs['src']
			side, round_end = round_decode(src)
			tmp.append({
				'round': index_r+1,
				'half': index_h+1,
				f'team{team}': team_name,
				f'result{team}': 1 if title else 0,
				f'side{team}': side,
				f'round_end{team}': round_end,
			})
	return tmp


def main(session, headers, main_page):
	# print('overview', main_page['url'])

	tmp = []
	for index, mi in enumerate(main_page['maps_info']):
		print('overview', mi['stats_url'])
		url = 'https://www.hltv.org' + mi['stats_url']
		request = session.get(url, headers=headers)

		round_history_teams = request.html.find('.round-history-con', first=True)

		try:
			team1, team2 = round_history_teams.find('.round-history-team-row')
		except:
			continue

		round_history_team1 = round_history(team1, 1)
		round_history_team2 = round_history(team2, 2)

		for t1, t2 in zip(round_history_team1, round_history_team2):
			if not t1['side1']:
				side1 = 't' if t2['side2'] == 'ct' else 'ct'
				t1['side1'] = side1
			elif not t2['side2']:
				side2 = 't' if t1['side1'] == 'ct' else 'ct'
				t2['side2'] = side2

			if t1['result1'] or t2['result2']:
				t1.update({
					'map_name': mi['map_name'],
					**t2
				})
				tmp.append(t1)

		time.sleep(3)

	return {'overview': tmp}


if __name__ == '__main__':
	mongo_client = MongoClient('mongodb+srv://dki_mongodb:386iPNuqq8njVbq3@cluster0.8krpn.mongodb.net/myFirstDatabase?retryWrites=true&w=majority')
	mongo_db = mongo_client['CSGO']
	mongo_collections = mongo_db['hltv_data']

	matches = mongo_collections.find({'demo_file_info': {'$exists': False}, 'overview': {'$exists': False}})

	headers = {'User-Agent': UserAgent().chrome}

	session = HTMLSession()

	len_matches = matches.count()

	for index, match in enumerate(matches):
		print(f'{index} / {len_matches}')

		if not match.get('best_of') or match.get('overview'):
			continue

		overview = main(session, headers, match)

		tmp = {
			'$set': {**overview}
		}
		mongo_collections.update_one({'url': match['url']}, tmp)

		print('sleep')
		time.sleep(6)