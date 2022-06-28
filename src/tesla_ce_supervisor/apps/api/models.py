from django.db import models
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


class SystemStatus(SingletonModel):
    """
        System status
    """
    version = models.CharField(max_length=255, null=True)
    last_config = models.DateField(null=True)
    status = models.CharField(max_length=255, null=True)


class Configuration(models.Model):
    """
        Encrypted storage of key/secret pairs
    """
    key = models.CharField(max_length=255, null=False, unique=True)
    value = EncryptedTextField(null=True)

