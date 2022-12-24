import asyncio


# https://www.hltv.org/stats/matches/performance/mapstatsid/123920/g2-vs-natus-vincere
# https://www.hltv.org/stats/matches/economy/mapstatsid/123920/g2-vs-natus-vincere
# https://www.hltv.org/matches/2349930/g2-vs-natus-vincere-iem-cologne-2021
						# /stats/matches/mapstatsid/123920/g2-vs-natus-vincere



async def main(asession, main_page):
	for map_info in main_page['maps_info']:
		url = map_info['stats_url'].split('/')
		url.insert(3, 'performance')
		url = 'https://www.hltv.org/' + '/'.join(url)
		request = await asession.get(url)

		killmatrix_menu = None
		killmatrix_content = None

		await asyncio.sleep(7)