from .coders import Encoder, Decoder
from .drawer import Drawer


class Processor:
    """
    Facade class for handling and delegating the proper processing of the
    available parsers
    """

    def __init__(
        self,
        number=None,
        high_byte=None,
        low_byte=None,
        draw_input_stream=None,
        draw_input_file=None,
        display=True,
    ):
        self.display = display
        # set byte parsing class
        if number:
            self.parser = Encoder(number=number)
        elif high_byte and low_byte:
            self.parser = Decoder(high_byte=high_byte, low_byte=low_byte)
        elif draw_input_stream:
            self.parser = Drawer(arg_stream=draw_input_stream)
        elif draw_input_file:
            self.parser = Drawer(draw_file=draw_input_file)
        else:
            raise ValueError("ByteProcessor initialized improperly.")
        self.process()

    def process(self):
        """
        Process this self.parser
        """
        self.parser.validate_parameters()
        self.parser.parse()
        if self.display:
            self.parser.display()
