from .abstract import FrontendAbstract


class Config(FrontendAbstract):
    """
    A class representing a generic configuration object.
    """

    authentication = True
    brand = str()
    logo = str()
    css = str()
    description = str()