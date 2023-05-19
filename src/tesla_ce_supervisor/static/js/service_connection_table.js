const base_url_connection = '/setup/api/';

const connection_service_desc = {
    'database': {name: 'Database', status: base_url_connection + 'connection/database', config: base_url_connection + 'config/database'},
    'rabbitmq': {name: 'RabbitMQ', status: base_url_connection + 'connection/rabbitmq', config: base_url_connection + 'config/rabbitmq'},
    'redis': {name: 'Redis', status: base_url_connection + 'connection/redis', config: base_url_connection + 'config/redis'},
    'vault': {name: 'HashiCorp Vault', status: base_url_connection + 'connection/vault', config: base_url_connection + 'config/vault'},
    'supervisor': {name: 'Supervisor', status: base_url_connection + 'connection/supervisor', config: base_url_connection + 'config/supervisor'},
    'minio': {name: 'MinIO', status: base_url_connection + 'connection/minio', config: base_url_connection + 'config/minio'}
}

function set_connection_status(service, status) {
    if (status) {
        $('td.service-connection-can-connect[data-service="' + service + '"]').html(
            '<i class="bi bi-check-circle text-success"></i>'
        );
        $('td.service-connection-can-connect[data-service="' + service + '"]').parent().find('.config-action').hide();
    } else {
        $('td.service-connection-can-connect[data-service="' + service + '"]').parent().find('.config-action').show();
        $('td.service-connection-can-connect[data-service="' + service + '"]').html(
            '<i class="bi bi-x-circle text-danger"></i>'
        );
    }
}

function set_connection_ready(service, status) {
    if (status) {
        $('td.service-connection-ready[data-service="' + service + '"]').html(
            '<i class="bi bi-check-circle text-success"></i>'
        );
        $('td.service-connection-ready[data-service="' + service + '"]').parent().find('.config-action').hide();
    } else {
        $('td.service-connection-ready[data-service="' + service + '"]').parent().find('.config-action').show();
        $('td.service-connection-ready[data-service="' + service + '"]').html(
            '<i class="bi bi-x-circle text-danger"></i>'
        );
    }
}

function set_connection_info(service, info) {
    if (info && Object.keys(info).length != 0) {
        $('td.service-connection-info[data-service="' + service + '"]').html(
            '<div class="alert alert-danger">'+info+'</div>'
        );
    } else {
        $('td.service-connection-info[data-service="' + service + '"]').html('-');
    }
}

function refresh_connection_service(service) {
    $.get(
        connection_service_desc[service]['status'],
        function(data) {
            // set_jobs(service, data['jobs']);
            // set_instances(service, data['instances']);
            set_connection_status(service, data['valid']);
            set_connection_ready(service, data['ready']);
            set_connection_info(service, data['info']);
        }
    );
}

function refresh_connection_all() {
    $('td.service-connection-name').each(function() {
        refresh_connection_service($(this).data('service'));
    });
}

function init_connection_table() {
    $('td.service-connection-name').each(function() {
        $(this).html(connection_service_desc[$(this).data('service')]['name']);
    });
    refresh_connection_all();
}

$('.global-action').click(function() {
   const action = $(this).data()['action'];

   if (action === 'refresh_all') {
       refresh_connection_all();
   }
});

$('.connection-action').click(function() {
   const service = $(this).data()['service'];
   const action = $(this).data()['action'];

   if (action === 'refresh') {
       refresh_connection_service(service);
   } else if (action === 'config') {
       config_action_service(service);
   }
});

function config_action_service(service) {
    $.post(
        connection_service_desc[service]['config'],
        function(data) {
            set_connection_ready(service, data['ready']);
            set_connection_info(service, data['info']);

            // set_jobs(service, data['jobs']);
            // set_instances(service, data['instances']);
            // set_connection_status(service, data['valid']);
            // set_connection_info(service, data['info']);
        }
    );
}

$(function() {
    init_connection_table();
});
