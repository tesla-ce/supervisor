const base_url_task = '/setup/api/task/log';

function print_status(status) {
    /*
        (0, 'CREATED'),
        (1, 'PENDING'),
        (2, 'RUNNING'),
        (3, 'SUCCESS'),
        (4, 'ERROR'),
        (5, 'TIMEOUT'),
      */
    switch(parseInt(status, 10)) {
        case 0:
            result = '<i class="bi bi-check-circle text-info"></i> Created';
            break;
        case 1:
            result = '<i class="bi bi-check-circle text-info"></i> Pending';
            break;
        case 2:
            result = '<i class="bi bi-check-circle text-info"></i> Running';
            break;
        case 3:
            result = '<i class="bi bi-check-circle text-success"></i> Success';
            break;
        case 4:
            result = '<i class="bi bi-x-circle text-danger"></i> Error';
            break;
        case 5:
            result = '<i class="bi bi-x-circle text-danger"></i> Timeout';
            break;
        default:
            result = '<i class="bi bi-x-circle text-danger"></i> (unknown)';
            break;
    }

    return result;
}

function button_trace(trace) {
    const aux_trace = JSON.stringify(trace);
    return "<button onclick='show_trace("+aux_trace+");' class='btn btn-sm btn-secondary' type='button'><i class='bi bi-filetype-json'></i></button>";
}
function show_trace(trace) {
    print_trace(trace);
    $("#trace_modal").modal('show');
}
function print_trace(trace) {
    console.log(trace);
    const aux_trace = JSON.parse(trace);
    console.log(aux_trace);
    const html = "<pre>"+JSON.stringify(aux_trace, undefined, 3)+"</pre>";
    $("#trace_modal .modal-body").html(html);

}
function set_log_status(data) {
    if (data.length > 0) {
        var append = false;
        for(let i=0; i < data.length; i++) {
            if (last_log_id === 1) {
                append = true;
            }

            if (data[i]['id'] > last_log_id) {
                last_log_id = data[i]['id'];
            }
            let html = '<tr><td>'+data[i]['created_at']+'</td><td>'+data[i]['code']+'</td><td>'+print_status(data[i]['status'])+'</td><td>'+button_trace(data[i]['error_json'])+'</td></tr>';

            if (append === true) {
                $("#tesla_configuration_log_table > tbody").append(html)
            } else {
                $("#tesla_configuration_log_table > tbody").prepend(html)
            }
        }
    }
}

function refresh_config_log() {
    $.get(
        base_url_task+'?task_id='+last_log_id,
        function(data) {
            set_log_status(data);
        }
    );
}

function init_config_log_table() {
    refresh_config_log();
}

$('.global-action-log').click(function() {
   const action = $(this).data()['action'];

   if (action === 'refresh_all') {
       refresh_config_log();
   }
});

var last_log_id = 1;

$(function() {
    init_config_log_table();
});
