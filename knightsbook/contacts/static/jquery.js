function formToJSON($form) {
	var json = {};

	$.map($form.serializeArray(), function(n, i) {
		json[n['name']] = n['value'];
	});

	return JSON.stringify(json);
}

$(document).ready(function() {

	setTimeout(function () {
		$(".alert").fadeIn(200);
	}, 50);

	$(".close-alert").click(function() {
		$(".alert").fadeOut(200);
	});

	$(".sidebar ul").find('a').click(function(e) {
		e.preventDefault();
		var page = $(this).attr('href');
		$(".content").load(page);
	});

	var $li = $('.sidebar li').click(function() {
		$li.removeClass('on');
		$(this).addClass('on');
	});

	$('#ajaxSubmit').click(function(e) {
		e.preventDefault();

		var pass = $('#password');
		if (pass.length) {
			pass.val(md5(pass.val()));
		}

		var form = $('#ajaxForm');
		var json = formToJSON(form);
		// console.log(json); // debug

		$.ajax({
			cache: false,
			url: form[0].action,
			type: 'POST',
			dataType: 'json',
			data: json,
			contentType: 'application/json;charset=UTF-8',
			complete: function(data, status) {
				// console.log(data); // debug

				var respJson = $.parseJSON(data.responseText);
				var redir = respJson['redirect'];
				if (redir) {
					window.location.replace(redir);
				}
			}
		});
	});
});
