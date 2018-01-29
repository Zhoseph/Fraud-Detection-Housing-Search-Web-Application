require('rootpath')();
var express = require('express');
var app = express();
var path = require('path');
var session = require('express-session');
var bodyParser = require('body-parser');
var expressJwt = require('express-jwt');
var config = require('config.json');
var queryString = require( "querystring" );
var url = require( "url" );
var fs = require('fs');

app.set('view engine', 'ejs');
app.set('views', __dirname + '/view');
app.use(bodyParser.urlencoded({ extended: false }));
app.use(bodyParser.json());
app.use(session({ secret: config.secret, resave: false, saveUninitialized: true }));

// use JWT auth to secure the api
app.use('/api', expressJwt({ secret: config.secret }).unless({ path: ['/api/users/authenticate', '/api/users/register'] }));

// routes
//place before other routes here: //make user visible among pages ejs //default pass data to all pages
app.use('*', function(req,res,next){
	//console.log('get *: res.session.userId' + req.session.userId);
	if(req.session.userId){
		//make user visible among pages ejs //default pass data to all pages
		res.locals.userId = req.session.userId || null;	
		console.log('get *: res.locals.userId' + res.locals.userId);
	}
	next();	
});
app.post('*', function(req,res,next){
	//console.log('get *: res.session.userId' + req.session.userId);
	if(req.session.userId){
		//make user visible among pages ejs //default pass data to all pages
		res.locals.userId = req.session.userId || null;	
		console.log('get *: res.locals.userId' + res.locals.userId);
	}
	next();	
});

//app.use('/login', require('./controller/login.controller'));
app.use('/register', require('./controller/register.controller'));
app.use('/users', require('./controller/users.controller'));
app.use('/search', require('./controller/search.controller'));
app.use('/post', require('./controller/post.controller'));
app.use('/detail', require('./controller/detail.controller'));
app.use('/fraudreport', require('./controller/fraudreport.controller'));
app.use('/listings', require('./controller/listings.controller'));
app.use('/app', require('./controller/app.controller'));

app.use('/test', require('./controller/test.controller'));
app.use('/ldetail', require('./controller/ldetail.controller'));

app.use("/detail",  express.static(__dirname + '/app/detail'));
app.use("/detail/show",  express.static(__dirname + '/app/detail'));
app.use("/users",  express.static(__dirname + '/app/listings'));
app.use("/post",  express.static(__dirname + '/app/detail'));
app.use("/listings",  express.static(__dirname + '/app/detail'));
app.use("/",  express.static(__dirname + '/app/index'));

// make '/app' default route
app.get('/', function (req, res){
	console.log("get /app");
    return res.redirect('/app');
});

var server = app.listen(3000, function () {
    console.log('Server listening at http://' + server.address().address + ':' + server.address().port);
});
