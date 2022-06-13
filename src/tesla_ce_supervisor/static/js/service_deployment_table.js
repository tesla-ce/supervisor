const base_url = '/setup/api/';

const service_desc = {
    'lb': {name: 'Load Balancer', deploy: base_url + 'deploy/lb', status: base_url + 'check/lb'},
    'database': {name: 'Database', path: base_url + 'deploy/database', status: base_url + 'check/database'},
    'rabbitmq': {name: 'RabbitMQ', path: base_url + 'deploy/rabbitmq', status: base_url + 'check/rabbitmq'},
    'minio': {name: 'MinIO', path: base_url + 'deploy/minio', status: base_url + 'check/minio'},
    'redis': {name: 'Redis', path: base_url + 'deploy/redis', status: base_url + 'check/redis'},
    'vault': {name: 'HashiCorp Vault', path: base_url + 'deploy/vault', status: base_url + 'check/vault'},
}

function set_instances(service, num) {
    $('td.service-deploy-instances[data-service="' + service + '"]').html(num);
}
function set_jobs(service, num) {
    $('td.service-deploy-jobs[data-service="' + service + '"]').html(num);
}
function set_status(service, status) {
    if (status) {
        $('td.service-deploy-status[data-service="' + service + '"]').html(
            '<i class="bi bi-check-circle text-success"></i>'
        );
    } else {
        $('td.service-deploy-status[data-service="' + service + '"]').html(
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

function refresh_all() {
    $('td.service-deploy-name').each(function() {
        refresh_service($(this).data('service'));
    });
}

function download_service(service) {
    $.get(
        service_desc[service]['deploy'] + '?zip=1',
        function(data) {
            // Set ZIP data
            $('#service_modal_dialog_file').attr('href', data['zip']);
            // Create the list of commands
            let commands = '';
            for(let cmd in data['commands']) {
                commands += '<p class="text-muted"><strong>' + data['commands'][cmd]['description'] + '</strong></p>';
                commands += '<pre><code className="language-bash">' + data['commands'][cmd]['command'] + '</code></pre><br/>';
            }
            $('#service_modal_commands').html(commands);
            // Show information in modal dialog
            $("#service_modal_dialog").modal('show');
        }
    );
}

function remove_service(service) {
    $.ajax({
        url: service_desc[service]['deploy'],
        type: 'DELETE',
        success: function(result) {
            refresh_service(service);
        }
    });
}

function remove_all() {
    $('td.service-deploy-name').each(function() {
        remove_service($(this).data('service'));
    });
}

function deploy_service(service) {
    $.post(
        service_desc[service]['deploy'],
        function() {
            refresh_service(service);
        }
    );
}

function deploy_all() {
    $('td.service-deploy-name').each(function() {
        deploy_service($(this).data('service'));
    });
}

function init_table() {
    $('td.service-deploy-name').each(function() {
        $(this).html(service_desc[$(this).data('service')]['name']);
    });
    refresh_all();
}

$('.global-action').click(function() {
   const action = $(this).data()['action'];

   if (action === 'refresh_all') {
       refresh_all();
   } else if (action === 'remove_all') {
       remove_all();
   } else if (action === 'deploy_all') {
       deploy_all();
   }
});

$('.service-action').click(function() {
   const service = $(this).data()['service'];
   const action = $(this).data()['action'];

   if (action === 'refresh') {
       refresh_all();
   } else if (action === 'download') {
       download_service(service);
   } else if (action === 'remove') {
       remove_service(service);
   } else if (action === 'deploy') {
       deploy_service(service);
   }
});

$(function() {
   init_table();
});
