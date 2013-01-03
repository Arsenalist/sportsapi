from bs4 import BeautifulSoup
import re

class TeamSummary:
    def __init__(self, team, ortg, drtg, pace, oefg, otov, orb, oftfga, defg, dtov, drb, dftfga):
        self.team = team
        self.ortg = ortg
        self.drtg = drtg
        self.pace = pace
        self.oefg = oefg
        self.otov = otov
        self.orb = orb
        self.oftfga = oftfga
        self.defg = defg
        self.dtov = dtov
        self.drb = drb
        self.dftfga = dftfga

    def find_rank(self, summary):
        for idx, val in enumerate(summary):
            if self.team == val.team:
                return idx+1
        raise Exception("Could not find team in summary")

    def __str__(self):
        return self.team;

    def __repr__(self):
        return self.__str__()

# utility
def has_style_but_no_class(tag):
    return tag.has_key('style') and not tag.has_key('class')

def has_empty_class(tag):
    return tag.name == 'tr' and tag['class'] == ''

bbref2espn_conversion = {
    'SAS': 'SA',
    'NYK': 'NY',
    'GSW': 'GS',
    'UTA': 'UTAH',
    'BRK': 'BKN',
    'PHO': 'PHX',
    'NOH': 'NO',
    'WAS': 'WSH'
}

def bbref2espn(bbref_team):
    if bbref_team in bbref2espn_conversion:
        return bbref2espn_conversion[bbref_team].lower()
    else:
        return bbref_team.lower()

def get_summary_stats(summary_html):
    soup = BeautifulSoup(summary_html)
    table = soup.find('table', id='misc')
    trs = table.find('tbody').findAll('tr')
    del trs[-1]
    summary = []
    for tr in trs:
        tds = tr.findAll('td')
        bbref_team = re.search(r"/.*/(.*)/.*\..*", tds[1].a['href']).group(1)
        team = bbref2espn(bbref_team)
        t = TeamSummary(            
            team,
            float(tds[8].string),
            float(tds[9].string),
            float(tds[10].string),
            float(tds[11].string),
            float(tds[12].string),
            float(tds[13].string),
            float(tds[14].string),
            float(tds[15].string),
            float(tds[16].string),
            float(tds[17].string),
            float(tds[18].string)
        )
        summary.append(t)

    ortg_sorted = sorted(summary, key=lambda team_summary: team_summary.ortg, reverse=True)
    drtg_sorted = sorted(summary, key=lambda team_summary: team_summary.drtg)
    pace_sorted = sorted(summary, key=lambda team_summary: team_summary.pace, reverse=True)
    oefg_sorted = sorted(summary, key=lambda team_summary: team_summary.oefg, reverse=True)
    otov_sorted = sorted(summary, key=lambda team_summary: team_summary.otov)
    orb_sorted = sorted(summary, key=lambda team_summary: team_summary.orb, reverse=True)
    oftfga_sorted = sorted(summary, key=lambda team_summary: team_summary.oftfga, reverse=True)
    defg_sorted = sorted(summary, key=lambda team_summary: team_summary.defg)
    dtov_sorted = sorted(summary, key=lambda team_summary: team_summary.dtov, reverse=True)
    drb_sorted = sorted(summary, key=lambda team_summary: team_summary.drb, reverse=True)
    dftfga_sorted = sorted(summary, key=lambda team_summary: team_summary.dftfga)
    for team in summary:
        team.ortg_rank = team.find_rank(ortg_sorted)
        team.drtg_rank = team.find_rank(drtg_sorted)
        team.pace_rank = team.find_rank(pace_sorted)
        team.oefg_rank = team.find_rank(oefg_sorted)
        team.otov_rank = team.find_rank(otov_sorted)
        team.orb_rank = team.find_rank(orb_sorted)
        team.oftfga_rank = team.find_rank(oftfga_sorted)
        team.defg_rank = team.find_rank(defg_sorted)
        team.dtov_rank = team.find_rank(dtov_sorted)
        team.drb_rank = team.find_rank(drb_sorted)
        team.dftfga_rank = team.find_rank(dftfga_sorted)

    return summary

    



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

