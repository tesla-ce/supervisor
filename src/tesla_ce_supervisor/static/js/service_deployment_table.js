function set_instances(service, num) {
    $('td.service-deploy-instances[data-service="' + service + '"]').html(num);
}
function set_jobs(service, num) {
    $('td.service-deploy-jobs[data-service="' + service + '"]').html(num);
}
function set_status(service, num) {
    $('td.service-deploy-status[data-service="' + service + '"]').html(num);
}
$('.service-action').click(function() {
   const service = $(this).data()['service'];
   const action = $(this).data()['action'];
   set_instances(service, action);
});
