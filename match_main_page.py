import re
import time
import traceback


def match_unixtime(team_boxs):
    unixtime = team_boxs.find('.time', first=True).attrs['data-unix']
    # unixtime = int(int(re.search(r'\d+', unixtime_html).group(0)) / 1000)
    unixtime = int(int(unixtime) / 1000) 

    time_and_event = team_boxs.find('.timeAndEvent', first=True)
    event_link, event = time_and_event.find('a', first=True).attrs.values()
    return {'unixtime': unixtime, 'event': event, 'event_link': event_link}


def team_score(team_boxs, team):
    name, score = team_boxs.find('.team')[team].text.split('\n')
    return {f'team{team+1}': name, f'score{team+1}': score}


def team_url(teams_boxs, team):
    return {f'url{team+1}': list(teams_boxs.find('.team')[team].links)[0]}
    

def teams_box(request):
    teams_box = request.html.find('.teamsBox', first=True)
    if not teams_box:
        return {}

    time = match_unixtime(teams_box)
    team1 = team_score(teams_box, 0)
    team2 = team_score(teams_box, 1)
    url1 = team_url(teams_box, 0)
    url2 = team_url(teams_box, 1)

    return {**time, **team1, **team2, **url1, **url2}


def demo_href(request):
    try:
        href = request.html.find('.g-grid', first=True) \
            .find('.col-5-small', first=True) \
            .find('.streams', first=True) \
            .find('a', first=True).attrs['href']
    except:
        print('ERROR: demo href not found')
        traceback.print_exc()
        # 1/0
    return href


def pick_ban(veto):
    maps = [
        'Mirage', 'Inferno', 'Train', 'Dust2', 'Overpass',
        'Nuke', 'Cache', 'Cobblestone', 'Vertigo', 'Ancient'
    ]
    solution = 'decider'
    if 'picked' in veto:
        solution = 'picked'
    elif 'removed' in veto:
        solution = 'removed'
    map_name = [i for i in maps if i in veto]
    return {'solution': solution, 'map_name': ''.join(map_name)}


def map_veto(request, t_box):
    # return {'map_veto': request.html.find('.veto-box')[-1].text}
    veto = request.html.find('.veto-box')[-1].text.split('\n')
    team1, team2 = t_box['team1'], t_box['team2']
    tmp = []
    for v in veto:
        if team1 in v:
            solution = pick_ban(v)
            solution.update({'team': team1})
        elif team2 in v:
            solution = pick_ban(v)
            solution.update({'team': team2})
        else:
            solution = pick_ban(v)
            solution.update({'team': None})
        tmp.append(solution)
    return {'map_veto': tmp}


def team_map_result(mapholder, side):
    team_name, score = mapholder.find(f'.results-{side}', first=True).text.split('\n')
    
    try:
        score = int(score)
    except:
        return None, None
    return team_name, score


def stats_url(mapholder):
    return mapholder.find('.results-center-stats', first=True).find('a', first=True).attrs['href']


def result_by_sides(mapholder):
    half_score = mapholder.find('.results-center-half-score', first=True)
    t1, t2 = half_score.find('.t')
    ct1, ct2 = half_score.find('.ct')
    return {
        'half1': {'t': int(t1.text), 'ct': int(ct1.text)},
        'half2': {'t': int(t2.text), 'ct': int(ct2.text)}
    }


def played_map(mapholder):
    map_name = mapholder.find('.map-name-holder', first=True).text
    team1, score1 = team_map_result(mapholder, 'left')
    team2, score2 = team_map_result(mapholder, 'right')
    if score1 is None or score2 is None:
        return None
    
    try:
        tmp = {
            'map_name': map_name,
            'team1': team1,
            'team2': team2,
            'score1': score1,
            'score2': score2,
            'stats_url': stats_url(mapholder),
            **result_by_sides(mapholder)
        }
    except:
        return None
    return tmp
    

def played_maps(request):
    mapholders = request.html.find('.mapholder')

    maps_info = []
    for maph in mapholders:
        map_info = played_map(maph)
        if not map_info:
            continue
        maps_info.append(map_info)
    return len(mapholders), maps_info


def maps_names_header(matchstats):
    mn = matchstats.find('.header', first=True).find('.dynamic-map-name-full')
    return [i.text for i in mn]


def team_stats(data):
    tmp = []
    for d in data:
        players = d.find('.players')
        kd = d.find('.kd')
        pm = d.find('.plus-minus')
        adr = d.find('.adr')
        kast = d.find('.kast')
        rating = d.find('.rating')
        for i in range(1, 6):
            player = players[i].text
            if '\n' in player:
                player = player.split('\n')[-1]
            tmp.append({
                'player': player,
                'kd': kd[i].text,
                'plus_minus': int(pm[i].text),
                'adr': float(adr[i].text),
                'kast': kast[i].text,
                'rating': float(rating[i].text)
            })
    return tmp


def players_stats(requests):
    matchstats = requests.html.find('.matchstats', first=True)
    maps_names = maps_names_header(matchstats)
    
    players_stats = matchstats.find('.stats-content')
    tmp = []
    for mn, ps in zip(maps_names, players_stats):
        tmp.append({
            'total': team_stats(ps.find('.totalstats')),
            't': team_stats(ps.find('.tstats')),
            'ct': team_stats(ps.find('.ctstats')),
            'map_name': mn
        })
    return tmp
    

def main(session, headers, match_url):
    print('match_main_page', match_url.split('/')[3])

    url = 'https://www.hltv.org' + match_url
    request = session.get(url, headers=headers)
    best_of, maps_info = played_maps(request)
    t_box = teams_box(request)
    d_href = demo_href(request) 

    tmp = {
        'url': match_url,
        'demo_href': d_href,
        'best_of': best_of,
        'maps_info': maps_info,
        'players_stats': players_stats(request),
        **t_box,
        **map_veto(request, t_box),
    }
    time.sleep(5)
    return tmp