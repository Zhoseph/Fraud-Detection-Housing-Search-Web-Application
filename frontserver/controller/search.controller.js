var express = require('express');
var router = express.Router();
var request = require('request');
var config = require('config.json');


router.post('/general', function (req, res) {
	
	res.send('ok');
	
	
    // register using api to maintain clean separation between layers
	/*console.log("searchinput:"+req.body.searchinput);
	console.log("minprice:"+req.body.minprice);
	console.log("chSearchTitle:"+req.body.chSearchTitle);
	console.log("minBedRoom:"+req.body.minBedRoom);
	console.log("maxBedRoom:"+req.body.maxBedRoom);
    request.post({
        url: config.awsApiUrl + '/login' + req.body.searchinput
        		+ req.body.chSearchTitle + req.body.minBedRoom
        		+ req.body.maxBedRoom,
        form: req.body,
        json: true
    }, function (error, response, body) {
        if (error) {
            return res.render('register', { error: 'An error occurred' });
        }

        if (response.statusCode !== 200 || !response.body.success) {
            return res.render('register', {
                error: response.body.msg,
                username: req.body.username,
                phonenum: req.body.phonenum,
                email: req.body.email,
            });
        }
        
        req.session.success = 'Registration successful';
        return res.redirect('/login');
    });*/
});


router.get('/', function (req, res) {
    res.render('search');
});



//router.post('/', function (req, res) {
//    // register using api to maintain clean separation between layers
//    request.post({
//        url: config.apiUrl + '/users/register',
//        form: req.body,
//        json: true
//    }, function (error, response, body) {
//        if (error) {
//            return res.render('register', { error: 'An error occurred' });
//        }
//
//        if (response.statusCode !== 200) {
//            return res.render('register', {
//                error: response.body,
//                username: req.body.username,
//                phonenum: req.body.phonenum,
//                email: req.body.email,
//            });
//        }
//
//        // return to login page with success message
//        req.session.success = 'Registration successful';
//        return res.redirect('/login');
//    });
//});

router.post('/', function (req, res) {
    // register using api to maintain clean separation between layers
	console.log("searchinput:"+req.body.searchinput);
	console.log("minprice:"+req.body.minprice);
	console.log("chSearchTitle:"+req.body.chSearchTitle);
	console.log("minBedRoom:"+req.body.minBedRoom);
	console.log("maxBedRoom:"+req.body.maxBedRoom);
    request.post({
        url: config.awsApiUrl + '/login' + req.body.searchinput
        		+ req.body.chSearchTitle + req.body.minBedRoom
        		+ req.body.maxBedRoom,
        form: req.body,
        json: true
    }, function (error, response, body) {
        if (error) {
            return res.render('register', { error: 'An error occurred' });
        }

        if (response.statusCode !== 200 || !response.body.success) {
            return res.render('register', {
                error: response.body.msg,
                username: req.body.username,
                phonenum: req.body.phonenum,
                email: req.body.email,
            });
        }
        //
        //if () {
        //    return res.render('register', {
        //        error: response.body,
        //        username: req.body.username,
        //        phonenum: req.body.phonenum,
        //        email: req.body.email,
        //    });
        //}

        // return to login page with success message
        req.session.success = 'Registration successful';
        return res.redirect('/login');
    });
});

/*router.post('/', function (req, res) {
    // register using api to maintain clean separation between layers
    request.post({
        url: config.awsApiUrl + '/user/signup/' + req.body.username + '/' + req.body.password + '/' + req.body.email + '/' + req.body.phonenum + '/',
        form: req.body,
        json: true
    }, function (error, response, body) {
        if (error) {
            return res.render('register', { error: 'An error occurred' });
        }

        if (response.statusCode !== 200 || !response.body.success) {
            return res.render('register', {
                error: response.body.msg,
                username: req.body.username,
                phonenum: req.body.phonenum,
                email: req.body.email,
            });
        }
        //
        //if () {
        //    return res.render('register', {
        //        error: response.body,
        //        username: req.body.username,
        //        phonenum: req.body.phonenum,
        //        email: req.body.email,
        //    });
        //}

        // return to login page with success message
        req.session.success = 'Registration successful';
        return res.redirect('/login');
    });
});*/

module.exports = router;