from .canvas import Canvas, Point, Line
from .command import BaseCommand, PenCommand, MoveCommand, ClearCommand, ColorCommand
from .parser import Parser


class Drawer(Parser):
    """
    Abstraction for processing a btye stream and generating draw lines, commands and pen up/down points
    on a canvas.
    """

    default_canvas = Canvas(-8192, 8191, -8192, 8191)

    def __init__(self, arg_stream=None, draw_file=None, canvas=None):
        """
        :param arg_stream: str: raw un-decoded op codes
        :param draw_file: str: file name to process a byte stream from
        :param canvas: Canvas: support configurable Canvas
        """
        super(Drawer, self).__init__()
        self.commands = list()
        self.draw_lines = list()
        self.pen_down_points = list()
        self.pen_up_points = list()
        # naive assumptions
        self.current_point = None
        self.was_drawing = False
        self.drawer_out_of_bounds = False
        self.pen_down = False

        if canvas:
            self.canvas = canvas
        else:
            self.canvas = Drawer.default_canvas
            for border in self.canvas.borders:
                self.draw_lines.append(border)

        self.color = self.canvas.default_color

        if arg_stream:
            self.input_steam = arg_stream
        else:
            with open(draw_file, "r") as file:
                # here would be another place to run validation on the input_file e.g. /n's
                self.input_steam = file.readline()

    def validate_parameters(self):
        if self.input_steam is None:
            raise RuntimeError("invalid input stream for Drawer")

    def parse(self):
        self._decode_input_stream()
        self.result = [command.raw_command for command in self.commands]

    def display(self):
        for command in self.result:
            print(command)

    def _out_of_bounds(self, point):
        return not self.canvas.contains_point(point)

    def _decode_input_stream(self):
        """
        Start of op code processing.  determind the command code were dealing with then delegate
        """
        self.raw_op_codes = list(self._get_op_codes())
        self.current_op_code_pointer = 0
        while self.current_op_code_pointer < len(self.raw_op_codes):
            next_op_code = self.raw_op_codes[self.current_op_code_pointer]

            if next_op_code == "F0":
                self._handle_clear_command()
            elif next_op_code == "A0":
                self._handle_color_command()
            elif next_op_code == "80":
                self._handle_pen_command()
            elif next_op_code == "C0":
                self._handle_move_command()
            else:
                # unrecognized command, ignore
                self.current_op_code_pointer = self.current_op_code_pointer + 1

    def _get_op_codes(self):
        """
        Yield op codes from the given input stream
        """
        while self.input_steam:
            yield self.input_steam[:2]
            self.input_steam = self.input_steam[2:]

    def _handle_clear_command(self):
        """
        Handle a clear command

        - Create a clear command instance and append its raw command value
        - Update this drawers globals for subsequent commands

        """
        clear_command = ClearCommand()
        self.commands.append(clear_command)
        self.current_op_code_pointer = (
            self.current_op_code_pointer + clear_command.current_point_offset
        )
        self.current_color = [0, 0, 0, 225]
        self.current_point = self.canvas.center_point
        self.pen_down = False

    def _handle_color_command(self):
        """
        Handle a pen command.

        - Grab the next eight op codes
        - Decode into a rgba color and update this drawers color
        - Update this drawers globals for subsequent commands

        """
        r_bytes = [
            self.raw_op_codes[self.current_op_code_pointer + 1],
            self.raw_op_codes[self.current_op_code_pointer + 2],
        ]
        g_bytes = [
            self.raw_op_codes[self.current_op_code_pointer + 3],
            self.raw_op_codes[self.current_op_code_pointer + 4],
        ]
        b_bytes = [
            self.raw_op_codes[self.current_op_code_pointer + 5],
            self.raw_op_codes[self.current_op_code_pointer + 6],
        ]
        a_bytes = [
            self.raw_op_codes[self.current_op_code_pointer + 7],
            self.raw_op_codes[self.current_op_code_pointer + 8],
        ]

        color_command = ColorCommand(r_bytes, g_bytes, b_bytes, a_bytes)
        self.color = color_command.color
        self.commands.append(color_command)
        self.current_op_code_pointer = (
            self.current_op_code_pointer + color_command.current_point_offset
        )

    def _handle_pen_command(self):
        """
        Handle a pen command.

        - Grab the next two op codes
        - Decode into either pen up or pen down command
        - Update this drawers globals for subsequent commands

        """

        pen_bytes = [
            self.raw_op_codes[self.current_op_code_pointer + 1],
            self.raw_op_codes[self.current_op_code_pointer + 2],
        ]
        pen_command = PenCommand(pen_bytes)
        if self.drawer_out_of_bounds and pen_command.is_down:
            raise ValueError(
                "Invalid Drawer Command: Cannot PEN DOWN while drawer is off the canvas."
            )
        if not self.current_point and pen_command.is_down:
            raise ValueError(
                "Invalid Drawer Command: Cannot PEN DOWN before setting an initial point."
            )
        self.commands.append(pen_command)
        self.current_op_code_pointer = (
            self.current_op_code_pointer + pen_command.current_point_offset
        )
        self.pen_down = pen_command.is_down
        if self.pen_down:
            self.pen_down_points.append(self.current_point)
        else:
            self.pen_up_points.append(self.current_point)

    def _handle_move_command(self):
        """
        Handle a pen command.

        - Build a list of move points based off the next 4 op code bytes for each loop
        - Handle cases for termination
        - run subroutine to update self.commands based off new points list

        """
        new_points = list()
        if self.current_op_code_pointer + 1 < len(self.raw_op_codes):

            # get number of parameters
            #
            move_pointer = self.current_op_code_pointer
            orginal_current_point = self.current_point
            # determine if we keep processing coordinate bytes based off command ops of endof byte stream
            next_move_op = self.raw_op_codes[move_pointer + 1]
            while next_move_op not in ["F0", "A0", "80"] and move_pointer + 1 < len(
                self.raw_op_codes
            ):
                # decode the coordinate and append to moves in this run
                x_axis_bytes = [
                    self.raw_op_codes[move_pointer + 1],
                    self.raw_op_codes[move_pointer + 2],
                ]
                y_axis_bytes = [
                    self.raw_op_codes[move_pointer + 3],
                    self.raw_op_codes[move_pointer + 4],
                ]

                new_point = Point(
                    BaseCommand.decode_bytes(x_axis_bytes[0], x_axis_bytes[1]),
                    BaseCommand.decode_bytes(y_axis_bytes[0], y_axis_bytes[1]),
                )
                new_point.x = int(new_point.x + self.current_point.x)
                new_point.y = int(new_point.y + self.current_point.y)

                new_points.append(new_point)
                self.current_point = new_point

                # determine if we have a terminating case for this move command or update pointers
                # Note: this is major assumption not defined, after any move to center is a single parameter move
                # command.  This is the only way i could get around ignoring bad parameters e.g. Blue Square
                if move_pointer + 5 == len(self.raw_op_codes) or (
                    new_point.x == 0 and new_point.y == 0
                ):
                    break
                else:
                    move_pointer = move_pointer + 4
                    next_move_op = self.raw_op_codes[move_pointer + 1]

            # set pointers for build subroutine
            self.current_point = orginal_current_point
            self.current_op_code_pointer = (
                self.current_op_code_pointer + (4 * len(new_points)) + 1
            )
            self._build_move_command(new_points)

    def _build_move_command(self, new_points):
        """
        Determine if we have to handle out of bound cases and make sub commands where needed.
        We assume if the pen is down that a move command has set this.current_point

        :param new_points: [Point]: list of move points for this move command. May contain points out of bounds
        """

        valid_moves_points = list()
        for next_point in new_points:
            if self.pen_down:
                # we can assert that the pen will not be down and out of bounds at the same time
                if not self._out_of_bounds(self.current_point) and self._out_of_bounds(
                    next_point
                ):
                    # in bounds going out
                    # execute mv points to edge point
                    # execute pen up
                    # mark out of bounds
                    edge_point = self._build_edge_point(
                        inner_point=self.current_point, outer_point=next_point
                    )
                    valid_moves_points.append(edge_point)

                    move_command = MoveCommand(points=valid_moves_points)
                    self.commands.append(move_command)

                    pen_up_command = PenCommand(["40", "00"])  # zero for pen down
                    self.pen_down = False
                    self.commands.append(pen_up_command)

                    new_line = Line(self.current_point, edge_point, self.color)
                    self.draw_lines.append(new_line)
                    self.pen_up_points.append(edge_point)
                    self.drawer_out_of_bounds = True
                    self.was_drawing = True
                    self.current_point = next_point
                    # reset valid_move_points
                    valid_moves_points = list()

                elif not self._out_of_bounds(
                    self.current_point
                ) and not self._out_of_bounds(next_point):
                    # normal case make a new line
                    valid_moves_points.append(next_point)
                    new_line = Line(self.current_point, next_point, self.color)
                    self.draw_lines.append(new_line)
                    self.current_point = next_point

            else:
                if self.drawer_out_of_bounds:
                    # handle the case where multiple moves out of bounds are being done
                    # meaning we wont update valid moves until we re-enter the canvas boundaries,
                    # but still update the current pointer
                    if (
                        self._out_of_bounds(self.current_point)
                        and not self._out_of_bounds(next_point)
                        and self.was_drawing
                    ):
                        # out of bounds coming in
                        # execute mv points to this edge point
                        # execute pen down
                        # mark in bounds
                        # move to next point
                        edge_point = self._build_edge_point(
                            inner_point=next_point, outer_point=self.current_point
                        )
                        valid_moves_points.append(edge_point)
                        move_command = MoveCommand(points=valid_moves_points)
                        self.commands.append(move_command)
                        pen_down_command = PenCommand(
                            ["40", "01"]
                        )  # non-zero for pen down
                        self.pen_down = True
                        self.commands.append(pen_down_command)

                        new_line = Line(next_point, edge_point, self.color)
                        self.draw_lines.append(new_line)
                        self.pen_down_points.append(edge_point)
                        self.drawer_out_of_bounds = False
                        self.was_drawing = False
                        self.current_point = next_point
                        # reset valid_move_points
                        valid_moves_points = [next_point]

                    elif self._out_of_bounds(
                        self.current_point
                    ) and self._out_of_bounds(next_point):
                        # still out of bounds move next_point
                        self.current_point = next_point
                else:
                    # normal case make a new line
                    valid_moves_points.append(next_point)
                    self.current_point = next_point

        # add final move command if any moves
        if valid_moves_points:
            move_command = MoveCommand(points=valid_moves_points)
            self.commands.append(move_command)

    def _build_edge_point(self, inner_point, outer_point):
        """
        Determine the edge point where this line crosses the drawer's canvas border

        Approach:

        - Get the slope and y-intercept of the line from the given points via:
            m = (y2 - y1)/(x2 - x1)
            b = y - mx

        - Now that we now we have a line equation y = mx + b, based off the relativity of the points, we can
        assert an x/y axis via:

            y = mx + b
            x = (y - b) / m

        or the y-intercept is zero meaning we cross the border at a corner

        - Handle all 8 edge cases where {A, B, C, D} represent a quadrant side and { E, F, G, H } are corners

            H       D      E
                - - - - -
                |   |   |
                |   |   |
            C   - - - - -  A
                |   |   |
                |   |   |
                - - - - -
            G       B      F

        Note: we must also account for when the slope is zero when finding for x axis

        :param inner_point: Point: point for this line that is within the drawers canvas borders
        :param outer_point: Point: point for this line that is out of the drawers canvas borders

        """
        slope = (outer_point.y - inner_point.y) / (outer_point.x - inner_point.x)
        # substitute inner point to solve for b
        b = inner_point.y - (slope * inner_point.x)

        edge_point_x = None
        edge_point_y = None

        # handle edge cases ;) no pun intended
        if outer_point.x > self.canvas.max_x and (
            outer_point.y > self.canvas.min_y and outer_point.y < self.canvas.max_y
        ):
            # A, we can assert that the edge point's x axis will be the self.canvas.max_x
            edge_point_x = self.canvas.max_x
            edge_point_y = (slope * self.canvas.max_x) + b

        elif outer_point.y < self.canvas.min_y and (
            outer_point.x > self.canvas.min_x and outer_point.x < self.canvas.max_x
        ):
            # B, we can assert that the edge point's y axis will be the self.canvas min_y
            if slope == 0:
                edge_point_x = self.canvas.min_y - b
            else:
                edge_point_x = (self.canvas.min_y - b) / slope

            edge_point_y = self.canvas.min_y

        elif outer_point.x < self.canvas.min_x and (
            outer_point.y > self.canvas.min_y and outer_point.y < self.canvas.max_y
        ):
            # C, we can assert that the edge point's x axis will be the self.canvas min_x
            edge_point_x = self.canvas.min_y
            edge_point_y = (slope * self.canvas.min_x) + b

        elif outer_point.y < self.canvas.min_y and (
            outer_point.x > self.canvas.min_x and outer_point.x < self.canvas.max_x
        ):
            # D, we can assert that the edge point's y axis will be the self.canvas max_y
            if slope == 0:
                edge_point_x = self.canvas.max_y - b
            else:
                edge_point_x = (self.canvas.max_y - b) / slope

            edge_point_y = self.canvas.max_y

        elif b == 0:
            # handle corner cases
            if outer_point.x > inner_point.x and outer_point.y > inner_point.y:
                # E, we can assert the x, y axis's are self.canvas.max_x and self.canvas.max_y
                edge_point_x = self.canvas.max_x
                edge_point_y = self.canvas.max_y
            elif outer_point.x > inner_point.x and outer_point.y < inner_point.y:
                # F, we can assert the x, y axis's are self.canvas.max_x and self.canvas.min_y
                edge_point_x = self.canvas.max_x
                edge_point_y = self.canvas.min_y

            elif outer_point.x < inner_point.x and outer_point.y < inner_point.y:
                # G, we can assert the x, y axis's are self.canvas.min_x and self.canvas.min_y
                edge_point_x = self.canvas.min_x
                edge_point_y = self.canvas.min_y

            elif outer_point.x < inner_point.x and outer_point.y > inner_point.y:
                # H, we can assert the x, y axis's are self.canvas.min_x and self.canvas.max_y
                edge_point_x = self.canvas.min_x
                edge_point_y = self.canvas.max_y

        if edge_point_x is not None and edge_point_y is not None:
            return Point(int(edge_point_x), int(edge_point_y))
        else:
            raise RuntimeError("Failed building canvas edge point")
