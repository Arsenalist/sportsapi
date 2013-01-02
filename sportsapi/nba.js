exports.findLineScoreByTeam = function (req, res) {
    var team = req.params.team;
    var callback = req.params.callback;
    client.hget(line_scores_json_store, team, function(err, results) {
        prepareAndSendData(results, res, callback);
    });
}

exports.findLineScoreHtmlByTeam = function (req, res) {
    var team = req.params.team;
    var callback = req.params.callback;
    client.hget(line_scores_html_store, team, function(err, results) {
        prepareAndSendData(results, res, callback);
    });
}

exports.findMiniScheduleByTeam = function (req, res) {
    var team = req.params.team;
    var callback = req.params.callback;
    client.hget(mini_schedule_json_store, team, function(err, results) {
        prepareAndSendData(results, res, callback);
    });
}

exports.findMiniScheduleHtmlByTeam = function (req, res) {
    var team = req.params.team;
    var callback = req.params.callback;
    client.hget(mini_schedule_html_store, team, function(err, results) {
        prepareAndSendData(results, res, callback);
    });
}

prepareAndSendData = function(data, res, callback) {
    var data = callback == null ? results : callback + '(' + data + ')';
    data = injector_function_source + data;
    setJsonResponseHeaders(res, data);
    res.end(data);
}


function setJsonResponseHeaders(res, data) {
    res.header('content-type', 'text/json');
    res.header('content-length', data == null ? 0 : data.length);    
}



