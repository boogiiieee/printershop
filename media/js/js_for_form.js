$(document).ready(function(){
	function add_default_input(id, name) {
		if($(id).val() == ''){ $(id).val(name); };
		$(id).click(function(){ if ($(this).val() == name) { $(this).val(''); }; });
		$(id).blur(function(){ if ($(this).val() == '') { $(this).val(name); }; });
	};
});
