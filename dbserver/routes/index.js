// require('rootpath')();
var express = require('express');
var router = express.Router();
var fs = require('fs');
var util= require('util');
var request = require('request');
var multiparty = require('multiparty');
var s3 = require('s3.json');
var AWS = require('aws-sdk');
var PORT = s3.PORT || 27372;
var mapConfig = require('map.json');

//connect mongodb
var mgoose = require('mongoose');
var db = mgoose.connect('connection string');  
var ObjectId = require('mongodb').ObjectID;

var mysql = require('./mysql'); // './mysql' point to mysql,js file

//mongo shema: testposting1
var schema= new mgoose.Schema({name:'string', age:'string', gender:'string'});
var Collname = mgoose.model('Collname',schema);
//mongo shema: testposting2
var listSchema= new mgoose.Schema({
  listingID: Number, 
  title: String,
  type: String,
  availableOn: Date,
  price: Number,
  description: String,
  image: [String],
  area: Number,
  bedroom: Number,
  bathroom: Number,
  laundry: String,
  parking: String,
  petOK: Boolean,
  isFurnished: Boolean,
  noSmoking: Boolean,
  rating: Number,
  wheelChairAccessiable: Boolean,
  duplicatedAddExisted: Boolean, 
  duplicatedImgExisted: Boolean,
  address: {
    region: String,
    street: String,
    city: String,
    state: String,
    lat: Number,
    lon: Number,
    zipcode: String
  },
  user: {
    id: String,
    email: String,
    contactName: String,
    phone: String
  }
}); //check Mongoose datatypes, http://mongoosejs.com/docs/schematypes.html
var Listing = mgoose.model('listing',listSchema);


//mongo shema: fraudreport
var reportSchema= new mgoose.Schema({
  listingID: String,
  negativeWords: [String],
  positiveWords: [String],
  //duplicatedListings: [ { duplicates: [String], type: String } ], //?????
  duplicatedListings: [ {} ], 
  score: Number,
  avgPrice: {
    price: Number,
    latestDate: String
  },
  listingUrl: String,
  emailAddress: String,
  priceScore: Number,
  imageScore: Number,
  addressScore: Number,
  descriptionScore: Number
});
 //check Mongoose datatypes, http://mongoosejs.com/docs/schematypes.html
var Report = mgoose.model('report', reportSchema);

/*var ProductSchema = new Schema({
name: String,
conditions:  [{}],
colors: [{}]
          });

var Product = mongoose.model('Product', productSchema);

var product = new Product({
    name: req.body.name,
    conditions: req.body.conditions,
    colors: req.body.colors
});*/



/* GET home page. */
router.get('/', function(req, res, next) {
  res.render('index', { title: 'Express' });
});

/* DELETE user listings. */
router.get('/users/deletelisting/:id', function(req, res, next) {
  console.log('get /users/deletelisting/:id, userId:' + req.params.id);

  var key = req.params.id;
  console.log('search key:' + key);

  //fraud report API 1
  Listing.remove( { _id : ObjectId(key)} ).exec(function (err, docs) {
          //var retObj = { message : 'message', body : 'body'}; 
          if(err){
            console.log('error: find /users/deletelisting/:id');
            return res.send('error: /users/deletelisting/:id');
          }
          return res.send('removed');           
        });        
  });


/* GET user listings. */
router.get('/users/mylistings/:id', function(req, res, next) {
  console.log('get /users/mylistings/:id, userId:' + req.params.id);

  var key = req.params.id;
  console.log('search key:' + key);

  //fraud report API 1
  Listing.find( { 'user.id' : key} ).exec(function (err, docs) {
          //var retObj = { message : 'message', body : 'body'}; 
          if(err){
            console.log('error: find /users/mylistings/:id');
            return res.send('error: /users/mylistings/:id');
          }
          //console.log('report found:' + doc);
          //retObj.message = "Found";
          //retObj.body = doc;
          console.log('/users/mylistings found' + docs); 

          //connect to mysql 
          var database = mysql.getConnection();
          //test db
          database.query('select * from user where email= "' + key + '"', function(err, rows, fields) {
                if(err){
                  console.log("ERROR: " + err.message);
                  return res.send("error: /users/mylistings, query user database");
                }
                else 
                { // result
                  console.log("/users/mylistings found user in mysql:"+rows);
                  return res.send({rows: rows, docs: docs});        //mongo return doc is string
                }
            });
          
        });        
  });


