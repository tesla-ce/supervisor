from django import forms
from .base import ConfigForm

TRUE_FALSE_CHOICES = [
    ('True', 'True'),
    ('False', 'False'),
]


class TeslaServiceMinioForm(ConfigForm):
    storage_url = forms.CharField(label='Storage URL', max_length=255)
    storage_private_bucket = forms.CharField(label='Storage private bucket name', max_length=255)
    storage_public_bucket = forms.CharField(label='Storage public bucket name', max_length=255)
    storage_region = forms.CharField(label='Storage region', max_length=255)
    storage_access_key = forms.CharField(label='Storage access key', max_length=255)
    storage_secret_key = forms.CharField(label='Storage secret key', max_length=255, widget=forms.PasswordInput(render_value=True))
    storage_ssl_verify = forms.ChoiceField(choices=TRUE_FALSE_CHOICES)

    _field_correspondence = [
        ('storage_url', 'STORAGE_URL'),
        ('storage_private_bucket', 'STORAGE_BUCKET_NAME'),
        ('storage_public_bucket', 'STORAGE_PUBLIC_BUCKET_NAME'),
        ('storage_region', 'STORAGE_REGION'),
        ('storage_access_key', 'STORAGE_ACCESS_KEY'),
        ('storage_secret_key', 'STORAGE_SECRET_KEY'),
        ('storage_ssl_verify', 'STORAGE_SSL_VERIFY'),
    ]
