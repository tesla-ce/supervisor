class TeslaException(Exception):
    pass


class ProviderExistsException(TeslaException):
    def __init__(self, provider_id):
        self._provider_id = provider_id
        super().__init__(provider_id)

    @property
    def provider_id(self):
        return self._provider_id


class VLEExistsException(TeslaException):
    def __init__(self, vle_id):
        self._vle_id = vle_id
        super().__init__(vle_id)

    @property
    def vle_id(self):
        return self._vle_id
