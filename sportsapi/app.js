var express = require('express');
var app = express();
var nba = require('./nba.js');
var redis = require('redis');
var fs = require('fs');
var port = 3000;

client = redis.createClient();
client.on('error', function(err) {console.log('Error ', err)});

line_scores_json_store = 'line_scores_json';
line_scores_html_store = 'line_scores_html';

mini_schedule_json_store = 'mini_schedule_json';
mini_schedule_html_store = 'mini_schedule_html';

injector_function_source = fs.readFileSync('./jsfunctions/injector.js', 'UTF-8');
console.log("it is ", injector_function_source);

app.get('/nba/v1/linescore/:team/:callback?', nba.findLineScoreByTeam);
app.get('/nba/v1/linescorehtml/:team/:callback', nba.findLineScoreHtmlByTeam);

app.get('/nba/v1/minischedule/:team/:callback?', nba.findMiniScheduleByTeam);
app.get('/nba/v1/minischedulehtml/:team/:callback', nba.findMiniScheduleHtmlByTeam);


app.use("/static", express.static(__dirname + '/static'));

app.listen(port);
console.log('Listening on port', port);
