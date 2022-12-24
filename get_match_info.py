import json
import time
import random
import traceback
from requests_html import HTMLSession
from pymongo import MongoClient
from multiprocessing import Pool
from fake_useragent import UserAgent

import match_main_page
import event_info
import teams_rank
import economy
import maps_history
import overview
import demo_files


headers = {'User-Agent': UserAgent().chrome}


def main(match_url):
	mongo_client = MongoClient('')
	mongo_db = mongo_client['CSGO']
	mongo_collections = mongo_db['hltv_data']
	# mongo_collections = mongo_db['tmp']

	print(match_url)
	if mongo_collections.find_one({'url': match_url}) or not match_url:
		print('already in database', match_url)
		return

	time.sleep(random.randint(100, 1000)/100)
	session = HTMLSession()

	try:
		main_page = match_main_page.main(session, headers, match_url)
	except Exception as e:
		mongo_collections.insert_one({'url': match_url})
		print('ERROR main_page', match_url)
		traceback.print_exc()
		return

	# d_file = demo_files.main(session, headers, main_page)

	e_info = event_info.main(session, headers, main_page)
	t_rank = teams_rank.main(session, headers, main_page)
	ov_view = overview.main(session, headers, main_page)
	eco = economy.main(session, headers, main_page)
	# m_history = maps_history.main(session, headers, main_page)

	match_info = {
		**main_page,
		**e_info,
		**t_rank,
		**ov_view,
		**eco,
		#**m_history
		# **d_file,
	}
	mongo_collections.insert_one(match_info)

	print('sleep 30 sec')
	time.sleep(30)	
	

if __name__ == '__main__':
	pool = Pool()
	
	with open('urls.txt') as f:
		file = f.read()

	urls = file.split('\n')

	for i in range(0, len(urls), 2):
		print(f'index {i}\n')
		u = [urls[i], urls[i+1]]
		pool.map(main, u)
		
		print('\n')