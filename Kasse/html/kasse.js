/**
 * 
 */

console.log("Load kasse.js")

cart = {"id":5,"items":["3001,3002","3003"]};

function onAddItem()
{
	console.log("onAddItem")
	var xmlhttp = new XMLHttpRequest();   // new HttpRequest instance	
	console.log("Post")
	xmlhttp.open("POST", "/cart");
	xmlhttp.setRequestHeader("Content-Type", "application/json");
	console.log("Send Cart");
	console.log(cart);		
	xmlhttp.send(JSON.stringify(cart));	
	console.log("Send done");
}