
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
    // window.scrollTo(0,0);
    $("html, body").animate({ scrollTop: 0 });
}

function advance() {
	console.log("Advancing show")
    sess.call("http://localhost/frame#advance").then(ab.log);
	get_currentimage_url();
}

function rewind() {
	console.log("Rewinding show")
    sess.call("http://localhost/frame#rewind").then(ab.log);
	get_currentimage_url();
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
            showlist();
		}
	
	    );
}

function get_currentimage_url() {
	console.log("Asking for current image url")
    sess.call("http://localhost/frame#getcurrentimage").then(
		function (jsonresult) {
			// local_currentshow.items = jQuery.parseJSON(jsonresult);
			// current_show = jsonresult;
			current_show = "<a href='"+ jsonresult + "'>" + jsonresult + "</a>"
			current_show = "<img style='max-width:100%; max-height:100%;  display: block; margin-left: auto; margin-right: auto' src='"+ jsonresult + "'>"
			
			console.log("Setting URL...");
			$('#currentImageURL').html(current_show);
			// console.log($('#currentImageURL').text());
			get_currentshow();
			getlist();
		}
	
	    );
}

function get_currentshow() {
	console.log("Asking for current show")
    sess.call("http://localhost/frame#getcurrentshow").then(
		function (jsonresult) {
			// local_currentshow.items = jQuery.parseJSON(jsonresult);
			current_show = jsonresult;
			$('#currentShow').text(jsonresult);
			console.log("Current show: " + $('#currentShow').text() );
		}
	
	    );
	
}

function showlist() {
	console.log("Showing for list MARK")

    var showlist_div = $("<div>");
	var json = { items: ['item 1', 'item 2', 'item 3'] };
	json = local_showlist;
	$(json.items).each(function(index, item) {
	    showlist_div.prepend(
	        $(document.createElement('div')).html('<button class="btn btn-large btn-block" onclick="switchshow('+ (index +1)  + ');">'+ item +'</button>')
	    );
	});
	$('div#showsList').replaceWith(showlist_div);
}

function subscribe_image() {
    console.log("Subscribing image changes");
    sess.subscribe("http://localhost/image", onImageEvent);
}

function subscribe_msg() {
    console.log("Subscribing messages");

    sess.subscribe("http://localhost/msg", onMsgEvent);
}
function subscribe_show() {
    console.log("Subscribing current show");

    sess.subscribe("http://localhost/currentshow", onShowEvent);
}


function onMsgEvent(topicUri, event) {
    
    // $('#currentImageURL').html(current_show);
    fullMsg = "";
    // frameMessage
    if (event) {
        fullMsg = '<div class="alert alert-info">' + event +  '</div>';
    }
    
    $('#frameMessage').html(fullMsg);
	
   // console.log(topicUri);
   console.log(event);
}

function onShowEvent(topicUri, event) {
   console.log("SHOW EVENT: ", event);
   $('#currentShow').text(event);

}

 
function onImageEvent(topicUri, event) {
    
    current_show = "<a href='"+ event + "'>" + event + "</a>"
	current_show = "<img style='max-width:100%; max-height:100%;  display: block; margin-left: auto; margin-right: auto' src='"+ event + "'>"
	console.log("Setting URL...");
	$('#currentImageURL').html(current_show);
	
   console.log(topicUri);
   console.log("MESSAGE ON FRAME: ", event);
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
           $('a#prog-name').css({color:'lightgreen'});

            getlist();
            get_currentshow();
            get_currentimage_url();

            subscribe_image();
            subscribe_msg();
            subscribe_show();


            console.log("Alpha-one");
		   // establish a prefix, so we can abbreviate procedure URIs ..
			// sess.prefix("calculator", "http://example.com/simple/calculator#");
		   // session.prefix("calc", "http://localhost/calc#");
      },

      // WAMP session is gone
      function (code, reason) {
          switch (reason) {
            case ab.CONNECTION_CLOSED:
               console.log("Connection was closed properly - done.");
               break;
            case ab.CONNECTION_UNREACHABLE:
               console.log("Connection could not be established.");
               break;
            case ab.CONNECTION_UNSUPPORTED:
               console.log("Browser does not support WebSocket.");
               break;
            case ab.CONNECTION_LOST:
               console.log("Connection lost - reconnecting ...");

               // automatically reconnect after 1s
               window.setTimeout(connect, 1000);
               break;
          }
         // things to do once the session fails
                 console.log("Connection is down.");
                 $('a#prog-name').css({color:'red'});
                 
      }
   );

};
