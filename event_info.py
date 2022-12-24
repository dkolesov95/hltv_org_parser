import time


def main(session, headers, main_page):
	print('event_info', main_page['url'])

	url = 'https://www.hltv.org' + main_page['event_link']
	request = session.get(url, headers=headers)

	event_info = request.html.find('.no-top-border', first=True)
	
	try:
		unixtime = event_info.find('tbody', first=True).find('span', first=True).attrs['data-unix']
		unixtime = int(int(unixtime) / 1000)
	except:
		unixtime = None

	prizepool = event_info.find('tbody', first=True).find('.prizepool', first=True).text
	teams_number = event_info.find('tbody', first=True).find('.teamsNumber', first=True).text
	location = event_info.find('tbody', first=True).find('.location', first=True).text

	tmp = {
		'unixtime': unixtime,
		'prizepool': prizepool,
		'teams_number': teams_number,
		'location': location
	}
	time.sleep(5)
	return {'event_info': tmp}