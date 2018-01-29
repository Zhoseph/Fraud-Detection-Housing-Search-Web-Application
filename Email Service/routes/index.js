var nodemailer = require("nodemailer");
exports.request_report = function(req,res){
    res.render("request_report");
}
exports.check = function(req,res){
    res.send({"status":"OK"});
}
exports.send=function(req,res){
    var data = req.body;
    var score = "";
    if(data.score != null){
        score = data.score;
    }
    var address_score ="";
    if(data.address_score != null){
        address_score = data.address_score;
    }
    var price_score ="";
    if(data.price_score != null){
        price_score = data.price_score;
    }
    var image_score ="";
    if(data.image_score != null){
        image_score = data.image_score;
    }
    var description_score ="";
    if(data.description_score != null){
        description_score = data.description_score;
    }
    var average_price = "Not Avaliable";
    if(data.avg_price.price != null){
        average_price = data.avg_price.price;
    }
    var average_price_date = "";
    if(data.avg_price.latest_date != null){
        average_price_date = data.avg_price.latest_date;
    }
    var total_number = data.duplicated_listings[0].duplicates.length + data.duplicated_listings[1].duplicates.length;
    var listingurl = "";
    if(data.listing_url != null){
        listingurl = data.listing_url;
    }
    var pos = "";
    if(data.positive_words.length > 0){
        pos = data.positive_words[0];
        for(var i = 1; i < data.positive_words.length; i ++){
            pos += ", " +data.positive_words[i];
        }
    }
    if(pos.length == 0){
        pos = "There are no Positive Words in the listing description."
    }

    var neg = "";
    if(data.negative_words.length > 0){
        neg = data.negative_words[0];
        for(var i = 1; i < data.negative_words.length; i ++){
            neg += ", " +data.negative_words[i];
        }
    }
    if(neg.length == 0){
        neg = "There are no Negative Words in the listing description.";
    }

    var dup =  "";
    console.log("current length: " + data.duplicated_listings[0].duplicates.length + " Type: " + data.duplicated_listings[0].type);
    if(data.duplicated_listings[0].duplicates.length > 0){
        var type = data.duplicated_listings[0].type;
        dup += "<tr><td height='12'></td></tr><tr><td style='color:#EC7063;font-weight:500;line-height:1.25!important;line-height:1.25;vertical-align:middle'>Duplicate Type : " +type +" duplicate</td></tr>";
        for(var i = 0; i < data.duplicated_listings[0].duplicates.length; i ++){
            var add = data.duplicated_listings[0].duplicates[i];
            var num = i + 1;
            dup += "<tr><td style='width:100%;height:auto;display:block;font-weight:500;'><p>" + num + ". <a href = ' " + add +" '>" + add +"</a></p></td></tr>"
        }
    }
    if(data.duplicated_listings[1].duplicates.length > 0){
        var type = data.duplicated_listings[1].type;
        dup += "<tr><td height='24'></td></tr><tr><td style='color:#EC7063;font-weight:500;line-height:1.25!important;line-height:1.25;vertical-align:middle'>Duplicate Type : " + type +" duplicate</td></tr>";
        for(var i = 0; i < data.duplicated_listings[1].duplicates.length; i ++){
            var add = data.duplicated_listings[1].duplicates[i];
            var num = i + 1;
            dup += "<tr><td style='width:100%;height:auto;display:block;font-weight:500;'><p>" + num + ". <a href = ' " + add +" '>" + add +"</a></p></td></tr>"
        }
    }
    if(dup.length ==0){
        dup = "We could not find any duplicated listings for the submitted listing URL on Craigslist, Trulia, Hotpads and Apartments.com.";
    }


    var transporter = nodemailer.createTransport({
        service: "Gmail",
        auth: {
            user: "user@gmail.com",
            pass: "pwd"
        }
    });
    var mailOptions = {
        from: 'coconutJelly918@gmail.com',
        to: data.email_address,
        subject: 'Fraud Report is Ready ✔', // Subject line
        html: '<!DOCTYPE html>\
        <html>\
        <head>\
        <meta charset="UTF-8">\
        <title>Fraud Report</title>\
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/normalize/5.0.0/normalize.min.css">\
        <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap.min.css">\
        <script src="https://ajax.googleapis.com/ajax/libs/jquery/3.2.1/jquery.min.js"></script>\
        <script src="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/js/bootstrap.min.js">\
        <script src="https://cdnjs.cloudflare.com/ajax/libs/prefixfree/1.0.7/prefixfree.min.js"></script>\
        </head>\
        <body>\
        <div>\
        <table width="750" border="0" cellpadding="0" cellspacing="0" align="center" class="m_-2337546958194283536mobile" style="vertical-align:top;border-collapse:collapse">\
        <tbody>\
        <tr>\
        <td width="750" align="center">\
        <table width="415" cellspacing="0" cellpadding="0" border="0" align="center" valign="middle" class="m_-2337546958194283536fullCenter">\
        <tbody>\
        <tr>\
        <td valign="top" align="left"></td>\
        </tr>\
        <tr>\
        <td width="20" valign="top" align="left" style="width:20px"></td>\
        <td class="m_-2337546958194283536banner-bg" valign="top" align="center" style="border-collapse:collapse">\
        <table width="690" cellspacing="0" cellpadding="0" border="0" align="center" valign="middle" class="m_-2337546958194283536fullCenter">\
        <tbody>\
        <tr>\
        <td width="100%" align="center">\
        <p style="font-size:12px;text-align:center;line-height:2.5!important;line-height:2.5;font-weight:300">This is your Fraud Assessment report.</p>\
    </td>\
    </tr>\
    </tbody>\
    </table>\
    </td>\
    <td width="20" valign="top" align="left" style="width:20px"></td>\
        </tr>\
        </tbody>\
        </table>\
        </td>\
        </tr>\
        </tbody>\
        </table>\
        <table width="750" border="0" cellpadding="0" cellspacing="0" align="center" class="m_-2337546958194283536mobile" bgcolor="1ec089" style="background-color:#1ec089;vertical-align:top;border-collapse:collapse">\
        <tbody>\
        <tr>\
        <td width="750" align="center">\
        <table width="415" cellspacing="0" cellpadding="0" border="0" align="center" valign="middle" class="m_-2337546958194283536fullCenter">\
        <tbody>\
        <tr>\
        <td width="20" valign="top" align="left" style="width:20px"></td>\
        <td class="m_-2337546958194283536banner-bg" valign="top" align="center" style="border-collapse:collapse">\
        <table width="690" cellspacing="0" cellpadding="0" border="0" align="center" valign="middle" class="m_-2337546958194283536fullCenter">\
        <tbody>\
        <tr>\
        <td height="30"></td>\
        </tr>\
        <tr>\
        <td width="100%" align="center">\
        <a class="m_-2337546958194283536logolnk" href=""><img border="0" class="m_-2337546958194283536f-logo CToWUd" height="140" src="http://bosorganization.com/images/icon-house.png" style="height:140px;width:140px"></a>\
        </td>\
        </tr>\
        <tr>\
        <td height="30"></td>\
        </tr>\
        </tbody>\
        </table>\
        </td>\
        <td width="20" valign="top" align="left" style="width:20px"></td>\
        </tr>\
        </tbody>\
        </table>\
        </td>\
        </tr>\
        </tbody>\
        </table>\
        <table width="750" border="0" cellpadding="0" cellspacing="0" align="center" class="m_-2337546958194283536mobile" bgcolor="1ec089" style="background-color:#1ec089;vertical-align:top;border-collapse:collapse">\
        <tbody>\
        <tr>\
        <td width="750" align="center">\
        <table width="415" cellspacing="0" cellpadding="0" border="0" align="center" valign="middle" class="m_-2337546958194283536fullCenter">\
        <tbody>\
        <tr>\
        <td width="20" valign="top" align="left" style="width:20px"></td>\
        <td class="m_-2337546958194283536banner-bg" valign="top" align="center">\
        <table width="690" cellspacing="0" cellpadding="0" border="0" align="center" valign="middle" class="m_-2337546958194283536fullCenter" style="border-collapse:collapse">\
        <tbody>\
        <tr>\
        <td bgcolor="4f5f6a" style="background-color:#4f5f6a;border-top-left-radius:5px;border-top-right-radius:5px" align="center">\
        <table>\
        <tbody>\
        <tr>\
        <td height="4"></td>\
        </tr>\
        </tbody>\
        </table>\
        </td>\
        </tr>\
        <tr>\
        <td bgcolor="ffffff" style="background-color:#fff" align="center">\
        <table>\
        <tbody>\
        <tr>\
        <td height="20"></td>\
        </tr>\
        <tr>\
        <td>\
        </table>\
        </td>\
        </tr>\
        </tbody>\
        </table>\
        </td>\
        </tr>\
        </tbody>\
        </table>\
        <table width="750" border="0" cellpadding="0" cellspacing="0" align="center" class="m_-2337546958194283536mobile" bgcolor="f4f4f1" style="background-color:#f4f4f1;vertical-align:top;border-collapse:collapse">\
        <tbody>\
        <tr>\
        <td width="750" align="center">\
        <table width="415" cellspacing="0" cellpadding="0" border="0" align="center" valign="middle" class="m_-2337546958194283536fullCenter">\
        <tbody>\
        <tr>\
        <td width="20" valign="top" align="left" style="width:20px"></td>\
        <td bgcolor="f4f4f1" style="background-color:#fff" align="center">\
        <table width="690" cellspacing="0" cellpadding="0" border="0" align="center" valign="middle" class="m_-2337546958194283536fullCenter">\
        <tbody>\
        <tr>\
        <td height="35"></td>\
        </tr>\
        <tr>\
        <td>\
        <table width="100%" style="font-weight:300;text-align:left">\
        <tbody>\
        <tr>\
        <td width="30" valign="top" align="left" style="width:30px"></td>\
        <td align="center" style="border-bottom:solid 1px #bbb;text-align:center;font-family:Helvetica,Verdana,sans-serif;font-weight:300">\
        <p style="font-size:24px;line-height:1.75!important;line-height:1.75;letter-spacing:1px">Fraud Assessment Report</p>\
    </td>\
    <td width="30" valign="top" align="left" style="width:30px"></td>\
    </tr>\
        <tr>\
            <td height="15"></td>\
        </tr>\
        <tr>\
        <td width="30" valign="top" align="left" style="width:30px"></td>\
        <td align="center" style="text-align:left">\
<table width="100%" style="font-size:18px;text-align:left;line-height:2!important;line-height:2" cellspacing="0" cellpadding="0" border="0">\
    <tbody>\
        <tr>\
            <td style="color:#85929E;font-weight:800;line-height:1.25!important;line-height:1.25;vertical-align:top"> Listing URL : </td>\
        </tr>\
        <tr><td style="width:100%;display:block;font-weight:400;line-height:1.25!important;line-height:1.25;vertical-align:top"><p><a href = " ' + listingurl +'">' + listingurl +'</a></p></td>\
            <td style = "width = 0%"></td>   \
        </tr>\
        <tr>\
            <td height="12"></td>\
        </tr>\
        <tr>\
            <td style="color:#85929E;font-weight:800;line-height:1.25!important;line-height:1.25;vertical-align:top"> Total Score : </td>\
        </tr>\
        <tr>\
            <td height="12"></td>\
        </tr>\
        <tr>\
            <td style="color:#F1948A;font-weight:400;text-align:left;line-height:1.25!important;line-height:1.25;vertical-align:top"> ' + score + '<br>&nbsp;&nbsp;</td>\
        </tr>\
        <tr>\
            <td height="12"></td>\
        </tr>\
        <tr>\
            <td style="color:#85929E;font-weight:800;line-height:1.25!important;line-height:1.25;vertical-align:top"> Description Score : </td>\
        </tr>\
        <tr>\
            <td height="12"></td>\
        </tr>\
        <tr>\
            <td style="color:#F1948A;font-weight:400;text-align:left;line-height:1.25!important;line-height:1.25;vertical-align:top"> ' + description_score + '<br>&nbsp;&nbsp;</td>\
        </tr>\
        <tr>\
            <td height="12"></td>\
        </tr>\
        <tr>\
            <td style="color:#85929E;font-weight:800;line-height:1.25!important;line-height:1.25;vertical-align:top"> Price Score : </td>\
        </tr>\
        <tr>\
            <td height="12"></td>\
        </tr>\
        <tr>\
            <td style="color:#F1948A;font-weight:400;text-align:left;line-height:1.25!important;line-height:1.25;vertical-align:top"> ' + price_score + '<br>&nbsp;&nbsp;</td>\
        </tr>\
        <tr>\
            <td height="12"></td>\
        </tr>\
        <tr>\
            <td style="color:#85929E;font-weight:800;line-height:1.25!important;line-height:1.25;vertical-align:top"> Image Score : </td>\
        </tr>\
        <tr>\
            <td height="12"></td>\
        </tr>\
        <tr>\
            <td style="color:#F1948A;font-weight:400;text-align:left;line-height:1.25!important;line-height:1.25;vertical-align:top"> ' + image_score + '<br>&nbsp;&nbsp;</td>\
        </tr>\
        <tr>\
            <td height="12"></td>\
        </tr>\
        <tr>\
            <td style="color:#85929E;font-weight:800;line-height:1.25!important;line-height:1.25;vertical-align:top"> Address Score : </td>\
        </tr>\
        <tr>\
            <td height="12"></td>\
        </tr>\
        <tr>\
            <td style="color:#F1948A;font-weight:400;text-align:left;line-height:1.25!important;line-height:1.25;vertical-align:top"> ' + address_score + '<br>&nbsp;&nbsp;</td>\
        </tr>\
        <tr>\
            <td height="12"></td>\
        </tr>\
        <tr>\
            <td style="color:#85929E;font-weight:800;line-height:1.25!important;line-height:1.25;vertical-align:top"> Positive Words In The Description Are :</td>\
        </tr>\
        <tr>\
            <td height="12"></td>\
        </tr>\
        <tr>\
            <td style="color:#2ECC71;font-weight:400;text-align:left;line-height:1.25!important;line-height:1.25;vertical-align:top"> ' + pos + '<br>&nbsp;&nbsp;</td>\
        </tr>\
        <tr>\
            <td height="12"></td>\
        </tr>\
        <tr>\
            <td style="color:#85929E;font-weight:800;line-height:1.25!important;line-height:1.25;vertical-align:top"> Negative Words In The Description Are :</td>\
        </tr>\
        <tr>\
            <td height="12"></td>\
        </tr>\
        <tr>\
            <td style="color:#F1948A;font-weight:400;text-align:left;line-height:1.25!important;line-height:1.25;vertical-align:top"> ' + neg + '<br>&nbsp;&nbsp;</td>\
        </tr>\
        <tr>\
            <td height="12"></td>\
        </tr>\
        <tr>\
            <td style="color:#85929E;font-weight:800;line-height:1.25!important;line-height:1.25;vertical-align:top">Latest Average Rent Price Based On Data Obtained On ' + average_price_date +' Is :</td>\
        </tr>\
        <tr>\
            <td height="12"></td>\
        </tr>\
        <tr>\
            <td style="color:#F1948A;font-weight:400;text-align:left;line-height:1.25!important;line-height:1.25;vertical-align:top"> $ ' + average_price + '<br>&nbsp;&nbsp;</td>\
        </tr>\
        <tr>\
            <td height="60"></td>\
        </tr>\
    </tbody>\
</table>\
     <tr>\
        <td height="25"></td>\
    </tr>\
    <tr>\
        <td width="30" valign="top" align="left" style="width:30px"></td>\
        <td align="center" style="border-bottom:solid 1px #bbb;text-align:left">\
            <p style="font-size:24px;text-align:center;line-height:1.75!important;line-height:1.75;font-weight:300;letter-spacing:1px">Duplicated Listings</p>\
        </td>\
        <td width="30" valign="top" align="left" style="width:30px"></td>\
    </tr>\
    <tr>\
        <td height="15"></td>\
    </tr>\
        <tr>\
        <td width="30" valign="top" align="left" style="width:30px"></td>\
        <td align="center" style="text-align:left">\
        <table width="100%" style="font-size:18px;text-align:left;line-height:1!important;line-height:1" cellspacing="0" cellpadding="0" border="0">\
        <tbody>\
        <tr>\
        <td style="color:#85929E;font-weight:700;text-transform:uppercase;line-height:1.25!important;line-height:1.25;vertical-align:top">TOTAL NUMBER:</td>\
        <td style="color:#F1948A;font-weight:500;text-align:right;line-height:1.25!important;line-height:1.25;vertical-align:top">' + total_number + '</td>\
        </tr>' + dup + '\
        </tbody>\
        </table>\
        </td>\
        <td width="30" valign="top" align="left" style="width:30px"></td>\
        </tr>\
        <tr>\
        <td height="15"></td>\
        </tr>\
        </tbody>\
        </table>\
        </td>\
        </tr>\
        <tr>\
        <td height="15"></td>\
        </tr>\
        <tr>\
        <td>\
        <table width="100%">\
        <tbody>\
        <tr>\
        <td width="30" valign="top" align="left" style="width:30px"></td>\
        <td align="center">\
        <p style= "font-family:Helvetica,Verdana,sans-serif;color:#a4a4a4;font-size:12px;text-align:center;line-height:1.25!important;line-height:1.25;font-weight:700"> To find any possible duplicated listings, we search listings posted on Craigslist, Trulia, Hotpads, and Apartments.com. We will extend this list in the future versions of our fraud detection service.</p>\
    </td>\
    <td width="30" valign="top" align="left" style="width:30px"></td>\
        </tr>\
        </tbody>\
        </table>\
        </td>\
        </tr>\
        <tr>\
        <td height="10"></td>\
        </tr>\
        </tbody>\
        </table>\
        </td>\
        <td width="20" valign="top" align="left" style="width:20px"></td>\
        </tr>\
        </tbody>\
        </table>\
        </td>\
        </tr>\
        </tbody>\
        </table>\
        <table width="750" border="0" cellpadding="0" cellspacing="0" align="center" class="m_-2337546958194283536mobile" bgcolor="f4f4f1" style="background-color:#f4f4f1;vertical-align:top;border-collapse:collapse">\
        <tbody>\
        <tr>\
        <td width="750" align="center">\
        <table width="415" cellspacing="0" cellpadding="0" border="0" align="center" valign="middle" class="m_-2337546958194283536fullCenter" bgcolor="e6e6e6" style="background-color:#e6e6e6">\
        <tbody>\
        <tr>\
        <td width="20" valign="top" align="left" style="width:20px"></td>\
        <td align="center">\
        <table width="690" cellspacing="0" cellpadding="0" border="0" align="center" valign="middle" class="m_-2337546958194283536fullCenter">\
        <tbody>\
        <tr>\
        <td>\
        <table width="100%" cellspacing="0" cellpadding="0" border="0" align="center" valign="middle" class="m_-2337546958194283536fullCenter">\
        <tbody>\
        <tr>\
        <td align="center">\
        <img src="https://ci3.googleusercontent.com/proxy/HzK05Acrkm9pHcWRx5MFzRaAsT-nlnhaFhtYvswCBqlZnsNTU3pLatE28HkDcak0d6gN7XKbdPwchKcHfcslYZwLr7S0Rcn_Ga3LhwOxc56pe92cr5ChXVV5j_zzxiTuTjMfW4Xa=s0-d-e1-ft#https://dbmgns9xjyk0b.cloudfront.net/email-content/receipt-bottom-edge-white.png" style="width:100%;height:auto;display:block" class="CToWUd">\
        </td>\
        </tr>\
        </tbody>\
        </table>\
        </td>\
        </tr>\
        <tr>\
        <td height="15"></td>\
        </tr>\
        <tr>\
        <td>\
        <table width="100%">\
        <tbody>\
        <tr>\
        <td width="30" valign="top" align="left" style="width:30px"></td>\
        <td align="center" style="border-bottom:solid 1px #bbb;text-align:left">\
        <p style="font-size:24px;text-align:center;line-height:1.75!important;line-height:1.75;font-weight:300;letter-spacing:1px">Information</p>\
        </td>\
        <td width="30" valign="top" align="left" style="width:30px"></td>\
        </tr>\
        <tr>\
        <td width="30" valign="top" align="left" style="width:30px"></td>\
        <td align="center" style="text-align:center;font-family:Helvetica,Verdana,sans-serif;font-weight:300;color:#35b5dc">\
        <p style="font-weight:500;font-size:15px;line-height:1!important;line-height:1">CMPE 295B Team3 - One Washinton Square, San Jose, CA 95122</p>\
    <p style="font-weight:500;font-size:15px;line-height:1!important;line-height:1">You have received this email in response to your fraud report request submitted on our website.</p>\
    </td>\
    <td width="30" valign="top" align="left" style="width:30px"></td>\
        </tr>\
        <tr>\
        <td height="35"></td>\
        </tr>\
        </tbody>\
        </table>\
        </td>\
        </tr>\
        </tbody>\
        </table>\
        </td>\
        <td width="20" valign="top" align="left" style="width:20px"></td>\
        </tr>\
        </tbody>\
        </table>\
        </div>\
        </body>\
        </html>' // html body
    };
    transporter.sendMail(mailOptions, function(err, response){
        if(err){
            console.log('ERROR!');
            return res.send('ERROR');
        }
        res.send({"status":"OK"});
    });
    console.log("Succeed");
}