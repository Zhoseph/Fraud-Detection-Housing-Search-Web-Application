var express = require('express');
var router = express.Router();

// use session auth to secure the angular app files
router.use('/', function (req, res, next) {
	console.log('use /');
	/*if (req.path !== '/login' && !req.session.userId) {
        return res.redirect('/users/login');
    }*/
	//return res.render('index', {userId : req.session.userId});
	return res.render('index');
});

// make JWT token available to angular app
router.get('/token', function (req, res) {
    res.send(req.session.token);
});

// serve angular app files from the '/app' route
router.use('/', express.static('app'));

module.exports = router;