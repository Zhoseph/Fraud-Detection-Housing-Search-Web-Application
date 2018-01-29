var express = require('express');
var router = express.Router();
var request = require('request');
var config = require('config.json');
var url= require('url');


router.get('/', function (req, res) {
	res.render('listings');
});

router.post('/gsearch', function (req, res) {
	
	console.log('post /gsearch, key: ' +req.body.generalsearch);
	
	 /*return res.redirect(url.format({
         pathname:"/detail/show",
         query: {
            "created": JSON.stringify(j.created),
            "info":"newly created listing"
          }
     }));  */
    request.post({
	        url: config.awsApiUrl + '/listings/gsearch?key='
	        	+ req.body.generalsearch,	       
	    }, function (error, response, body) {
	        if (error) {
	        	console.log('post /gsearch error');
	        }
	        if (response.statusCode !== 200) {	 
	        }
	        console.log('respond: 200');
	        console.log('body before JSON.parse: ');
	        //console.log(body);
	        //var j=JSON.parse(body);
	        //console.log(j.description);
//	        console.log('body after JSON.parse: ');
//	        console.log('created listing lat:');
//	        console.log(j.created.address.lat);
//	        console.log('recommend[0].address.lat');
//	        console.log(j.recommend[0].address.lat);
	        //req.session.success = 'Registration successful'; 
	        return res.render('listings', {docs: body});
	    });
        
    });


module.exports = router;