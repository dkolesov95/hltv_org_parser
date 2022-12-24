import os
import shutil
import sys
import patoolib

sys.path.insert(0, '../csgo demo file/')

import demo_parser



rar_path = '/home/dmitrykolesov/Downloads/demo_rar/'
unrar_path = '/home/dmitrykolesov/Downloads/demo_unrar/'


def download_demo_file(session, headers, main_page):
	url = 'https://www.hltv.org' + main_page['demo_href']
	
	demo_id = main_page['demo_href'].split('/')[-1]
	file_name = rar_path + demo_id + '.rar'
	with open(file_name, 'wb') as f:
		print(f'Downloading {demo_id}')
		request = session.get(url, headers=headers, stream=True)
		total_length = request.headers.get('content-length')

		if total_length is None:
			f.write(request.content)
		else:
			dl = 0
			total_length = int(total_length)
			for data in request.iter_content(chunk_size=4096):
				dl += len(data)
				f.write(data)
				done = int(50 * dl / total_length)
				sys.stdout.write("\r[%s%s]" % ('=' * done, ' ' * (50-done)) )
				sys.stdout.flush()


def unrar_demo_file(main_page):
	demo_id = main_page['demo_href'].split('/')[-1]
	print('unrar', demo_id)

	os.mkdir(unrar_path+demo_id)

	file_name = rar_path + demo_id + '.rar'
	unrar_file_name = patoolib.extract_archive(file_name, outdir=unrar_path+demo_id)
	files = os.listdir(unrar_file_name)
	return files


def parse_demo_files(files, main_page):
	demo_id = main_page['demo_href'].split('/')[-1]

	demo_info = []
	files_json = []
	for df in files:
		file_path = unrar_path + demo_id + '/' + df
		# demo_info.append(demo_parser.main(file_path))
		try:
			demo_info += demo_parser.main(file_path)
			files_json.append(df)
		except:
			print(f'ERROR parse_demo_files {df}')
			continue

	return demo_info, files_json


def remove_file(key, main_page, files=None):
	print('remove', key)
	demo_id = main_page['demo_href'].split('/')[-1]
	if key == 'rar':
		file_name = rar_path + demo_id + '.rar'
		os.remove(file_name)
	elif key == 'dem':
		dir_name = unrar_path + demo_id
		shutil.rmtree(dir_name)
	elif key == 'json':
		for fn in files:
			fn = fn.replace('.dem', '.json')
			os.remove(fn)


def main(session, main_page):
	best_of = main_page['best_of']

	download_demo_file(session, main_page)
	files = unrar_demo_file(main_page)

	demo_info, files_json = parse_demo_files(files, main_page)

	print('\n', 'FILES', files, '\n')

	remove_file('rar', main_page)
	remove_file('dem', main_page)
	if files_json:
		remove_file('json', main_page, files_json)

	return {'demo_file_info': demo_info}