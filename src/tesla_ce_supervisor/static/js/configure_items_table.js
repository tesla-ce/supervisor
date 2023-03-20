const base_url_connection = '/setup/api/';

const connection_step_desc = {
    'vault_init_kv': {name: 'Vault init KV', status: base_url_connection + 'task/config/vault_init_kv', config: base_url_connection + 'config/tesla/vault_init_kv'},
    'vault_init_transit': {name: 'Vault init Transit', status: base_url_connection + 'task/config/vault_init_transit', config: base_url_connection + 'config/tesla/vault_init_transit'},
    'vault_init_roles':  {name: 'Vault init Roles', status: base_url_connection + 'task/config/vault_init_roles', config: base_url_connection + 'config/tesla/vault_init_roles'},
    'vault_init_policies': {name: 'Vault init Policies', status: base_url_connection + 'task/config/vault_init_policies', config: base_url_connection + 'config/tesla/vault_init_policies'},
    'vault_unseal': {name: 'Vault Unseal', status: base_url_connection + 'task/config/vault_unseal', config: base_url_connection + 'config/tesla/vault_unseal'},
    'migrate_database': {disable_download: true, name: 'Migrate database', status: base_url_connection + 'task/config/migrate_database', config: base_url_connection + 'config/tesla/migrate_database'},
    'collect_static': {disable_download: true, name: 'Collect static', status: base_url_connection + 'task/config/collect_static', config: base_url_connection + 'config/tesla/collect_static'},
    'load_fixtures': {disable_download: true, name: 'Load fixtures', status: base_url_connection + 'task/config/load_fixtures', config: base_url_connection + 'config/tesla/load_fixtures'},
    'create_superuser': {disable_download: true, name: 'Create superuser', status: base_url_connection + 'task/config/create_superuser', config: base_url_connection + 'config/tesla/create_superuser'}
}

function set_step_status(step, status) {
    $('td.item-config-status[data-step="' + step + '"]').html(print_status(status));
}

function set_step_status_execute(step, status) {
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
            // set_jobs(service, data['jobs']);
            // set_instances(service, data['instances']);
            set_step_status(step, data['status']);
            // set_config_ready(service, data['ready']);
            // set_config_info(service, data['info']);
        }
    );
}

function config_action_step(step) {
    loading(true, step);
    $.post(
        connection_step_desc[step]['config'],
        function(data) {

            // set_jobs(service, data['jobs']);
            // set_instances(service, data['instances']);
            set_step_status_execute(step, data['result']);
            // set_config_ready(service, data['ready']);
            set_step_info(step, data['info']);
            refresh_config_log();
            loading(false, step);
        }
    );
}

function download_step(step) {
    $.get(
        connection_step_desc[step]['config'] + '?zip=1',
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

function refresh_config_all() {
    $('td.item-config-name').each(function() {
        refresh_config_step($(this).data('step'));
    });
}

function init_config_table() {
    $('td.item-config-name').each(function() {
        const step = $(this).data('step');
        $(this).html(connection_step_desc[step]['name']);

        if (connection_step_desc[step]['disable_download'] === true) {
            $("[data-step='"+step+"'][data-action='download']").remove();
        }
    });
    refresh_config_all();
}

$('.global-action').click(function() {
   const action = $(this).data()['action'];

   if (action === 'refresh_all') {
       refresh_config_all();
   }
});

$('.step-action').click(function() {
   const step = $(this).data()['step'];
   const action = $(this).data()['action'];

   if (action === 'refresh') {
       refresh_config_step(step);
   } else if (action === 'execute') {
       config_action_step(step);
   } else if (action === 'download') {
       download_step(step);
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
});
