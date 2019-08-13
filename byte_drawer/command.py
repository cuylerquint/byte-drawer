from .canvas import Color
from .coders import Decoder


class BaseCommand(object):
    """
    Abstraction for representing the actions that a Drawer can excute
    """

    def __init__(self, type, current_point_offset):
        """
        :param type: str
        :param current_point_offset: int: number of successful op byte codes processed for this command
        """
        self.type = type
        self.current_point_offset = current_point_offset
        self._process()

    def __repr__(self):
        return self.raw_command

    def _process(self):
        raise NotImplementedError

    @staticmethod
    def decode_bytes(high_byte, low_byte):
        """
        Wrapper function to utilize the Decoder Class

        :param high_byte: str
        :param low_byte: str
        """
        decoder = Decoder(high_byte=high_byte, low_byte=low_byte)
        decoder.parse()
        return decoder.result


class ClearCommand(BaseCommand):
    def __init__(self):
        super(ClearCommand, self).__init__(type="CLR", current_point_offset=1)

    def _process(self):
        self.raw_command = "CLR;"


class ColorCommand(BaseCommand):
    def __init__(self, r_bytes, g_bytes, b_bytes, a_bytes):
        """
        :param r_bytes: str
        :param g_bytes: str
        :param b_bytes: str
        :param a_bytes: str
        """

        self.r_bytes = r_bytes
        self.g_bytes = g_bytes
        self.b_bytes = b_bytes
        self.a_bytes = a_bytes
        super(ColorCommand, self).__init__(type="CO", current_point_offset=9)

    def _process(self):
        self.color = Color(
            r=BaseCommand.decode_bytes(
                high_byte=self.r_bytes[0], low_byte=self.r_bytes[1]
            ),
            g=BaseCommand.decode_bytes(
                high_byte=self.g_bytes[0], low_byte=self.g_bytes[1]
            ),
            b=BaseCommand.decode_bytes(
                high_byte=self.b_bytes[0], low_byte=self.b_bytes[1]
            ),
            a=BaseCommand.decode_bytes(
                high_byte=self.a_bytes[0], low_byte=self.a_bytes[1]
            ),
        )
        self.raw_command = "CO {};".format(self.color)


class MoveCommand(BaseCommand):
    def __init__(self, points):
        """
        :param points: [Point]: list of Points this command entails
        """
        self.points = points
        super(MoveCommand, self).__init__(type="MO", current_point_offset=None)

    def _process(self):
        self.raw_command = "MV {};".format(" ".join([str(x) for x in self.points]))


class PenCommand(BaseCommand):
    def __init__(self, pen_bytes):
        """
        :param pen_bytes: str
        """
        self.pen_bytes = pen_bytes
        super(PenCommand, self).__init__(type="PEN", current_point_offset=3)

    def _process(self):
        if BaseCommand.decode_bytes(self.pen_bytes[0], self.pen_bytes[1]) == 0:
            self.raw_command = "PEN UP;"
            self.is_down = False
        else:
            self.raw_command = "PEN DOWN;"
            self.is_down = True
