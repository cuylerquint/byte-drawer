import argparse

from byte_drawer import TestRunner, Processor

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Draw Some Byte Streams!!")
    parser.add_argument(
        "--encode", help="Encode a integer into a Hexadecimal.", nargs=1
    )
    parser.add_argument(
        "--decode", help="Decode a high and low byte into a integer.", nargs=2
    )
    parser.add_argument(
        "--test",
        help="run test suite for given values in the assessment.",
        action="store_true",
    )
    parser.add_argument(
        "--draw-stream",
        help="draw from a stream of bytes via the command line.",
        nargs=1,
    )
    parser.add_argument(
        "--draw-file", help="draw from a stream of bytes in a text file.", nargs=1
    )
    args = parser.parse_args()

    try:
        if args.encode:
            Processor(number=int(args.encode[0]))
        elif args.decode:
            Processor(high_byte=args.decode[0], low_byte=args.decode[1])
        elif args.draw_stream:
            Processor(draw_input_stream=args.draw_stream[0])
        elif args.draw_file:
            Processor(draw_input_file=args.draw_file[0])
        elif args.test:
            TestRunner()
        else:
            print("run program with --help for insight on how to execute")
    except ValueError as err:
        print("ValueError: {}".format(err))
    except RuntimeError as err:
        print("RuntimeError: {}".format(err))
