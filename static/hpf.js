
// WAMP session object
var sess;
var local_showlist = {};
var current_show = "DEFAULT";
var current_image_url = "";
var frameserver_ip = location.hostname;

function switchshow(targetshow) {
	console.log("Switching shows to " + targetshow)

	sess.call("com.hpf.switch", [targetshow]).then(console.log);


	get_currentshow();
	get_currentimage_url();
    $("html, body").animate({ scrollTop: 0 });
}

function advance() {
	console.log("Advancing show")
		console.log("SESSION" + sess)
    sess.call("com.hpf.advance").then(

			console.log(),

			function (error) {
				console.log("Call failed:", error);
				connection.close();
			}

		);
		console.log("Done advancing.")
		get_currentimage_url();
}

function rewind() {
	console.log("Rewinding show")
    sess.call("com.hpf.rewind").then(

			console.log,

			function (error) {
				console.log("Call failed:", error);
				connection.close();
			});
	get_currentimage_url();
}

function stop() {
	console.log("Stopping show")
    sess.call("com.hpf.stop").then(console.log);
}

function start() {
	console.log("Starting show")
    sess.call("com.hpf.start").then(console.log);
}
function getlist() {
		console.log("Asking for list of shows")

		sess.call("com.hpf.showlist").then(

			function (jsonresult) {
			    console.log("Received list of shows");
			    console.log(jsonresult);

	        local_showlist.items = jQuery.parseJSON(jsonresult);
	        showlist();
			}
			,

			function (error) {
				console.log("Call failed:", error);
				connection.close();
			}

	);
}

function get_currentimage_url() {
	console.log("Asking for current image url")
    sess.call("com.hpf.getcurrentimage").then(
		function (jsonresult) {
			console.log("Retrived current image URL");
			console.log(jsonresult);
			jsonresult = "http://" + frameserver_ip + ":8080" + jsonresult
			console.log(jsonresult);

			current_show = "<a href='"+ jsonresult + "'>" + jsonresult + "</a>"
			current_show = "<img style='max-width:100%; max-height:100%;  display: block; margin-left: auto; margin-right: auto' src='"+ jsonresult + "'>"
			$('#currentImageURL').html(current_show);
			get_currentshow();
			getlist();
		},
		function (error) {
			console.log("Call failed:", error);
			connection.close();
		}

	    );
}
//
function get_currentshow() {
	console.log("Asking for currently active show")

	sess.call("com.hpf.getcurrentshow").then(
		function (jsonresult) {
			current_show = jsonresult;
			$('#currentShow').text(jsonresult);
			console.log("Received current show: " + $('#currentShow').text() );
		}
	 );

}

function showlist() {
	console.log("Updating UI with fresh list of shows")

    var showlist_div = $("<div id='showsList'>");
    var showlist_list = $("<ul class='dropdown-menu pull-right'></ul>");
	json = local_showlist;
	$(json.items).each(function(index, item) {
	console.log("DEBUG");
    showlist_div.prepend(
        $(document.createElement('div')).html('<button class="btn btn-large btn-block" onclick="switchshow('+ (index +1)  + ');">'+ item +'</button>')
    );

    showlist_list.prepend(
    $(document.createElement('li')).html('<a onclick="switchshow(' + (index+1) + ')">' + item + '</a>')

    );

	});
	console.log(showlist_list);
    console.log(showlist_div);

    $('ul#showsmenu').replaceWith(showlist_list);
	$('div#showsList').replaceWith(showlist_div);
}

function subscribe_image() {
    console.log("Subscribing image changes");
			sess.subscribe('com.hpf.image', onImageEvent);

}

function subscribe_msg() {
    console.log("Subscribing messages");

    sess.subscribe("com.hpf.msg", onMsgEvent);
}
function subscribe_show() {
    console.log("Subscribing current show");

    sess.subscribe("com.hpf.currentshow", onShowEvent);
}
function subscribe_status() {
    console.log("Subscribing status changes");

    sess.subscribe("com.hpf.status", onStatusEvent);
}
function onMsgEvent(event) {

    fullMsg = "";

    if (event != "") {
        fullMsg = '<div class="alert alert-info">' + event +  '</div>';
	    console.log("MESSAGE ON FRAME: ", event);
    }
    $('#frameMessage').html(fullMsg);
}

