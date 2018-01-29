var express = require('express');
var router = express.Router();
var ejs = require("ejs");
var mysql = require('./mysql'); // './mysql' point to mysql,js file
var crypt = require ('crypto');

/* GET /users. */
router.get('/', function(req, res, next) {

	//connect to database with connection pool	
	var database = mysql.getConnection();
	//test db
	database.query('select * from user where email= "user01@gmail.com" ', function(err, rows, fields) {
			if(err){
				console.log("ERROR: " + err.message);
				return res.send("error: test query user01@gmail.com");
			}
			else 
			{	// result
				console.log("Oh yes!:"+rows);
				return res.send(rows);
			}
	});
});


/* POST /users/ login. */
router.post('/login', function(req, res, next) {

	var email = req.body.email;
	var password = req.body.password;
	
	console.log('POST /login: ')
	password = crypt.createHash('md5').update(password).digest('hex');
	var getUser="select * from user where email='"+ email +"' and password='" + password +"'";
	console.log("Query is:"+getUser);

	if (email && password){		
		mysql.fetchData(function(err,results){
			if(err){
				console.log('/login mysql query'+err);
				throw err;
			}
			else 
			{
				if(results.length > 0){
					console.log("valid Login");
					//req.session.user = results[0];
					//return res.redirect('/userhome');
					return res.send('valid Login'); //label			
				}
				else {				
					console.log("user or password incorrect");
					//return res.render('index');
					return res.send('user or password incorrect'); //label				
				}
			}  
		},getUser); //mysql.fetchData(function(err,results),query)
	}else{	
		console.log('please input the email and password');
		return res.send('please input the email and password');
	}
  	//res.send('respond with a resource');
});


/* POST /users/logout. */
router.post('/logout', function(req, res, next) {
	req.session.destroy();
	res.send('logout succeed');
});

/* POST /users/register. */
router.post('/register', function(req, res, next) {

	var email = req.body.email;
	var firstname = req.body.firstname;
	var lastname = req.body.lastname;
	var password = req.body.password;
	var password_r = req.body.password_r;

	//connect to database with connection pool	
	var database = mysql.getConnection();
	console.log('1111111111111111');
	if(email && lastname && password && password_r){
		
		if(password==password_r){
			password = crypt.createHash('md5').update(password).digest('hex');
		}
		database.query('select * from user where email=?', [email], function(error,result){

			if(error){
				console.log('dbserver: /users/register query email error');
				return res.send('dbserver: /users/register query email error');
			} 
			if(result.length>0){
				return res.send('email exists');
			}else{
				var mysqldate ='';
				mysql.datetime(function(time) {
					mysqldate=time;					
				});
				
				var user={
						email: email,
						firstname: firstname,
						lastname: lastname,
						password: password,
						create_at: new Date().toISOString().slice(0, 19).replace('T', ' ')
				}
				
				database.query('insert into user set ?', user, function(error){
					if(error){
						console.log('dbserver: /users/register mywql insert into user err:'+error);
						return	res.send('dbserver: /users/register mywql insert into user err, please try again');
					}
					database.query('select * from user where email=? and password = ?', [email, password], function(error,result){
						if(error){
							console.log('dbserver: /users/register mywql select user err:'+ error);
							return	res.send('dbserver: /users/register select user err, please try again');
						}
						if(result.length ==1){
							//req.session.user = result[0]; //register successfully, return to user's homepage	
							return res.send('registered');
						}else{
							//return res.render('index');
						}						
					});
				});				
			}		
		});		
	}else{
		return res.send('fields are required'); // pass value from js to page
	}

});

	
module.exports = router;