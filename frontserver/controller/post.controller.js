var express = require('express');
var router = express.Router();
var request = require('request');
var config = require('config.json');
var multiparty = require('multiparty');
var util= require('util');
var url= require('url');

router.get('/', function (req, res) {
	//if(req.path !== '/login')
	console.log('get /post');
	if (!req.session.userId) {
		res.redirect('/users/login');
	}else{
		res.render('post');
	}
    
});
router.get('/1', function (req, res) {
    res.render('detail');
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

//test the EMAIL-URL API
router.get('/url', function (req, res) {	
	console.log('get /url');
	var userurl ={
			project : 'Scraper',
			spider : 'universalSpider',
			url : 'https://www.trulia.com/property/3274828479-223-Burning-Tree-Dr-San-Jose-CA-95119',
			email_address : 'abc@gmail.com'
	}
	
    request.post({
	        url: 'http://ec2-52-40-27-112.us-west-2.compute.amazonaws.com:6800/schedule.json?project='
	        	+ userurl.project + '&spider=' + userurl.spider
	        	+ '&url=' + userurl.url
	        	+ '&email_address=' + userurl.email_address, 
	        //form: req.form,	
	        //json: true
	    }, function (error, response, body) {
	        if (error) {
	            //return res.render('register', { error: 'An error occurred' });
	            //var retStr;// = req.param('ltitle') + req.param('ltitle');
	            //return res.send(error);
	        	console.log('error');
	        }

	        if (response.statusCode !== 200 || !response.body.success) {
	 
	        }
	        console.log('yes-200');
	        console.log(body);
	        //var j=JSON.parse(body);
	        //console.log(j.description);
	        //req.session.success = 'Registration successful'; 
	        return res.send(body);
	        //return res.redirect('/login');
	    });
});



router.post('/', function (req, res) {
    // register using api to maintain clean separation between layers
	//console.log("ltitle:"+req.param('ltitle'));
	//console.log("lbody:"+req.form());
	
//	app.post('upload', function(req, res){
//		  var type = req.get('content-type');
//		  var localReq = request({ /*  */ }); //  content-type to keep boundary
//		  req.pipe(localReq);
//		  localReq.pipe(res);
//		});
	
	var type = req.get('content-type');
	console.log(type);
	
	/*var form = new multiparty.Form();

    form.parse(req, function(err, fields, files) {
      if (err) {
        res.writeHead(400, {'content-type': 'text/plain'});
        res.end("invalid request: " + err.message);
        return;
      }
      res.writeHead(200, {'content-type': 'text/plain'});
      res.write('received fields:\n\n '+util.inspect(fields));
      res.write('\n\n');
      res.end('received files:\n\n '+util.inspect(files));
    });*/


//	var form = new multiparty.Form({
//	    encoding:"utf-8",
//	    uploadDir:"public/upload",  //
//	    keepExtensions:true  //
//	})
//
//	form.parse(req, function(err, fields, files) {
//	    var obj ={};
//	    Object.keys(fields).forEach(function(name) {
//	        console.log('name:' + name+";filed:"+fields[name]);
//	        obj[name] = fields[name];
//	    });
//
//	    Object.keys(files).forEach(function(name) {
//	        console.log('name:' + name+";file:"+files[name]);
//	        obj[name] = files[name];
//	    });
//	    console.log(">> obj:",obj);
//	    callback(err,obj);
//	});
	
    var lreq= request.post({
        url: config.awsApiUrl + '/testposting2/' + req.session.userId, //+ req.param('ltitle') + req.param('lbody'),
//        headers: [
//                  {
//                    name: 'content-type',
//                    value: 'multipart/form-data'
//                  }
//                ],
        //form: req.form,	//CAN WE SEND REQ.BODY??
        //json: true
    }, function (error, response, body) {
        if (error) {
            //return res.render('register', { error: 'An error occurred' });
            //var retStr;// = req.param('ltitle') + req.param('ltitle');
            //return res.send(error);
        }

        if (response.statusCode !== 200 || !response.body.success) {
        	
        	//var retStr = req.body.ltitle + req.body.lbody;
            //return res.send(retStr);
            
            /*return res.render('register', {
                error: response.body.msg,
                username: req.body.username,
                phonenum: req.body.phonenum,
                email: req.body.email,
            });*/
        }
        console.log('response:200');
        
        console.log('body before JSON.parse: ');
        console.log(body);
        
        var j=JSON.parse(body);
        console.log('body after JSON.parse: ');
        console.log('created listing lat:');
        console.log(j.created.address.lat);
        console.log('recommend[0].address.lat');
        console.log(j.recommend[0].address.lat);
        
        req.session.success = 'Registration successful';
        
        //return res.redirect('/detail/show');        
        return res.redirect(url.format({
            pathname:"/detail/show",
            query: {
               "created": JSON.stringify(j.created),
               "info":"newly created listing"
             }
        }));     
        
    });
    
    req.pipe(lreq);
    
 //lreq.pipe(res);
    
});

module.exports = router;