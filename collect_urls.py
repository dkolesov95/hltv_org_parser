import time
from requests_html import HTMLSession


if __name__ == '__main__':
	session = HTMLSession()	
	for i in range(0, 6100, 100):
		url = f'https://www.hltv.org/results?offset={i}'
		request = session.get(url)

		tmp = ['\n']
		sublist = request.html.find('.results-sublist')
		for s in sublist:
			tmp += s.links

		with open('urls.txt', 'a') as f:
			f.write('\n'.join(tmp))
		
		print('index', i, 'sleep 30 sec')
		time.sleep(30)