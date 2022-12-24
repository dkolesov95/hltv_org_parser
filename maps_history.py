import time
from datetime import datetime



def generate_date(unixtime):
	unixtime = unixtime - 60*60*24
	sd = datetime.fromtimestamp(unixtime - 60*60*24*31*3).strftime('%Y-%m-%d')
	ed = datetime.fromtimestamp(unixtime).strftime('%Y-%m-%d')
	return f'?startDate={sd}&endDate={ed}'


def map_info(column):
	map_name = column.find('.map-pool', first=True)
	if not map_name:
		return None

	stats_row = column.find('.stats-row')
	tmp = {'map_name': map_name.text}
	for sr in stats_row:
		title, value = sr.find('span')
		if title.text == 'Wins / draws / losses':
			wins, draws, losses = value.text.split('/')
			tmp.update({
				'wins': int(wins),
				'draws': int(draws),
				'losses': int(losses)
			})
		else:
			tmp[title.text] = value.text
	return tmp

def main(session, headers, main_page):
	print('maps_history', main_page['url'])

	data = [
		(main_page['team1'], main_page['url1']),
		(main_page['team2'], main_page['url2'])
	]

	tmp = []
	for d in data:
		team, url = d
		url = f"https://www.hltv.org/stats/teams/maps/{'/'.join(url.split('/')[-2:])}"
		date = generate_date(main_page['unixtime'])
		request = session.get(url+date, headers=headers)
		try:
			columns = request.html.find('.stats-team-maps', first=True).find('.two-grid', first=True).find('.col')
		except Exception as e:
			print('maps_history', 'ERRRO', e)
			continue
		for column in columns:
			m_info = map_info(column)
			if not m_info:
				continue
			m_info.update({'team': team})
			tmp.append(m_info)

		time.sleep(5)
	return {'maps_history': tmp}