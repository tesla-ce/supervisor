from ..exceptions import TeslaException

class TeslaDeployException(TeslaException):
    pass


class TeslaDeployNomadException(TeslaDeployException):
    pass


class TeslaDeployNomadTemplateException(TeslaDeployNomadException):
    pass


class TeslaDeployNomadException(TeslaDeployNomadException):
    pass
