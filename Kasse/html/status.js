
statusTimeout=0
global_url="127.0.0.1:8080\status.json"

$(document).ready(function() {
	statusTimeout = setTimeout(postStatusRequest, 10000);	
});


//------------------------------------------------------------------------------
function displayStatus(data){
	var t1="<tbody>"
	t1 += "<tr>";
	t1 += "<td>Sold(All)</td>";
	t1 += "<td>"+unescape(data["itemsSold"]["count"])+"</td>";
	t1 += "</tr>";
	t1 += "<tr>";	
	t1 += "<td>Sum(All)</td>";
	t1 += "<td>"+unescape(data["itemsSold"]["sum"])+"</td>";
	t1 += "</tr>";
	t1+="</tbody>
	$("#statusOverallTableId tbody").replaceWith(txt);
	
	
	len=data["itemsSoldByPaydesk"].length()
	var t2="<tbody>"
	for(let key in data["itemsSoldByPaydesk"]){
		t2 += "<tr>";	
		t2 += "<td>"+unescape(data["itemsSoldByPaydesk"][key]["sold"])+"</td>";
		if ("sold10min" in data["itemsSoldByPaydesk"][key])
		{
			t2 += "<td>"+unescape(data["itemsSoldByPaydesk"][key]["sold10min"])+"</td>";
		}
		else
		{
			t2 += "<td>-</td>";
		}
		t2 += "</tr>";		
	t2+="</tbody>
	$("#statusPaydesks tbody").replaceWith(txt);
	
		
}
//------------------------------------------------------------------------------
function postStatusRequest(){
	var response={}	
	console.log("JSON CMD: "+global_url+" "+json_data);	
	$.ajax({
		url: "global_url,
	    type: "POST",	    
	    data: "{"action":"status"}",
	    contentType: "application/json",
	    success: function(json_response){			// successful return	    		    		    	
	    	response = JSON.parse(JSON.stringify(json_response));		// create a array out of the json response
	    	console.log(response);
	    	displayMessage(response.msg,response.error)
	    	displayStatus(response);						// refresh the cart display	    	
	    },
		error: function(json_response){				// error return
			console.log("--------------STATUS ERROR RESPONSE---------------");			
		}
	})
}
