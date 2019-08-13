from .parser import Parser


class Encoder(Parser):
    """
    Encode a signed int into a hex
    """

    def __init__(self, number):
        super(Encoder, self).__init__()
        self.signed_number = number

    def validate_parameters(self):
        if self.signed_number < -8192 or self.signed_number > 8191:
            raise ValueError("Encoder values out of range.")

    def parse(self):
        # add 8192 to signed_number
        intermediate_decimal = self.signed_number + 8192
        # apply mask
        low_seven = intermediate_decimal & 0x007F
        high_seven = intermediate_decimal & 0x3F80
        # shift with bitwise
        self.result = hex(low_seven + (high_seven << 1))

    def display(self):
        super(Encoder, self).display()
        print("encoded {} -> {}".format(self.signed_number, self.result))


class Decoder(Parser):
    """
    Decode two bytes into int with its most significant set
    """

    def __init__(self, high_byte, low_byte):
        super(Decoder, self).__init__()
        self.high_byte = int(high_byte, base=16)
        self.low_byte = int(low_byte, base=16)

    def validate_parameters(self):
        if self.high_byte < -8192 or self.low_byte > 8191:
            raise ValueError("Encoder values out of range.")
        return

    def parse(self):
        shifted = self.low_byte + (self.high_byte << 7)
        # subtract 8192 from shifted
        self.result = shifted - 8192

    def display(self):
        super(Decoder, self).display()
        print(
            "decoded {}-{} -> {}".format(
                hex(self.high_byte), hex(self.low_byte), self.result
            )
        )
