var ejs= require('ejs');
var mysql = require('mysql');

//Put your mysql configuration settings - user, password, database and port
function getConnection(){
	
	//use connection pool	
	var pool = mysql.createPool({
	    host     : 'localhost',
	    connectionLimit : 5000,
	    max_connections  : 5000,
	    acquireTimeout : 100000,
	    connectTimeout : 100000,
	    user     : 'user',
	    password : 'pwd',
	    database : 'listinguser',
	    port	 : 3306,
	    supportBigNumbers: true,
	    bigNumberStrings: true
	});
	return pool;
	
	//no use connection pool
	/*
	var connection = mysql.createConnection({
	    host     : 'localhost',
	    user     : 'root',
	    password : '23001288',
	    database : 'twitter_db',
	    port	 : 3306
	});
	return connection;
	*/
}


function fetchData(callback,sqlQuery){
	
	console.log("\nSQL Query::"+sqlQuery);
	var connection=getConnection();
	
	connection.query(sqlQuery, function(err, rows, fields) {
		if(err){
			console.log("ERROR: " + err.message);
		}
		else 
		{	// result
			console.log("DB Results:"+rows);
			callback(err, rows);
		}
	});
	console.log("\nConnection closed..");
	//connection.end();
}	

function datetime(result){
	var date = new Date();
	var year, month, day, hours, minutes, seconds;
	
	year = String(date.getFullYear());
	month = String(date.getMonth());
	if(month.length == 1){
		month = "0"+month;
	}
	
	day = String(date.getDate());
	if(day.length == 1){
		day = "0"+day;
	}
	
	hours = String(date.getHours());
	if(hours.length == 1){
		hours = "0"+hours;
	}
	
	minutes = String(date.getMinutes());
	if(minutes.length == 1){
		minutes = "0"+minutes;
	}
	
	seconds = String(date.getSeconds());
	if(seconds.length == 1){
		seconds = "0"+seconds;
	}
	
	result(year + "-" + month + "-" + day + " " + hours + ":" + minutes + ":" + seconds);	
}	

exports.getConnection=getConnection;
exports.datetime=datetime;
exports.fetchData=fetchData;