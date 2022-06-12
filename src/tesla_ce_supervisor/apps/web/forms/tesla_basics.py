from django import forms
from .base import ConfigForm


class TeslaBasicInfoForm(ConfigForm):
    institution_acronym = forms.CharField(label='Institution acronym', max_length=100)
    institution_name = forms.CharField(label='Institution name', max_length=250)
    base_domain = forms.CharField(label='Base domain', max_length=250)
    admin_email = forms.EmailField(label='Administrator email', max_length=250)

    _field_correspondence = [
        ('base_domain', 'TESLA_DOMAIN'),
        ('institution_acronym', 'TESLA_INSTITUTION_ACRONYM'),
        ('institution_name', 'TESLA_INSTITUTION_NAME'),
        ('admin_email', 'TESLA_ADMIN_MAIL'),
    ]