function onStatusEvent(event) {
   console.log("Status update: ", event);
   switch(event)
   {
       case 'show-list-rebuilt':
            getlist();
            break;
        default:
            console.log("No event case matched: ", event);
   }
}


function onShowEvent(event) {
   console.log("SHOW EVENT: ", event);
   $('#currentShow').text(event);

}
//
function onImageEvent(event) {
    event = "http://" + frameserver_ip + ":8080" + event
    current_show = "<a href='"+ event + "'>" + event + "</a>"
	current_show = "<img style='max-width:100%; max-height:100%;  display: block; margin-left: auto; margin-right: auto' src='"+ event + "'>"
	console.log("Updating frame image with fresh image URL");
	$('#currentImageURL').html(current_show);

   console.log("EVENT: image changed to ", event);
}
//

hpfinit = function() {

		console.log("Program started")


    $(document).keydown(function(evt) {
        switch (evt.keyCode) {
            case 39:  advance(); break;
            case 37:  rewind(); break;

        }
        console.log(evt);
      });

    $('.dropdown-toggle').dropdown()

		var connection = new autobahn.Connection({
			url: 'ws://' + frameserver_ip + ':9000/ws',
			realm: 'hpf'}
		);
		console.log(current_show)
		console.log(connection)

		connection.onopen = function (session) {
			sess = session;
			console.log("On open..")
			var received = 0;


	    console.log("Connected!");
      $('a#prog-name').css({color:'lightgreen'});


			subscribe_image();
      subscribe_msg();
      subscribe_show();
      subscribe_status();

			// # Do these currently work?  TODO: verify each one
			getlist(); // I think so.
      get_currentshow(); // I think so now.  Fixed typo in WS call. comd vs com
      get_currentimage_url(); // Yes, looks like it.


		};

		// # These look out of place?
		console.log("Connection will be attempted")
		console.log(connection)

		connection.open();


///  INNER MARKER


/// OLD CODE FOLLOWS

  //  // connect to WAMP server
	// wsuri = "ws://" + frameserver_ip + ":9000";
	// ab.connect(wsuri,
  //     // WAMP session was established
  //        // things to do once the session has been established
	// 	function (session) {
	// 	   sess = session;
	// 	   console.log("Connected!");
  //          $('a#prog-name').css({color:'lightgreen'});
	//
  //           getlist();
  //           get_currentshow();
  //           get_currentimage_url();
	//
            // subscribe_image(session);
  //           subscribe_msg();
  //           subscribe_show();
  //           subscribe_status();
	//
	// 	   // establish a prefix, so we can abbreviate procedure URIs ..
	// 		// sess.prefix("calculator", "http://example.com/simple/calculator#");
	// 	   // session.prefix("calc", "http://localhost/calc#");
  //     },
	//
  //     // WAMP session is gone
  //     function (code, reason) {
  //         switch (reason) {
  //           case ab.CONNECTION_CLOSED:
  //              console.log("Connection was closed properly - done.");
  //              break;
  //           case ab.CONNECTION_UNREACHABLE:
  //              console.log("Connection could not be established.");
  //              break;
  //           case ab.CONNECTION_UNSUPPORTED:
  //              console.log("Browser does not support WebSocket.");
  //              break;
  //           case ab.CONNECTION_LOST:
  //              console.log("Connection lost - reconnecting ...");
	//
  //              // automatically reconnect after 1s
  //              window.setTimeout(connect, 1000);
  //              break;
  //         }
  //        // things to do once the session fails
  //                console.log("Connection is down.");
  //                $('a#prog-name').css({color:'red'});
  //
  //     }
  //  );

};
