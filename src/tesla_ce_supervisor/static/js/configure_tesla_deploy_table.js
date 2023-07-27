const base_url = '/setup/api/';

const connection_step_desc = {
    'api': {name: 'API', deploy: base_url + 'deploy/tesla/api', status: base_url + 'check/tesla/api'},
    'beat': {name: 'Beat', deploy: base_url + 'deploy/tesla/beat', status: base_url + 'check/tesla/beat'},
    'worker-all': {name: 'Worker all', deploy: base_url + 'deploy/tesla/worker-all', status: base_url + 'check/tesla/worker-all'},
    'worker': {name: 'Worker', deploy: base_url + 'deploy/tesla/worker', status: base_url + 'check/tesla/worker'},
    'worker-enrolment': {name: 'Worker enrolment', deploy: base_url + 'deploy/tesla/worker-enrolment', status: base_url + 'check/tesla/worker-enrolment'},
    'worker-enrolment-storage': {name: 'Worker enrolment storage', deploy: base_url + 'deploy/tesla/worker-enrolment-storage', status: base_url + 'check/tesla/worker-enrolment-storage'},
    'worker-enrolment-validation': {name: 'Worker enrolment validation', deploy: base_url + 'deploy/tesla/worker-enrolment-validation', status: base_url + 'check/tesla/worker-enrolment-validation'},
    'worker-verification': {name: 'Worker verification', deploy: base_url + 'deploy/tesla/worker-verification', status: base_url + 'check/tesla/worker-verification'},
    'worker-alerts': {name: 'Worker alerts', deploy: base_url + 'deploy/tesla/worker-alerts', status: base_url + 'check/tesla/worker-alerts'},
    'worker-reporting': {name: 'Worker reporting', deploy: base_url + 'deploy/tesla/worker-reporting', status: base_url + 'check/tesla/worker-reporting'},
    'lapi': {name: 'LAPI - Learner API', deploy: base_url + 'deploy/tesla/lapi', status: base_url + 'check/tesla/lapi'},
    'dashboard': {name: 'Dashboard', deploy: base_url + 'deploy/tesla/dashboard', status: base_url + 'check/tesla/dashboard'},
    'moodle': {name: 'Moodle', deploy: base_url + 'deploy/tesla/moodle', status: base_url + 'check/tesla/moodle'},
    'face-recognition': {name: 'TFR - TeSLA Face Recognition', deploy: base_url + 'deploy/tesla/fr', status: base_url + 'check/tesla/fr'},
    'keystroke': {name: 'TKS - TeSLA Keystroke', deploy: base_url + 'deploy/tesla/ks', status: base_url + 'check/tesla/ks'},
    'tpt': {name: 'TPT - TeSLA Plagiarism Tool', deploy: base_url + 'deploy/tesla/tpt', status: base_url + 'check/tesla/tpt'}
}

function set_instances(service, instances) {
    const cell = $('td.item-deploy-instances[data-step="' + service + '"]');
    if (instances) {
        if (cell.data()['catalog'] === 'consul') {
            let services = '<ul class="list-unstyled">';
            for (let srv in instances['services']) {
                if (instances['services'][srv]['healthy_instances'] === instances['services'][srv]['total_instances'] && instances['services'][srv]['total_instances'] > 0) {
                    services += '<li class="text-success">' + instances['services'][srv]['name'] + ' (' + instances['services'][srv]['healthy_instances'] + '/' + instances['services'][srv]['total_instances'] + ')</li>';
                } else {
                    services += '<li class="text-danger">' + instances['services'][srv]['name'] + ' (' + instances['services'][srv]['healthy_instances'] + '/' + instances['services'][srv]['total_instances'] + ')</li>';
                }
            }
            services += '</ul>';
            cell.html(services);
        } else {
            cell.html(
                instances['healthy'] + '/' + instances['total']
            );
        }
    } else {
        cell.html(
            '0/0'
        );
    }
}
function set_jobs(service, jobs) {
    if (jobs) {
        $('td.item-deploy-jobs[data-step="' + service + '"]').html(
            '' + jobs['running'] + '/' + jobs['expected'] + ' (' + jobs['healthy'] + ' healthy)'
        );
    } else {
        $('td.item-deploy-jobs[data-step="' + service + '"]').html(
            '0/0 (0 healthy)'
        );
    }
}
function set_status(service, status) {
    if (status) {
        $('td.item-deploy-status[data-service="' + service + '"]').html(
            '<i class="bi bi-check-circle text-success"></i>'
        );
    } else {
        $('td.item-deploy-status[data-service="' + service + '"]').html(
            '<i class="bi bi-x-circle text-danger"></i>'
        );
    }
}

