$(document).ready(function() {

	$("input#enable-ssl").click(function() {
		if ($(this).is(':checked')) {
			$("label#label-scheme").html("https://");
		} else {
			$("label#label-scheme").html("http://");
		}
	});

	$("input#input-url").focus(function() {
		$(this).attr('placeholder', '');
	})

	$("input#input-url").blur(function() {
		$(this).attr('placeholder', 'enter a url address...');
	})
});