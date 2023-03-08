import json
from tesla_ce_supervisor.apps.api.models import TaskLog


class TaskClient:
    def __init__(self):
        pass

    def get_last_by_code(self, code):
        try:
            return TaskLog.objects.filter(code=code).order_by('-created_at').first()
        except TaskLog.DoesNotExist:
            pass

        return None

    def get_lasts_tasks(self, task_id):
        try:
            if task_id is None:
                task_id = 1
            return TaskLog.objects.filter(id__gt=task_id).order_by('-created_at')[:20]
        except TaskLog.DoesNotExist:
            pass

        return None

    def create(self, code):
        task_log = TaskLog()
        task_log.code = code

        task_log.save()
        return task_log

    def create_from_core(self, command, status):
        task_log = TaskLog()

        task_log.code = command
        setup_commands = [
            'vault_unseal'
            'vault_init_kv',
            'vault_init_policies',
            'vault_init_transit',
            'vault_init_roles',
            'migrate_database',
            'collect_static',
            'load_fixtures',
            'create_superuser'
        ]

        # by default type is CONFIG
        task_log.type = 2

        if command in setup_commands:
            task_log.type = 0

        # mark task as error
        task_log.status = 4
        if 'status' in status and status['status'] is True:
            # mark task SUCCESS
            task_log.status = 3

        task_log.error_json = json.dumps(status)
        task_log.save()

        return task_log