/* GET fraudreport. */
router.get('/fraudreport/:id', function(req, res, next) {
  console.log('get /fraudreport/:id, listingId:' + req.params.id);

  var key = req.params.id;
  console.log('search key:' + key);

  //fraud report API 1
  Report.findOne( { listingID : ObjectId(key)} ).exec(function (err, doc) {
          var retObj = { message : 'message', body : 'body'}; 
          /*if(err){
            console.log('error: find fraud report');
            return res.send('error: find fraud report');
          }*/
          if( err || !doc) {
              retObj.message = "NoFound";
              retObj.body='';
              console.log("No report found");
              return res.send( JSON.stringify(retObj));
          }else {            
            console.log('report found:' + doc);
            retObj.message = "Found";
            retObj.body = doc;
            return res.send( JSON.stringify(retObj));
          };
          
      });
});

router.post('/writereport', function(req, res, next) {
  console.log('get /fraudreport/:id, listingId:');

  //var key = req.;
  console.log('received JSON:')
  console.log(req.body);
  console.log('received listing_id:')
  //var listing = JSON.parse(req.body);
  console.log(req.body.listing_id);
  console.log('received POST /writereport');
  var j=req.body;
  
  if(j.score != undefined){
    //update mongo id's rating;
    var query = { _id: ObjectId(j.listing_id) };
    var isDuplicatedImg, isDuplicatedAdd;
    if(j.duplicated_listings[0].duplicates.length!=0){
      isDuplicatedImg =true;
    }else{
      isDuplicatedImg =false;
    }
    if(j.duplicated_listings[1].duplicates.length!=0){
      isDuplicatedAdd =true;
    }else{
      isDuplicatedAdd =false;
    }

    Listing.findOneAndUpdate(query, { rating: j.score, duplicatedAddExisted: isDuplicatedAdd, duplicatedImgExisted: isDuplicatedImg }, function (err, doc) {
      if (err){
        console.log('update rating err');
      }
      console.log('updated rating: ' + j.score);
      console.log('id score:' + j.score);
      console.log('j.dup[]:' + j.duplicated_listings);
      Report.create({
        listingID: j.listing_id,
        negativeWords: j.negative_words,
        positiveWords: j.positive_words,
        duplicatedListings: j.duplicated_listings, //?????
        score: j.score,
        avgPrice: {
          price: j.avg_price.price,
          latestDate: j.avg_price.latest_date
        },
        listingUrl: j.listing_url,
        emailAddress: j.email_address,
        priceScore: j.price_score,
        imageScore: j.image_score,
        addressScore: j.address_score,
        descriptionScore: j.description_score
      }, function (err, small) {
        if (err) {
          return console.log('creat doc: report err');
        }          
        // saved!
        console.log('report received and created')
        //console.log(small);
        console.log('saved listingId in report collection:' + ObjectId(small.listingID).valueOf());
        //curListingId = ObjectId(small.listingID).valueOf();
        return res.send('ok, received report');
      });
    }); //mongoDb updated           
     
  }

  

});

//http://54.193.92.20/api/fraud/listing/597a67a4bfd84b052193533f
/* GET listing data based on id */
/*router.get('/fraudreport/:id', function(req, res, next) {
  console.log('get /fraudreport/:id, listingId:' + req.params.id);

  var key = req.params.id;
  console.log('search key:' + key);

  //fraud report API 1
  request.get({ 
          url: 'http://54.193.92.20/api/fraud/listing/' + key,
      }, function (error, response, body) {
          if (error) {
            console.log('api 1 - fraud request: error');
          }
          if (response.statusCode !== 200) {
   
          }
          console.log('api 1 respond: 200');
          console.log(body);
          //var j=JSON.parse(body);
          //req.session.success = 'Registration successful'; 
          return res.send(body);
  });
});*/


/* GET listing data based on id */
router.get('/detail/show/:id', function(req, res, next) {
  console.log('get /detail/show/:id, listingId:' + req.params.id);

  var key = req.params.id;
  console.log('search key:' + key);

  Listing.find({ _id : ObjectId(key)}, function(err,doc){
      if(err){
        console.log('err: mongo findOne based on id()');
        return;
      }
      // RECOMMENDATION  
      var curlist = JSON.parse(JSON.stringify(doc[0], null, 4));
      var threshold = 0.1;
      var lat= curlist.address.lat;
      var lng =curlist.address.lon;
      var bedroom =curlist.bedroom;

      console.log('number record found by curobj._id:' + curListingId + ',' +doc.length);
      console.log('threshold:' + threshold + ', lat:' + lat +', lon:' + lng +', bedroom:' + bedroom);
      Listing.find({
        $or: [
               { $and: [
                  {'address.lat': {$lte : lat+threshold } }, 
                  {'address.lat': {$gte : lat-threshold } }, 
                  {'address.lon': {$lte : lng+threshold } }, 
                  {'address.lon': {$gte : lng-threshold } }
                  ] 
                },
                { bedroom: {$eq: bedroom } }
             ]         
        }).limit(10).sort({bedroom : -1}).exec(function (err, docs) {
          if(err){
            console.log('err');
            return res.send('err');;
          }
          console.log('number record found by recommendation:' + docs.length)
          docs.forEach(function(doc,index,err){
            console.log('index[' + index +']: lat:' + doc.address.lat + 'lng:' +  + doc.address.lon);
            console.log('bedroom' + doc.bedroom);
          });
          var recommend = { recommend: docs}
          return res.send(JSON.stringify({ created: doc[0], recommend: recommend }));
      });
   });

});


