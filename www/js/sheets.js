
function Sheet() {
	this.set = function(x, y, value) {
		var target = $("#sheet td").find("[data-x=" + x + "][data-y=" + y + "]");
		target.val(value);
	}
}

$(function() {

	var sheet = new Sheet();
	var ws = new WebSocket("ws://localhost:8888/ws/sheet");
	ws.onopen = function() {
		ws.send(JSON.stringify({
			"a": "listen",
			"sheetid": sheetid
		}));
	}

	ws.onmessage = function(evt) {
		console.log(evt.data);
		var data = jQuery.parseJSON(evt.data);
		switch(data.a) {
			case "c":
				// Update cell
				sheet.set(data.x, data.y, data.v);
				break;
			case "m":
				console.log(data.m);
				break;
		}
	};
	$('#sheet_title').change(function() {
		var title = $(this).val();
		var input = $(this)

		input.addClass('updating');

		jQuery.post('/sheet/' + sheetid, {"a":"t", "t":title}).done(function() {
			document.title = input.val();
			input.removeClass('updating');
		})
	});

	$('#sheet')
	.on("change", "input",function() {
		var input = $(this);
		var x = input.data('x');
		var y = input.data('y');
		var v = input.val();
		input.addClass('updating');
		
		jQuery.post('/sheet/' + sheetid, {"a":"c", "x":x, "y":y, "v":v}).done(function() {
			input.removeClass('updating');
		});
	})
	.on("keydown", "input", function(e){
		var x = $(this).data('x');
		var y = $(this).data('y');
		switch( e.keyCode ) {
			case 40:
				y++;
				break;
			case 38:
				y--;
				break;
			case 37:
				x--;
				break;
			case 39:
				x++;
				break;
			case 13:
				y++;
				break;
			default:
				return;
		}
		if( Math.min(x,y) >= 0 ) {
			var target = $("#sheet td").find("[data-x=" + x + "][data-y=" + y + "]");
			target.focus();
			target.select();
			e.preventDefault();
		}
	})
});
