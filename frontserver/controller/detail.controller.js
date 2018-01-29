var express = require('express');
var router = express.Router();
var request = require('request');
var config = require('config.json');
var url= require('url');


router.get('/', function (req, res) {
	res.render('detail');
});

router.get('/show/:id', function (req, res) {
	
	console.log('frontserver get /detail/show/:id, id is:');
	console.log(req.params.id);
		
	request.get({
        url: config.awsApiUrl +'/detail/show/' + req.params.id
    }, function (error, response, body) {
        if (error) {
        	console.log('error');
        }
        if (response.statusCode !== 200) {
        
        }        
        //log the response body
        console.log('/dbserver/recommend response: 200');
        var rslt = JSON.parse(body);
        return res.render('detail', {created: JSON.stringify(rslt.created), recommend: JSON.stringify(rslt.recommend)});

    });
	
});

//show specific listing after user posted new
router.get('/show', function (req, res) {
    
	console.log('get /detail/show: Get recommendation for');
	var created = JSON.parse(req.query.created)
    console.log('req.query.created._id: ');
    console.log(created._id);
	
	request.get({
        url: url.format({
	            pathname: config.awsApiUrl +'/recommend',
	            query: {
	               "id": created._id,
	               "lat": created.address.lat,
	               "lon": created.address.lon,
	               "bedroom": created.bedroom
	             }
	          }),
    }, function (error, response, body) {
        if (error) {
        	console.log('error');
        }
        if (response.statusCode !== 200 || !response.body.success) {
 
        }
        
        //log the response body
        console.log('/dbserver/recommend response: 200');
        var recommend = JSON.parse(body);
        console.log('recommend[0].address.lat:');
        console.log(recommend.recommend[0].address.lat);
        return res.render('detail', {created: req.query.created, recommend: body});
    });
	
});

//test the detail page
router.get('/testdetail', function (req, res) {
    
    request.get({
        url: config.awsApiUrl + '/testdetail', 
        //form: req.form,	
        //json: true
    }, function (error, response, body) {
        if (error) {
            //return res.render('register', { error: 'An error occurred' });
        	console.log('error');
        }
        if (response.statusCode !== 200 || !response.body.success) {
 
        }
        console.log('yes-200');
        console.log(body);
        return res.render('detail');
    });
});

module.exports = router;