/* POST listing general search */
router.post('/listings/gsearch', function(req, res, next) {
  console.log('POST /listings/gsearch , listingId:' + req.query.id);

  var key = req.query.key;
  console.log('search key:' + key);

  Listing.find({
      $or: [
                {'address.street' : new RegExp(key, 'i') }, 
                {'address.zipcode' : new RegExp(key, 'i') }, 
                {'address.city' : new RegExp(key, 'i') },
                { title : new RegExp(key, 'i') } 
                // {'address.lon': {$lte : lng+threshold } }, 
                // {'address.lon': {$gte : lng-threshold } }
           ]
      }).limit(10).sort({bedroom : -1}).exec(function (err, docs) {
      if(err){
          console.log('query gsearch err');
          return;
       }
      console.log('POST /listings/gsearch , number record found:' + docs.length)
      docs.forEach(function(doc,index,err){
        console.log('index[' + index +']: lat:' + doc.address.lat + 'lng:' +  + doc.address.lon);
        console.log('bedroom' + doc.bedroom);
      });
      //send created listing and recommend listings to /post router 
      res.setHeader('Content-Type', 'application/json');
      res.send(JSON.stringify({ docs: docs }));
  });

});


/* GET recommend listing based on id */
router.get('/recommend', function(req, res, next) {
  console.log('Get /recommend , listingId:' + req.query.id);
  // RECOMMENDATION
  var threshold = 0.1;
  var lat = parseFloat(req.query.lat);
  var lng = parseFloat(req.query.lon);
  var bedroom = parseFloat(req.query.bedroom);
  console.log('threshold:' + threshold + ', lat:' + lat +', lon:' + lng +', bedroom:' + bedroom);

  Listing.find({
      $or: [
             { $and: [
                {'address.lat': {$lte : lat+threshold } }, 
                {'address.lat': {$gte : lat-threshold } }, 
                {'address.lon': {$lte : lng+threshold } }, 
                {'address.lon': {$gte : lng-threshold } }
               ] 
              },
              { bedroom: {$lte: bedroom } }
           ]       

      }).limit(10).sort({bedroom : -1}).exec(function (err, docs) {
        if(err){
          console.log('query recommendation err');
          return;
        }
      //log recommendation
      //console.log('type of docs:' + typeof(docs));
      console.log('Get /recommend , number record found by recommendation:' + docs.length)
      docs.forEach(function(doc,index,err){
        console.log('index[' + index +']: lat:' + doc.address.lat + 'lng:' +  + doc.address.lon);
        console.log('bedroom' + doc.bedroom);
      });
      //send created listing and recommend listings to /post router 
      res.setHeader('Content-Type', 'application/json');
      res.send(JSON.stringify({ recommend: docs }));
  });

});

/* INNER TEST: POST listing*/
router.post('/testposting1', function(req, res, next) {    
  Collname.create({ name: 'newsmall', age: req.body.age }, function (err, small) {
    if (err) return handleError(err);
    // saved!
    console.log(small);
    res.json(small);
  })  
});

