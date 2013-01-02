from bs4 import BeautifulSoup
import re

# utility
def has_style_but_no_class(tag):
    return tag.has_key('style') and not tag.has_key('class')

def has_game_status_and_win_or_loss_class(class_):
    return class_ == 'game-status'

# returns the last game played, and the upcoming three games
def get_mini_schedule(schedule_html):
    soup = BeautifulSoup(schedule_html)
    table = soup.find('table', attrs = {'class': 'tablehead'})    
    lis = table.findAll('li', {'class': 'score'})

    previous_game_cont = {}
    tr = None
    # we need to go to the li level to find out whether it has a 'score' class which means
    # that the game has been played.  the last such game is the latest game played
    if lis is not None and len(lis) != 0:
        tr = lis[-1].findParent('tr')
        game_schedule = tr.findAll('ul', class_='game-schedule')[1]
        score_li =  game_schedule.find('li', class_='score')
        previous_game_cont = {
            'opp': tr.find('li', class_='team-name').a.string,
            'date': tr.find('td').string,
            'location': tr.find('li', class_='game-status').string,
            'result': game_schedule.find('li').span.string,
            'score': score_li.a.string,
            'game_id': re.search('(\d+)', score_li.a['href']).group(0)
        }
        
    # start of the season, no games played yet so just get the first three rows in the table (based on earlier work)
    if tr is None:
        next_games = table.findAll('tr', class_=re.compile(r'(evenrow|oddrow)'), limit=3)        

    # get the three rows from the last game played (based on our work to get the latest game played earlier)
    else:
        next_games = tr.findNextSiblings('tr', class_=re.compile(r'(evenrow|oddrow)'), limit=3)

    # create the next games object
    next_games_cont = []
    if next_games is not None and len(next_games) != 0:
         for game in next_games:
            time_td = game.findAll('td')[2]
            next_games_cont.append({
                'opp': game.find('li', class_='team-name').a.string,
                'date': game.find('td').string,
                'location': game.find('li', class_='game-status').string,
                'time': time_td.a.string if time_td.a is not None else time_td.string
            
            })  
    return {
        'previous': previous_game_cont,
        'next': next_games_cont
    }
            

# returns the game id by parsing the last game which as a box score linked from it
def get_latest_game_id(schedule_html):
    soup = BeautifulSoup(schedule_html)
    lis = soup.find_all('li', attrs = {'class': 'score'})
    recap_url = lis[-1].a['href']
    return re.search('(\d+)', recap_url).group(0)


# returns the team names, scores by quarter, and final score
def get_line_score(recap_html):
    soup = BeautifulSoup(recap_html)

    # parse the awaay and home team three digit codes
    table = soup.find('table', attrs = {'class': 'linescore'})
    tds = table.find_all('td', attrs = {'class': 'team'})
    away_name = tds[-2].a.string
    home_name = tds[-1].a.string

    # labels of the periods (e.g., 1, 2, OT etc., doesn't include total)
    tds = table.find_all('td', attrs = {'class': 'period'})
    periods = []
    for td in tds:
        periods.append({'l': td.string.strip()})

    # parse out the totals
    tds = table.find_all('td', attrs = {'class': 'ts'})
    away_total = tds[-2].string
    home_total = tds[-1].string

    # parse out the period scoring (no totals, as they were already parsed)
    tds = table.find_all(has_style_but_no_class)
    num_periods = len(tds) / 2
    for i in range(0,num_periods):
        periods[i]['a'] = tds[i].string
        periods[i]['h'] = tds[i+num_periods].string

    # put it together in something concise
    line_score = {
        'a': away_name,
        'h': home_name,
        'at': away_total,
        'ht': home_total,
        'p': periods
    }
    return line_score

