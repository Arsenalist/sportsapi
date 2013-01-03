import urllib2
from bs4 import BeautifulSoup
import re
import json
import common
import redis
import pystache

teams = (line.strip() for line in open('./teams.txt'))

r = redis.StrictRedis(host='localhost', port=6379, db=0)
line_scores_json_store = 'line_scores_json'
line_scores_html_store = 'line_scores_html'

mini_schedule_json_store = 'mini_schedule_json'
mini_schedule_html_store = 'mini_schedule_html'



def html(url):
    return urllib2.urlopen(url).read();

for team in teams:
    schedule_html = html('http://espn.go.com/nba/team/schedule/_/name/' + team)
    latest_game_id = common.get_latest_game_id(schedule_html)
    recap_html = html('http://espn.go.com/nba/recap?id=' + latest_game_id)
    line_score = common.get_line_score(recap_html)

    # store line score json in redis
    result = r.hset(line_scores_json_store, team, json.dumps(line_score))
    if result != 0 and result != 1:
        raise Exception('Could not set line_score for ' + team)
   
    # store line score html in redis
    txt = open("./templates/line_score.mustache", 'r').read()
    line_score_html = json.dumps(pystache.render(txt, line_score).encode('utf-8'))
    result = r.hset(line_scores_html_store, team, line_score_html)
    if result != 0 and result != 1:
        raise Exception('Could not set line_score for ' + team)

        
    # get mini schedule        
    mini_schedule = common.get_mini_schedule(schedule_html)

     # store mini schedule json in redis
    result = r.hset(mini_schedule_json_store, team, json.dumps(mini_schedule))
    if result != 0 and result != 1:
        raise Exception('Could not set mini schedule for ' + team)
   
    # store mini schedule  html in redis
    txt = open("./templates/mini_schedule.mustache", 'r').read()
    mini_schedule_html = json.dumps(pystache.render(txt, mini_schedule).encode('utf-8'))
    print mini_schedule_html
    result = r.hset(mini_schedule_html_store, team, mini_schedule_html)
    if result != 0 and result != 1:
        raise Exception('Could not set mini_schedule for ' + team)
   
