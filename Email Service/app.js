var express = require('express');
var path = require('path');
var favicon = require('serve-favicon');
var logger = require('morgan');
var cookieParser = require('cookie-parser');
var bodyParser = require('body-parser');
var http = require("http");
var index = require('./routes/index');
var users = require('./routes/users');
//var html = require('html');
var app = express();

// view engine setup
app.set('views', path.join(__dirname, 'views'));
app.set('view engine', 'ejs');

// uncomment after placing your favicon in /public
//app.use(favicon(path.join(__dirname, 'public', 'favicon.ico')));
app.use(logger('dev'));
app.use(bodyParser.json());
app.use(bodyParser.urlencoded({ extended: false }));
app.use(cookieParser());
app.use(express.static(path.join(__dirname, 'public')));



// catch 404 and forward to error handler


// error handler
app.use(function(err, req, res, next) {
  // set locals, only providing error in development
  res.locals.message = err.message;
  res.locals.error = req.app.get('env') === 'development' ? err : {};

  // render the error page
  res.status(err.status || 500);
  res.render('error');
});
app.get('/request_report',index.request_report);
app.get('/check', index.check);
app.post('/fraud_report',index.send);
var httpServer = require('http').createServer(app);
httpServer.listen(8888, function() {
    console.log('stock_recom_backend running on port ' + 8888 + '.');
});
console.log('Server running at http://127.0.0.1:8888/');
// 终端打印如下信息

module.exports = app;
