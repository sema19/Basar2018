
inputTimeout=0
var cartId = 1
var cartItems=[]
var cartsAvailable=[]
var cartObsolete=false;
var cart={"id":0, "items":[], "sum":0.0, "msg":"", "status":"undefined"}

$(document).ready(function() {
	//syncTimeout = setTimeout(syncTimer, 8000);
	postJsonCartResponse("update", {"id":cart["id"]})
});

$(function(){
		
	//----------------------------------- input field control
	$("#eingabeId").keyup(function() {			
		if (inputTimeout>0){			
	       	clearTimeout(inputTimeout);					// stop timeout if it was running 
	    }		
		var inputLen = $("#eingabeId").val().length;	// get length of barcode		
	
		if (inputLen == 8) {
	       	var barcode = $("#eingabeId").val();
	       	postJsonCartResponse("barcode",{"id":cart["id"], "bc":barcode})
	       	//addToCart(barcode)			
	       	$("#eingabeId").val("");					// reset the input field
	    } else if (inputLen > 8) {						// error case too many characters
	       	$("#eingabeId").val("");
	    } else if (inputLen > 0) {						// between 1 and 8 characters -> run timeout
	       	console.log("Input: "+inputLen);
	       	inputTimeout = setTimeout(function(){
	       		$("#eingabeId").val("");      			// reset input value by timeout  		
	     	}, 5000);
	    }
		
	});
	$("#btnCheckout").click(function(){				
		postJsonCartResponse("sold", {"id":cart["id"]})
	})
	$("#btnRefresh").click(function(){		
		postJsonCartResponse("update", {"id":cart["id"]})
	})
	$("#btnDelLast").click(function(){		
		postJsonCartResponse("delLast", {"id":cart["id"]})
	})
	$("#btnDelCart").click(function(){		
		postJsonCartResponse("delCart", {"id":cart["id"]})
	})
});

//------------------------------------------------------------------------------
function displayCart(cart)
{
	console.log("-------------- FUNCT: DisplayCart -----------");
	var sum=0;
	console.log(cart["items"]);
	var cartId=cart["id"];
	var cartStatus=cart["status"];
	var len = cart["items"].length;
	console.log(cart["items"]);
	var txt="<tbody>";
	for(var i=len-1;i>=0;i--){
		console.log("CART ITEM");
		console.log(i);
		console.log(cart["items"][i]);
		var pos = i+1;
    	txt += "<tr>";
    	txt += "<td>"+pos+"</td>";
    	txt += "<td>"+cart["items"][i].bc+"</td>";
    	txt += "<td>"+unescape(cart["items"][i].txt)+"</td>";		// unescape to allow ü,ö ...
    	var price = parseFloat(cart["items"][i].price).toFixed(2); 
    	priceTxt=price.toString();
    	txt += "<td>"+priceTxt+"</td>";
    	//txt += "<td>"+cart["items"][i].price+"</td>";
    	txt += "</tr>";
    	sum += parseFloat(cart["items"][i].price);
	}
	txt+="</tbody>";
	$("#cartTableId tbody").replaceWith(txt);
	$("#sumId").html(sum.toFixed(2)+"€");	
}


//------------------------------------------------------------------------------
function displayMessage(msg, error)
{
	console.log("-------------- FUNCT: DisplayCart -----------");
	try{
		if (error!=0){
			$("#errMsgId").html(unescape(msg)).css({background:"red",color:"yellow"});
		}else{
			if (msg!="") {
				$("#errMsgId").html(unescape(msg)).css({background:"grey",color:"lime"});
			}else{
				$("#errMsgId").html(unescape(msg)).css({background:"grey",color:"lime"});
			}
		}
	}
	catch(e)
	{
		alert(e+"\nFunktion konnte nicht ausgeführt werden. Bitte verständigen sie ihren Administrator");	
	}
}

//------------------------------------------------------------------------------
function postJsonCartResponse(url, data){
	var response={}
	json_data=JSON.stringify(data);
	console.log("JSON CMD: "+url+" "+json_data);	
	$.ajax({
		url: url,
	    type: "POST",	    
	    data: json_data,
	    //accept: "*/*",
	    contentType: "application/json",
	    //crossDomain: false,
	    //beforeSend: function( xhr ) {
	    //    xhr.setRequestHeader('X-Requested-With', {toString: function(){ return ''; }});
	    //  },
	    success: function(json_response){			// successful return	    	
	    	console.log("Response Update");
	    	console.log(json_response);
	    	response = JSON.parse(JSON.stringify(json_response));		// create a array out of the json response
	    	console.log(response);
	    	displayMessage(response.msg,response.error)
	    	displayCart(response);						// refresh the cart display	    	
	    },
		error: function(json_response){				// error return
			console.log("--------------BARCODE ERROR RESPONSE---------------");
			console.log(json_response);
			response = JSON.parse(JSON.stringify(json_response)).responseText;		// create a array out of the json response
	    	console.log(response);
			displayMessage(response.msg,response.error)
			displayCart(response);						// refresh the cart display
		}
	})
}
