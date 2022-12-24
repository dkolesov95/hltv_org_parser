import time


def team_name(team):
	return team.find('.team', first=True).find('.team-logo', first=True).attrs['alt']


def team_side(eq):
	side = eq.find('.equipment-category', first=True).attrs['src'].split('/')[-1][:2]
	if side == 'ct':
		return 'ct'
	return 't'


def round_result(eq):
	rs = eq.find('.equipment-category', first=True).attrs['class'][-1]
	if rs == 'lost':
		return 0
	return 1


def equipments(team, index_team):
	tn = team_name(team)
	eqs = team.find('.equipment-category-td')
	tmp = []
	for index, eq in enumerate(eqs):
		tmp.append({
			'round': index+1,
			f'team{index_team+1}': tn,
			f'side{index_team+1}': team_side(eq),
			f'value{index_team+1}': eq.attrs['title'].split(': ')[-1],
			f'result{index_team+1}': round_result(eq),
		})
	return tmp


def main(session, headers, main_page):
	print('economy', main_page['url'])

	tmp = []
	for map_info in main_page['maps_info']:
		url = map_info['stats_url'].split('/')
		url.insert(3, 'economy')
		url = 'https://www.hltv.org/' + '/'.join(url)
		request = session.get(url, headers=headers)

		halfs = request.html.find('.equipment-categories')
		for index_half, half in enumerate(halfs):
			teams = half.find('.team-categories')

			eqs1 = equipments(teams[0], 0)
			eqs2 = equipments(teams[1], 1)

			for eq1, eq2 in zip(eqs1, eqs2):
				if eq1['round'] == eq2['round']:
					eq1.update(eq2)
					eq1['half'] = index_half + 1
					eq1['map_name'] = map_info['map_name']
					tmp.append(eq1)
		time.sleep(5)
	return {'economy': tmp}