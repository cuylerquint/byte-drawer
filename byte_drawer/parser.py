from abc import abstractmethod


class Parser(object):
    """
    Abstraction used for code flow and DRYing
    """

    def __init__(self):
        self.result = None

    @abstractmethod
    def validate_parameters(self):
        raise NotImplementedError

    @abstractmethod
    def parse(self):
        raise NotImplementedError

    @abstractmethod
    def display(self):
        if self.result is None:
            raise RuntimeError(
                "{} parser failed to display result.".format(self.__class__.__name__)
            )
