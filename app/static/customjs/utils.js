<script type="text/javascript" charset="utf8" src="{{ url_for('static', filename='customjs/utils.js') }}" ></script>
(function($) {
	function time_convert(time){
		var hour=Number(time.trim().split(':')[0]);
		var minutes=''+time.trim().split(':')[1];
		var seconds=''+time.trim().split(':')[2];
		var AM_PM='';
		if(hour==0){hour+=12; AM_PM='AM'}
		else if(hour<12){AM_PM='AM'}
		else if (hour==12){AM_PM='PM'}
		else{hour-=12; AM_PM='PM'}
		return ""+hour + ":" + minutes + ":" + seconds + " " + AM_PM
	
}

function date_convert(date){
	return "" + date.trim().split('-')[1] + "-" + date.trim().split('-')[2] + "-" + date.trim().split('-')[0]
}



$('.nav-link').on('click',function(event){
          event.preventDefault();
          var x = $('.nav-link');
          x.removeClass('active');
          $(this).addClass('active');
          if ($('#todo').hasClass('active')){
          $('#to_do_tab').show();
			}
		  else{
          $('#to_do_tab').hide()
            }
      if ($('#events').hasClass('active')){
        $('#event_tab').show();
      }
      else{
        $('#event_tab').hide()
      }
	  });
	  
	
	  
$(document).ready( function () {
    $('#to_do_table').DataTable({
		"columns": [{ "searchable": false },
    { "searchable": false },
    { "searchable": false },
    { "searchable": false },
    null,
    { "searchable": false },
	{ "searchable": false }
    ]
	});
	
$('#to_do_table_alt').DataTable({
	"columns": [{ "searchable": false },
	{ "searchable": false },
	{ "searchable": false },
	{ "searchable": false },
	null,
	{ "searchable": false },
	{ "searchable": false }
	]
	});
});

	

$(document).ready( function () {
	$('#to_do_table_filter').prepend('Notes ');
	
	$('#to_do_table_alt_filter').prepend('Notes ');
	});
	

	
$('#hide_show_tasks').on("click", function(){
	event.preventDefault();
	if ($('#current_employee').css("display") != "none"){
	$('.completed_task').toggle();
	}
	else{
	$('.completed_task_alt').toggle();
	}
});



$('#task_creator').on("click", function(){
	event.preventDefault();
	var url="{{url_for('main_bp.task_maker')}}";
				$('#task_save').css("display", "inline");
				$('#make_event').css("display", "none");
				$('#form_modal').attr('src', url);
				$('.modal-title').text('Task Form');
				$('#formModal').modal({
						backdrop : 'static',
						keyboard : false});
});
})(jQuery);