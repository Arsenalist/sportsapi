import urllib2
from bs4 import BeautifulSoup
import re
import json
import common
import redis
import pystache
import codecs

teams = (line.strip() for line in open('./teams.txt'))
r = redis.StrictRedis(host='localhost', port=6379, db=0)

line_scores_json_store = 'line_scores_json'
line_scores_html_store = 'line_scores_html'

mini_schedule_json_store = 'mini_schedule_json'
mini_schedule_html_store = 'mini_schedule_html'

team_summary_html_store = 'team_summary_html'

standings_html_store = 'standings_html'

def nba_structure():
    return (
        {'CENTRAL': ['ind', 'chi', 'mil', 'det', 'cle']},
        {'PACIFIC': ['lac', 'gs', 'lal', 'sac', 'phx']},
        {'SOUTHEAST': ['mia', 'atl', 'orl', 'cha', 'wsh']},
        {'ATLANTIC': ['ny', 'bkn', 'phi', 'bos', 'tor']},
        {'NORTHWEST': ['okc', 'den', 'por', 'min', 'utah']},
        {'SOUTHWEST': ['sa', 'mem', 'hou', 'dal', 'no']},
        {'WESTERN': ['okc', 'lac', 'sa', 'mem', 'gs', 'hou', 'den', 'por', 'min', 'utah', 'lal', 'dal', 'sac', 'phx', 'no']},
        {'EASTERN': ['mia', 'ny', 'atl', 'ind', 'chi', 'mil', 'bkn', 'phi', 'bos', 'tor', 'orl', 'det', 'cha', 'cle', 'wsh']}
    )


def html(url):
    return urllib2.urlopen(url).read()
'''
for team in teams:
    schedule_html = html('http://espn.go.com/nba/team/schedule/_/name/' + team)
    latest_game_id = common.get_latest_game_id(schedule_html)
    recap_html = html('http://espn.go.com/nba/recap?id=' + latest_game_id)
    line_score = common.get_line_score(recap_html)

    # store line score html in redis
    txt = open("./templates/line_score.mustache", 'r').read()
    line_score_html = json.dumps(pystache.render(txt, line_score).encode('utf-8'))
    result = r.hset(line_scores_html_store, team, line_score_html)
    if result != 0 and result != 1:
        raise Exception('Could not set line_score for ' + team)
    print "Stored line score for %s" % team

        
    # get mini schedule        
    mini_schedule = common.get_mini_schedule(schedule_html)
   
    # store mini schedule  html in redis
    txt = open("./templates/mini_schedule.mustache", 'r').read()
    mini_schedule_html = json.dumps(pystache.render(txt, mini_schedule).encode('utf-8'))	
    result = r.hset(mini_schedule_html_store, team, mini_schedule_html)
    if result != 0 and result != 1:
        raise Exception('Could not set mini_schedule for ' + team)
    print "Stored mini schedule for %s" % team

summary_html = html('http://www.basketball-reference.com/leagues/NBA_2013.html') 
team_summary = common.get_summary_stats(summary_html)
for team in team_summary:
    txt = open("./templates/team_summary.mustache", 'r').read()
    team_summary_html = json.dumps(pystache.render(txt, team.__dict__).encode('utf-8'))
    result = r.hset(team_summary_html_store, team, team_summary_html)
    if result != 0 and result != 1:
        raise Exception('Could not set team summary for ' + team.team)
    print "Stored summary for %s" % team.team
'''
league_standings_html = html('http://espn.go.com/nba/standings/_/group/1')
conference_standings_html = html('http://espn.go.com/nba/standings/_/group/2')
division_standings_html = html('http://espn.go.com/nba/standings/_/group/3')

league = common.get_league_or_division_standings(league_standings_html)
conference = common.get_conference_standings(conference_standings_html)
division = common.get_league_or_division_standings(division_standings_html)

# create team_standings which has three entries for division, conference, and league standings
for team in teams:
    # keeps track of which container (EASTERN, WESTERN etc.) apply for this team
    team_containers = []
    for item in nba_structure():
        part, part_teams  = item.popitem()
        if team in part_teams:
            team_containers.append(part)

    # a structure we can work with in templates
    team_standings = []
    for t in team_containers:
        if t in division.keys():
            team_standings.append({'division': t, 'teams': division[t]})
        if t in conference.keys():
            team_standings.append({'division': t, 'teams': conference[t]})
    team_standings.append({'division': 'NBA', 'teams': league['NBA']})

    # to highlight current team, we need to modify structure to have a boolean value indicating which team to highlight    
    for team_standing in team_standings:
        for t in team_standing['teams']:
            t.current = team == t.team

    # replace team objects with a dict            
    for team_standing in team_standings:
        for k, v in team_standing.iteritems():
            if k == 'teams':
                dicts = []
                for t in v:
                    dicts.append(t.__dict__)
                team_standing['teams'] = dicts
                        
    txt = open("./templates/standings.mustache", 'r').read()
    renderer = pystache.Renderer(file_encoding='latin-1', string_encoding='latin-1')
    standings_html = renderer.render(txt, {'standings': team_standings})
    result = r.hset(standings_html_store, team, json.dumps(standings_html))
    if result != 0 and result != 1:
        raise Exception('Could not set standings for ' + team.team)
    print "Stored standings for ", team        



