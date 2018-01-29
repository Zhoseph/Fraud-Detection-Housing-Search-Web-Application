var express = require('express');
var router = express.Router();
var request = require('request');
var config = require('config.json');

router.get('/login', function (req, res) {
	
	//delete req.session.[variable];
	//req.session.destroy();
    res.render('login');
});

router.get('/register', function (req, res) {
    res.render('register');
});


router.get('/logout', function (req, res) {

	req.session.destroy();
    res.redirect('/users/login');
});

router.post('/register', function (req, res) {
    request.post({
        url: config.awsApiUrl + '/users/register',
        form: req.body,
        json: true
    }, function (error, response, body) {
        if (error) {
            return res.render('register', { error: 'error: dbserver POST /users/register' });
        }
        console.log('body');
        console.log(body);        
        if(body == 'registered'){
        	req.session.userId = req.body.email;
        	console.log('req.body.email'+req.body.email);
        	return res.redirect('/');
        }        
    	return res.render('register', { error: body});  	        
	});
});


router.post('/login', function (req, res) {
    request.post({
        url: config.awsApiUrl + '/users/login',
        form: req.body,
        json: true
    }, function (error, response, body) {
        if (error) {
            return res.render('login', { error: 'error: dbserver POST /users/login' });
        }
        if(body == 'valid Login'){
        	//session created;
        	delete req.session.userId;
        	req.session.userId = req.body.email;
        	console.log('successfully login!')
        	return res.redirect('/');
        }    	
        //save JWT token in the session to make it available to the angular app
        //req.session.token = body.token;
        console.log('body');
        console.log(body);
        console.log('req.body.email'+req.body.email);
    	return res.render('login', { error: "user or password incorrect", username: req.body.email });  	        
	});
});

router.get('/deletelisting/:id', function(req, res){
	if(!req.session.userId){
		res.redirect('/users/login');
	}else{		
		request.get({
	        url: config.awsApiUrl + '/users/deletelisting/' + req.params.id,
	    }, function (error, response, body) {
	        if (error) {
	            return res.send('error: dbserver /users/deletelisting');
	        }
	        if(body == 'removed'){
	        	return res.redirect('/users/mylistings');
	        }else{
	        	return res.send('/deletelisting/ error');
	        }     

	   });		
	}
});

router.get('/mylistings', function(req, res){
	if(!req.session.userId){
		res.redirect('/users/login');
	}else{		
		request.get({
	        url: config.awsApiUrl + '/users/mylistings/' + req.session.userId,
	    }, function (error, response, body) {
	        if (error) {
	            return res.render('login', { error: 'error: dbserver GET /users/mylistings' });
	        }
	        var data = JSON.parse(body);
	        console.log(data.rows);
	        return res.render('mylistings', {user: data.rows, listings : data.docs});
	        //console.log('get mylistings body: ')
	        //console.log(body);
	        //return res.send(body);
	        /*if(body == 'valid Login'){
	        	//session created;
	        	delete req.session.userId;
	        	req.session.userId = req.body.email;
	        	console.log('successfully login!')
	        	return res.redirect('/');
	        }    	
	        //save JWT token in the session to make it available to the angular app
	        //req.session.token = body.token;
	        console.log('body');
	        console.log(body);
	        console.log('req.body.email'+req.body.email);
	    	return res.render('login', { error: "user or password incorrect", username: req.body.email });  	        
		*/});
		
	}
});

//test 
router.get('/', function (req, res) {
    request.get({
        url: config.awsApiUrl + '/users',
        //form: req.body,
        json: true
    }, function (error, response, body) {
        if (error) {
            return res.render('login', { error: 'error: dbserver GET /users' });
        }
        //if (!body.token) {
        if(body == 'error: test query user01@gmail.com'){
        	return res.render('login', { error: 'Username or password is incorrect'});
        }
    	return res.render('login', { error: body});
    });
});


module.exports = router;