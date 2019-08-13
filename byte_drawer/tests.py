import unittest

from .canvas import Point, Canvas
from .coders import Encoder, Decoder
from .processor import Processor


class TestCoders(unittest.TestCase):
    def test_challege_one_given_encode_values(self):
        cases = [
            (6111, 0x6F5F),
            (340, 0x4254),
            (-2628, 0x2B3C),
            (-255, 0x3E01),
            (7550, 0x7A7E),
        ]
        for case in cases:
            parser = Encoder(number=case[0])
            parser.parse()
            byte_parser_encoded_value = parser.result
            expected_hex = hex(case[1])
            self.assertEqual(byte_parser_encoded_value, expected_hex)

    def test_challege_one_given_decode_values(self):
        cases = [
            ("0A", "0A", -6902),
            ("00", "29", -8151),
            ("3F", "0F", -113),
            ("44", "00", 512),
            ("5E", "7F", 3967),
        ]
        for case in cases:
            parser = Decoder(high_byte=case[0], low_byte=case[1])
            parser.parse()
            byte_parser_decoded_value = parser.result
            expected_int = case[2]
            self.assertEqual(byte_parser_decoded_value, expected_int)


class TestCanvas(unittest.TestCase):
    def test_contains_point(self):
        test_canvas = Canvas(-10, 10, -10, 10)

        cases = [
            (Point(4, 5), True),
            (Point(11, 11), False),
            (Point(-11, 0), False),
            (Point(0, -11), False),
            (Point(-11, -11), False),
        ]

        for case in cases:
            result = test_canvas.contains_point(case[0])
            self.assertEqual(result, case[1])


class TestDrawer(unittest.TestCase):
    def test_given_examples(self):
        cases = [
            # green line
            (
                "F0A04000417F4000417FC040004000804001C05F205F20804000",
                [
                    "CLR;",
                    "CO 0 255 0 255;",
                    "MV (0, 0);",
                    "PEN DOWN;",
                    "MV (4000, 4000);",
                    "PEN UP;",
                ],
            ),
            # blue square
            (
                "F0A040004000417F417FC04000400090400047684F5057384000804001C05F204000400001400140400040007E405B2C4000804000",
                [
                    "CLR;",
                    "CO 0 0 255 255;",
                    "MV (0, 0);",
                    "PEN DOWN;",
                    "MV (4000, 0) (4000, -8000) (-4000, -8000) (-4000, 0) (-500, 0);",
                    "PEN UP;",
                ],
            ),
            # red clipping
            (
                "F0A0417F40004000417FC067086708804001C0670840004000187818784000804000",
                [
                    "CLR;",
                    "CO 255 0 0 255;",
                    "MV (5000, 5000);",
                    "PEN DOWN;",
                    "MV (8191, 5000);",
                    "PEN UP;",
                    "MV (8191, 0);",
                    "PEN DOWN;",
                    "MV (5000, 0);",
                    "PEN UP;",
                ],
            ),
            # orange diagonal clipping #NOTE modified for rounding edge cases
            (
                "F0A0417F41004000417FC067086708804001C067082C3C18782C3C804000",
                [
                    "CLR;",
                    "CO 255 128 0 255;",
                    "MV (5000, 5000);",
                    "PEN DOWN;",
                    "MV (8191, 3404);",
                    "PEN UP;",
                    "MV (8191, 1595);",
                    "PEN DOWN;",
                    "MV (5000, 0);",
                    "PEN UP;",
                ],
            ),
        ]

        for case in cases:
            processor = Processor(draw_input_stream=case[0], display=False)
            self.assertEqual(processor.parser.result, case[1])


class TestRunner(object):
    def __init__(self):
        loader = unittest.TestLoader()
        tests = [
            loader.loadTestsFromTestCase(test)
            for test in [TestCoders, TestCanvas, TestDrawer]
        ]
        suite = unittest.TestSuite(tests)
        runner = unittest.TextTestRunner(verbosity=2)
        runner.run(suite)
