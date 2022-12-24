import json
import time
from fake_useragent import UserAgent
from datetime import date, datetime
from bs4 import BeautifulSoup



months = {
	'january': 1,
	'february': 2,
	'march': 3,
	'april': 4,
	'may': 5,
	'june': 6,
	'july': 7,
	'august': 8,
	'september': 9,
	'october': 10,
	'november': 11,
	'december': 12
}


def team_rank(request, unixtime):
	try:
		rank = request.html.find('.graph', first=True).attrs['data-fusionchart-config']
	except:
		return '', ''

	rank_json = json.loads(rank.encode('ascii', 'ignore'))
	now_rank = rank_json['dataSource']['dataset'][0]['data'][-1]['value']
	datas = rank_json['dataSource']['dataset'][0]['data']
	for data in datas:
		link_split = data['link'].split('/')
		if len(link_split) == 7:
			_, _, _, year, month, day, _ = link_split
		else:
			_, _, _, year, month, day = link_split
		week_number = datetime.fromtimestamp(unixtime).isocalendar()[1]
		previous_week_number = date(int(year), months[month], int(day)).isocalendar()[1]

		if week_number == previous_week_number and datetime.now().year == int(year):
			return data['value'], now_rank
	return '', now_rank


def main(session, headers, main_page):
	print('teams_rank', main_page.get('url'))

	tmp = {}
	for index, url in enumerate([main_page['url1'], main_page['url2']]):
		url = 'https://www.hltv.org' + url
		request = session.get(url, headers=headers)

		pr, nr = team_rank(request, main_page['unixtime'])
		tmp[f'rank{index+1}'] = {
			'previous_rank': pr,
			'now_rank': nr
		}
		time.sleep(3)
	return tmp