from django import forms
from .base import ConfigForm


class TeslaBasicInfoForm(ConfigForm):
    institution_acronym = forms.CharField(label='Institution acronym', max_length=100)
    institution_name = forms.CharField(label='Institution name', max_length=250)
    base_domain = forms.CharField(label='Base domain', max_length=250)
    admin_email = forms.EmailField(label='Administrator email', max_length=250)
    admin_password = forms.CharField(label='Administrator password', max_length=250, widget=forms.PasswordInput(render_value=True))
    data_path = forms.CharField(label='Data path', max_length=250, required=False)

    _field_correspondence = [
        ('base_domain', 'TESLA_DOMAIN'),
        ('institution_acronym', 'TESLA_INSTITUTION_ACRONYM'),
        ('institution_name', 'TESLA_INSTITUTION_NAME'),
        ('admin_email', 'TESLA_ADMIN_MAIL'),
        ('admin_password', 'TESLA_ADMIN_PASSWORD'),
        ('data_path', 'DEPLOYMENT_DATA_PATH')
    ]
