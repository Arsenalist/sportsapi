var express = require('express');
var app = express();
var nba = require('./nba.js');
var redis = require('redis');
var fs = require('fs');
var port = 3000;

client = redis.createClient();
client.on('error', function(err) {console.log('Error ', err)});

line_scores_html_store = 'line_scores_html';
mini_schedule_html_store = 'mini_schedule_html';
team_summary_html_store = 'team_summary_html';
standings_html_store = 'standings_html';

callback_linescore  = fs.readFileSync('./jsfunctions/callbacklinescore.js', 'UTF-8');
callback_minischedule  = fs.readFileSync('./jsfunctions/callbackminischedule.js', 'UTF-8');
callback_teamsummary  = fs.readFileSync('./jsfunctions/callbackteamsummary.js', 'UTF-8');
callback_standings  = fs.readFileSync('./jsfunctions/callbackstandings.js', 'UTF-8');

app.get('/nba/v1/linescorehtml/:team/:callback', nba.findLineScoreHtmlByTeam);
app.get('/nba/v1/minischedulehtml/:team/:callback', nba.findMiniScheduleHtmlByTeam);
app.get('/nba/v1/summaryhtml/:team/:callback', nba.findSummaryHtmlByTeam);
app.get('/nba/v1/standingshtml/:team/:callback', nba.findStandingsHtmlByTeam);


app.use("/static", express.static(__dirname + '/static'));

app.listen(port);
console.log('Listening on port', port);
