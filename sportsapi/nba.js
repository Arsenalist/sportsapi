exports.findLineScoreHtmlByTeam = function (req, res) {
    var team = req.params.team;
    var callback = req.params.callback;
    client.hget(line_scores_html_store, team, function(err, data) {
	var data = callback + '(' + data + ')';
	data = callback_linescore + data;
	setJsonResponseHeaders(res, data);
    });
}

exports.findMiniScheduleHtmlByTeam = function (req, res) {
    var team = req.params.team;
    var callback = req.params.callback;
    client.hget(mini_schedule_html_store, team, function(err, data) {
	var data = callback + '(' + data + ')';
	data = callback_minischedule + data;
	setJsonResponseHeaders(res, data);
    });
}

exports.findSummaryHtmlByTeam = function (req, res) {
    var team = req.params.team;
    var callback = req.params.callback;
    client.hget(team_summary_html_store, team, function(err, data) {
	var data = callback + '(' + data + ')';
	data = callback_teamsummary + data;
	setJsonResponseHeaders(res, data);
    });
}



function setJsonResponseHeaders(res, data) {
    res.header('content-type', 'text/javascript');
    res.header('content-length', data == null ? 0 : data.length);    
    res.end(data);
}