/* POST listing: created document in mongo*/
var curListingId ='-1';
router.post('/testposting2/:id', function(req, res, next) {
  var type = req.get('content-type');
  console.log(type);

  var bucket = s3.S3_BUCKET;
  var s3Client = new AWS.S3({
    accessKeyId: s3.S3_KEY,
    secretAccessKey: s3.S3_SECRET,
    //AWS.S3 connect parameter, http://docs.aws.amazon.com/AWSJavaScriptSDK/latest/AWS/Config.html#constructor-property
  });

  var form = new multiparty.Form();  
  form.parse(req, function(err, fields, files) {
    if (err) {
      res.writeHead(400, {'content-type': 'text/plain'});
      res.end("invalid request: " + err.message);
      return;
    }
    var obj ={};
    Object.keys(fields).forEach(function(name) {
        console.log('name:' + name+";filed:"+fields[name]);
        obj[name] = fields[name];
    });
    Object.keys(files).forEach(function(name) {
        console.log('name:' + name+";file:"+files[name]);
        obj[name] = files[name];
    });
    console.log(">> obj:",obj);

    //save images to S3
    var i=-1;
    var imageUrl =[];
    var lat=37.36,lng=-121.86;
    function loopwithcb(requestGeoLocation){
      var numberImage = Object.keys(files.files).length;
      console.log("numImage:" + numberImage);
      Object.keys(files.files).forEach(function(){
      i=i+1;
      var myFile = files.files[i];
      var fileName = Date.now()+myFile.originalFilename;
      s3Client.upload({
        Bucket: bucket,
        Key: fileName,
        ACL: 'public-read',
        Body: fs.createReadStream(myFile.path)
        //ContentLength: part.byteCount
        }, function (err, data) {
        if (err) {
            //handle error
            res.send("fail to upload, check the network");
            next();
        } else {
            //handle upload complete
            var s3url = "https://s3-" + s3.region + ".amazonaws.com/" + bucket + '/' + encodeURIComponent(fileName);
            imageUrl.push(s3url);
            console.log('imageurl:'+ imageUrl);
            //delete the temp file
            fs.unlink(myFile.path);
            if(myFile.originalFilename == '') 
              imageUrl=[]; //module-multiparty defect
            if(--numberImage == 0)
              requestGeoLocation(afterSave);                           
        }
        });
      });      
    }
    function requestGeoLocation(afterSave){
      console.log("https://maps.googleapis.com/maps/api/geocode/json?address=" 
            + encodeURIComponent(fields.street) +"," + encodeURIComponent(fields.region) + "," + fields.state + "&key=" + mapConfig.googleMapKey)
      request.get({
          url: "https://maps.googleapis.com/maps/api/geocode/json?address=" 
            + encodeURIComponent(fields.street) +"," + encodeURIComponent(fields.region) + "," + fields.state + "&key=" + mapConfig.googleMapKey             
              //form: req.form,
              //json: true
          }, function (error, response, body) {
          if (error) {
              res.send("err1 cannot get LAT,LON from geocoding cloud API, check network.");
              return next();
              //return res.render('err', { error: 'An error occurred' });
          }
          if (response.statusCode !== 200 ) {            
              res.send("err2 cannot get LAT,LON from geocoding cloud API, check network. (response.statusCode !== 200)");
              return next();
          }
          console.log('response-map: 200');
          //console.log(body);
          console.log("--xx"+response.body)
          var loc=JSON.parse(body);
          console.log("latitude:" + loc.results[0].geometry.location.lat);
          console.log("longitude:" + loc.results[0].geometry.location.lng);
          lat=loc.results[0].geometry.location.lat;
          lng=loc.results[0].geometry.location.lng
          afterSave();        
      });
    }           
    function afterSave(){
      console.log('i:'+ i);      
      var curUserId = req.params.id;
      console.log('curUserId:' + curUserId)
      console.log('outside print imageurl:'+ imageUrl);
        Listing.create({ 
          title : fields.title, 
          type : fields.type,
          description : fields.description,
          availableOn : fields.availableOn,
          price : parseFloat(fields.price),
          area: parseFloat(fields.area),
          bedroom: parseInt(fields.bedroom),
          bathroom: parseFloat(fields.bathroom),
          laundry: fields.laundry,
          parking: fields.parking,
          petOK: fields.petOK==undefined? false : true,
          isFurnished: fields.isFurnished==undefined? false : true,
          noSmoking: fields.noSmoking==undefined? false : true,
          rating: -1,
          wheelChairAccessiable: fields.wheelChairAccessiable==undefined? false : true,
          image : imageUrl,
          address: {
            region : fields.region,
            street: fields.street,
            city: fields.city,
            state: fields.state,
            lat: lat,
            lon: lng,
            zipcode: fields.zipcode
          },
          user: {
            id: curUserId,            //Math.floor(Math.random()*1000),
            email: fields.email,
            contactName: fields.contactName==undefined? '' : fields.contactName,
            phone: fields.phone==undefined? '' : fields.phone
          }          
        }, function (err, small) {
          if (err) {
            return console.log('creat doc err');
          }
          // saved!
          console.log(small);
          console.log('listingId:' + ObjectId(small._id).valueOf());
          curListingId = ObjectId(small._id).valueOf();

          // RECOMMENDATION
          var threshold = 0.1;
          var lat = small.address.lat;
          var lng = small.address.lon;
          var bedroom = small.bedroom;
          console.log('type of small:' + typeof(small));
          console.log('posted listing curobj._id:' + curListingId);
          console.log('threshold:' + threshold + ', lat:' + lat +', lon:' + lng +', bedroom:' + bedroom);

          Listing.find({
            $or: [
                   { $and: [
                      {'address.lat': {$lte : lat+threshold } }, 
                      {'address.lat': {$gte : lat-threshold } }, 
                      {'address.lon': {$lte : lng+threshold } }, 
                      {'address.lon': {$gte : lng-threshold } }
                      ] 
                    },
                    { bedroom: {$lte: bedroom } }
                 ]         
            }).limit(10).sort({bedroom : -1}).exec(function (err, docs) {
              if(err){
                console.log('err');
                return;
              }
              console.log('saveAfter: number record found by recommendation:' + docs.length)
              /*//log recommendation
              console.log('type of docs:' + typeof(docs));
              console.log('number record found by recommendation:' + docs.length)
              docs.forEach(function(doc,index,err){
                console.log('index[' + index +']: lat:' + doc.address.lat + 'lng:' +  + doc.address.lon);
                console.log('bedroom' + doc.bedroom);
              });*/

              //send created listing and recommend listings to /post router 
              //res.json(small);  //will send immediately
              res.setHeader('Content-Type', 'application/json');
              res.send(JSON.stringify({ created: small, recommend: docs }));
          
              next();     //POST LISTING: send listing -objectId to Fraud Detection Module
          });       
          
        });
    }
    loopwithcb(requestGeoLocation);  //call back
        

    /*res.writeHead(200, {'content-type': 'text/plain'});
      res.write('received fields:\n\n '+util.inspect(fields));
      res.write('\n\n');
      res.end('received files:\n\n '+util.inspect(files));*/
    //res.send(obj);
    });

});
/* POST LISTING: SEND newly created listing id to Fraud dectection  */
router.post('/testposting2/:id', function(req, res, next) {
  console.log('GET http://54.193.92.20/api/fraud/listing/' + curListingId);

  //fraud report API 1
  request.get({ 
          url: 'http://54.193.92.20/api/fraud/listing/' + curListingId,
      }, function (error, response, body) {
          if (error) {
            console.log('api 1 - fraud request: error');
          }
          if (response.statusCode !== 200) {
   
          }
          console.log('api 1 respond: 200');
          console.log(body);
          return ;
          //req.session.success = 'Registration successful';           
      });//end remote: fraud report API 1
  return ;
});

