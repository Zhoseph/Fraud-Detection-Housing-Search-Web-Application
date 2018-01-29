var express = require('express');
var router = express.Router();
var request = require('request');
var config = require('config.json');
var url= require('url');


router.get('/', function (req, res) {
	res.render('fraudreport');
});

router.get('/:id', function (req, res) {
	console.log('get /fraudreport/:id');
	console.log(req.params.id);
		
	request.get({
        url: config.awsApiUrl +'/fraudreport/' + req.params.id
    }, function (error, response, body) {
        if (error) {
        	console.log('error');
        }
        if (response.statusCode !== 200) {
        
        }        
        //log the response body
        console.log('/dbserver/fraudreport/:id respond: 200');
        var rslt = JSON.parse(body);
        console.log(rslt.body);
        if(rslt.message == 'NoFound'){
        	return res.render('fraudreportblank');
        }else{
        	return res.render('fraudreport', {report: JSON.stringify(rslt.body)});
        }        
        //return res.render('detail', {created: JSON.stringify(rslt.created), recommend: JSON.stringify(rslt.recommend)});
        
    });
	
});

module.exports = router;