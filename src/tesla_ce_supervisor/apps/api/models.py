from django.db import models
from django.utils import timezone
from fernet_fields import EncryptedCharField, EncryptedTextField


# Create your models here.
class SingletonModel(models.Model):
    """
        Model with a single instance
    """
    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        self.pk = 1
        super(SingletonModel, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        pass

    @classmethod
    def load(cls):
        obj, created = cls.objects.get_or_create(pk=1)
        return obj


SYSTEM_STATUS = (
    (0, 'UNKNOWN'),
    (1, 'NOT_INITIALIZED'),
    (2, 'INITIALIZING'),
    (3, 'INITIALIZED'),
    (4, 'RUNNING'),
    (5, 'UPDATING'),
    (6, 'HEALTHY'),
    (7, 'UNHEALTHY'),
    (8, 'TIMEOUT'),
    (9, 'ERROR'),
)

SERVICE_STATUS = (
    (0, 'UNKNOWN'),
    (1, 'NOT_INITIALIZED'),
    (2, 'INITIALIZING'),
    (3, 'INITIALIZED'),
    (4, 'RUNNING'),
    (5, 'HEALTHY'),
    (6, 'UNHEALTHY'),
    (7, 'TIMEOUT'),
    (8, 'ERROR'),
)

TASK_STATUS = (
    (0, 'CREATED'),
    (1, 'PENDING'),
    (2, 'RUNNING'),
    (3, 'SUCCESS'),
    (4, 'ERROR'),
    (5, 'TIMEOUT'),
)

TASK_TYPE = (
    (0, 'SETUP'),
    (1, 'DEPLOY'),
    (2, 'CONFIG'),
)


class SystemStatus(SingletonModel):
    """
        System status
    """
    version = models.CharField(max_length=255, null=True)
    last_config = models.DateField(null=True)
    status = models.SmallIntegerField(choices=SYSTEM_STATUS, null=False, default=0)

    def to_json(self):
        return {"version": self.version, "last_config": self.last_config.isoformat(), "status": self.status}

class Configuration(models.Model):
    """
        Encrypted storage of key/secret pairs
    """
    key = models.CharField(max_length=255, null=False, unique=True)
    value = EncryptedTextField(null=True)


class ServiceStatus(models.Model):
    """
        Service status
    """
    name = models.CharField(max_length=255, null=True)
    version = models.CharField(max_length=255, null=True)
    last_config = models.DateField(null=True)
    last_check = models.DateField(null=True)
    status = models.SmallIntegerField(choices=SERVICE_STATUS, null=False, default=0)


class ServiceStatusLog(models.Model):
    """
        Service status
    """
    service = models.ForeignKey(ServiceStatus, null=False, on_delete=models.CASCADE)

    message = models.TextField(null=True, blank=True, default=None)
    old_status = models.SmallIntegerField(choices=SERVICE_STATUS, null=False, default=0)
    new_status = models.SmallIntegerField(choices=SERVICE_STATUS, null=False, default=0)

    created_at = models.DateTimeField(null=False, blank=False, default=timezone.now)


class TaskLog(models.Model):
    """
       Task log
    """
    code = models.TextField(null=True, blank=True, default=None)
    status = models.SmallIntegerField(choices=TASK_STATUS, null=False, default=0)
    error_json = models.TextField(null=True, blank=True, default=None)
    type = models.SmallIntegerField(choices=TASK_TYPE, null=False, default=0)

    created_at = models.DateTimeField(null=False, blank=False, default=timezone.now)
    updated_at = models.DateTimeField(null=False, blank=False, default=timezone.now)

    parent_task = models.ForeignKey('self', null=True, on_delete=models.SET_NULL, related_name='parent')
    previous_task = models.ForeignKey('self', null=True, on_delete=models.SET_NULL, related_name='previous')

    def to_json(self):
        parent_task_id = None
        previous_task_id = None

        if self.parent_task != None:
            parent_task_id = self.parent_task.id

        if self.previous_task != None:
            previous_task_id = self.previous_task.id

        return {
            'code': self.code,
            'status': self.status,
            'error_json': self.error_json,
            'type': self.type,
            #'created_at': self.created_at.isoformat(),
            #'updated_at': self.updated_at.isoformat(),
            'parent_task_id': parent_task_id,
            'previous_task_id': previous_task_id,
        }