/* INNER TEST: get recommendation based on id  */
router.get('/testdetail', function(request, response){
   if(curListingId !='-1'){
    Listing.find({ _id : ObjectId(curListingId)}, function(err,docs){
      if(err){
        console.log('err: mongo find()');
        return;
      }
      // RECOMMENDATION  
      var curlist = JSON.parse(JSON.stringify(docs[0], null, 4));
      var threshold = 0.1;
      var lat= curlist.address.lat;
      var lng =curlist.address.lon;
      var bedroom =curlist.bedroom;

      console.log('number record found by curobj._id:' + curListingId + ',' +docs.length);
      console.log('threshold:' + threshold + ', lat:' + lat +', lon:' + lng +', bedroom:' + bedroom);
      Listing.find({
        $or: [
               { $and: [
                  {'address.lat': {$lte : lat+threshold } }, 
                  {'address.lat': {$gte : lat-threshold } }, 
                  {'address.lon': {$lte : lng+threshold } }, 
                  {'address.lon': {$gte : lng-threshold } }
                  ] 
                },
                { bedroom: {$lte: bedroom } }
             ]         
        }).limit(10).sort({bedroom : -1}).exec(function (err, docs) {
          if(err){
            console.log('err');
            return;
          }
          console.log('number record found by recommendation:' + docs.length)
          docs.forEach(function(doc,index,err){
            console.log('index[' + index +']: lat:' + doc.address.lat + 'lng:' +  + doc.address.lon);
            console.log('bedroom' + doc.bedroom);
          });
      });
   });
  }else{
    console.log('objectId empty');
  } 
  
  response.send('OK');
  return;
  //MyModel.find({ name: 'john', age: { $gte: 18 }}, function (err, docs) {});

});

//test node.js
router.post('/test', function(request, response){
  console.log(request.body);      // your JSON
  data=[
          {"uuid": "uuidv4", "status": "whatever"},
          {"uuid": "uuidv4", "status": "great"},
          {"name":"chen","age":"11","sex":"male"}
  ]
  response.json(data);
});
module.exports = router;