function refresh_service(service) {
    $.get(
        service_desc[service]['status'],
        function(data) {
            set_jobs(service, data['jobs']);
            set_instances(service, data['instances']);
            set_status(service, data['valid']);
        }
    );
}
function set_step_status_execute(step, status) {
    console.log(status);
    if (status == true) {
        $('td.item-config-status[data-step="' + step + '"]').html(
            '<i class="bi bi-check-circle text-success"></i>'
        );
        $('td.item-config-status[data-step="' + step + '"]').parent().find('.config-action').hide();
    } else {
        $('td.item-config-status[data-step="' + step + '"]').parent().find('.config-action').show();
        $('td.item-config-status[data-step="' + step + '"]').html(
            '<i class="bi bi-x-circle text-danger"></i>'
        );
    }
}


function set_step_info(step, info) {
    $('td.item-config-info[data-step="' + step + '"]').html(info);
}

function refresh_config_step(step) {
    $.get(
        connection_step_desc[step]['status'],
        function(data) {
            set_jobs(step, data['jobs']);
            set_instances(step, data['instances']);
            set_status(step, data['valid']);

        }
    );
}

function deploy_action_step(step) {
    loading(true, step);
    $.post(
        connection_step_desc[step]['deploy'],
        function(data) {

            // set_jobs(service, data['jobs']);
            // set_instances(service, data['instances']);
            set_step_status_execute(step, data['result']);
            // set_config_ready(service, data['ready']);
            set_step_info(step, data['info']);

            loading(false, step);
            refresh_config_step(step);
        }
    );
}

function refresh_config_all() {
    $('td.item-config-name').each(function() {
        refresh_config_step($(this).data('step'));
    });
}

function init_config_table() {
    $('td.item-config-name').each(function() {
        $(this).html(connection_step_desc[$(this).data('step')]['name']);
    });
    refresh_config_all();
}

function download_action_step(service) {
    $.get(
        connection_step_desc[service]['deploy'] + '?zip=1',
        function(data) {
            // Set ZIP data
            $('#service_modal_dialog_file').attr('href', data['zip']);
            // Create the list of commands
            let commands = '';
            for(let cmd in data['commands']) {
                commands += '<p class="text-muted"><strong>' + data['commands'][cmd]['description'] + '</strong></p>';
                commands += '<pre><code class="language-bash" data-prismjs-copy="Copy">' + data['commands'][cmd]['command'] + '</code></pre><br/>';
            }
            $('#service_modal_commands').html(commands);
            // Highlight code
            Prism.highlightAll();
            // Show information in modal dialog
            $("#service_modal_dialog").modal('show');
        }
    );
}

$('.global-action').click(function() {
   const action = $(this).data()['action'];

   if (action === 'refresh_all') {
       refresh_config_all();
   }
});

function remove_step(step) {
    $.ajax({
        url: connection_step_desc[step]['deploy'],
        type: 'DELETE',
        success: function(result) {
            refresh_config_step(step);
        }
    });
}

$('.step-action').click(function() {
   const step = $(this).data()['step'];
   const action = $(this).data()['action'];

   if (action === 'refresh') {
       refresh_config_step(step);
   } else if (action === 'execute') {
       deploy_action_step(step);
   } else if (action === 'download') {
       download_action_step(step);
   } else if (action === 'remove') {
        remove_step(step);
    }
});

function config_action_service(service) {
    $.get(
        connection_step_desc[service]['config'],
        function(data) {
            set_connection_ready(service, data['ready']);
            set_connection_info(service, data['info']);
        }
    );
}

function loading(show, step) {
    let html = '';
    if (show === true) {
        html = '<div class="spinner-border text-info" role="status"><span class="sr-only"></span></div>';
    }
    set_step_info(step, html);
}

$(function() {
    init_config_table();
    $("#specialized_workers").change(function() {
        const val = ($("#specialized_workers").prop('checked') === true ? 1 : 0);
        window.location.href = window.location.href.split('?')[0]+'?deployment_specialized_workers='+val;

    });
});


