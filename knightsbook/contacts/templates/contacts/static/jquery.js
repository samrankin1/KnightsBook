$(document).ready(function(){   
    setTimeout(function () {
        $(".alert").fadeIn(200);
     }, 50);
    $(".close-alert").click(function() {
        $(".alert").fadeOut(200);
    }); 
    $(".sidebar ul").find('a').click(function(e){
    e.preventDefault();
	var page = $(this).attr('href');
	$(".content").load(page);
	});
});