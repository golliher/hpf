
// WAMP session object
var sess;
var local_showlist = {};
var current_show = "DEFAULT";
var current_image_url = "";

function switchshow(targetshow) {
	console.log("Switching shows to " + targetshow)
    sess.call("http://localhost/frame#switch", targetshow).then(ab.log);
	get_currentshow();
	get_currentimage_url();
}

function advance() {
	console.log("Advancing show")
    sess.call("http://localhost/frame#advance").then(ab.log);
	get_currentimage_url();
}

function rewind() {
	console.log("Rewinding show")
    sess.call("http://localhost/frame#rewind").then(ab.log);
}

function stop() {
	console.log("Stopping show")
    sess.call("http://localhost/frame#stop").then(ab.log);
}

function start() {
	console.log("Starting show")
    sess.call("http://localhost/frame#start").then(ab.log);
}
function getlist() {
	console.log("Asking for list")
    sess.call("http://localhost/frame#showlist").then(
		function (jsonresult) {
			local_showlist.items = jQuery.parseJSON(jsonresult);
			console.log("Initialized shows with: " + local_showlist);
            showlist();
		}
	
	    );
}

function get_currentimage_url() {
	console.log("Asking for current image url")
    sess.call("http://localhost/frame#getcurrentimage").then(
		function (jsonresult) {
			console.log("MARK ONE");
			// local_currentshow.items = jQuery.parseJSON(jsonresult);
			// current_show = jsonresult;
			current_show = "<a href='"+ jsonresult + "'>" + jsonresult + "</a>"
			current_show = "<img width='300' src='"+ jsonresult + "'>"
			
			console.log("MARK TWO: " + current_show);
			console.log("Setting URL...");
			$('#currentImageURL').html(current_show);
			// console.log($('#currentImageURL').text());
		}
	
	    );
}

function get_currentshow() {
	console.log("Asking for current show")
    sess.call("http://localhost/frame#getcurrentshow").then(
		function (jsonresult) {
			console.log("MARK ONE");
			// local_currentshow.items = jQuery.parseJSON(jsonresult);
			current_show = jsonresult;
			console.log("MARK TWO: " + jsonresult);
			$('#currentShow').text(jsonresult);
			console.log($('#currentShow').text());
		}
	
	    );
	
}

function showlist() {
	console.log("Showing for list MARK")
    console.log(local_showlist)

    var ul = $("<ul>");
	var json = { items: ['item 1', 'item 2', 'item 3'] };
	json = local_showlist;
    // console.log("Faked json");
	console.log(json)
	$(json.items).each(function(index, item) {
	    ul.prepend(
	        $(document.createElement('div')).html('<button onclick="switchshow('+ (index +1)  + ');">'+ item +'</button><hr>')
	    );
	});
    // ul.appendTo('body');
	$('div#showsList').replaceWith(ul);
}

hpfinit = function() {

   // connect to WAMP server
	wsuri = "ws://" + window.location.hostname + ":9000";
	// wsuri = "ws://192.168.4.77:9000";
	ab.connect(wsuri,
      // WAMP session was established
         // things to do once the session has been established
		function (session) {
		   sess = session;
		   console.log("Connected!");

            // getlist();
            // get_currentshow();
            // get_currentimage_url();

		   // establish a prefix, so we can abbreviate procedure URIs ..
			// sess.prefix("calculator", "http://example.com/simple/calculator#");
		   // session.prefix("calc", "http://localhost/calc#");
      },

      // WAMP session is gone
      function (code, reason) {
         // things to do once the session fails
      }
   );

};
