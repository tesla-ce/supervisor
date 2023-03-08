from django import forms

class ConfigForm(forms.Form):
    """
        Base form for configuration views
    """
    _field_correspondence = []

    def update_config(self, config):
        for field in self._field_correspondence:
            #if field[0] not in self.cleaned_data:
            #    # TODO: REMOVE THIS BRANCH, ONLY TAKE INFO FROM CLEANED_DATA
            #    #config.set(field[1], self.data.get(field[0]))
            #else:
            config.set(field[1], self.cleaned_data.get(field[0]))

    def load_config(self, config):
        for field in self._field_correspondence:
            if field[0] in self.fields:
                self.fields[field[0]].initial = self.parse_config_value(field[0], config.get(field[1]))

    def parse_config_value(self, field, value):
        return value
