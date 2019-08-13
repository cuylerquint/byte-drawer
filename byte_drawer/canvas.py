class Point:
    """
    Abstraction for holding coordinate values on a Canvas
    """

    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __repr__(self):
        return "({}, {})".format(self.x, self.y)

    def __str__(self):
        return "({}, {})".format(self.x, self.y)


class Color:
    """
    Abstraction for holding RBGA values for a said color
    """

    def __init__(self, r, g, b, a):
        """
        :param r: int
        :param g: int
        :param b: int
        :param a: int
        """
        self.r = r
        self.g = g
        self.b = b
        self.a = a

    def __repr__(self):
        return "rgba({}, {}, {}, {})".format(self.r, self.g, self.b, self.a)

    def __str__(self):
        return "{} {} {} {}".format(self.r, self.g, self.b, self.a)


class Line:
    def __init__(self, start_point, finish_point, color):
        """
        Represents D

        :param start_point: Point
        :param finish_point: Point
        :param color: Color
        """
        self.start_point = start_point
        self.finish_point = finish_point
        self.color = color

    def __repr__(self):
        return "({}, {}, ({}))".format(self.start_point, self.finish_point, self.color)

    def __str__(self):
        return "({}, {}, ({}))".format(self.start_point, self.finish_point, self.color)

    def __dict__(self):
        return {
            "start_point": self.start_point.__dict__,
            "finish_point": self.finish_point.__dict__,
            "color": str(self.color.__repr__),
        }


class Canvas:
    """
    Abstraction representing what bounds a Drawer Class can draw in
    """

    center_point = Point(0, 0)
    default_color = Color(0, 0, 0, 255)

    def __init__(self, min_x, max_x, min_y, max_y, default_color=None):
        """

        :param min_x: int
        :param max_x: int
        :param min_y: int
        :param max_y: int
        """
        self.min_x = min_x
        self.max_x = max_x
        self.min_y = min_y
        self.max_y = max_y
        self.center_point = Canvas.center_point
        if default_color:
            self.default_color = default_color
        else:
            self.default_color = Canvas.default_color
        self._set_borders()

    def _set_borders(self):
        """
        Make lines out of this instances borders
        """

        max_x_max_y = Point(self.max_x, self.max_y)
        max_x_min_y = Point(self.max_x, self.min_y)
        min_x_min_y = Point(self.min_x, self.min_y)
        min_x_max_y = Point(self.min_x, self.max_y)
        self.borders = list()
        self.borders.append(Line(min_x_max_y, max_x_max_y, self.default_color))  # Top
        self.borders.append(Line(max_x_max_y, max_x_min_y, self.default_color))  # Right
        self.borders.append(
            Line(max_x_min_y, min_x_min_y, self.default_color)
        )  # Bottom
        self.borders.append(Line(min_x_min_y, min_x_max_y, self.default_color))  # Left

    def contains_point(self, point):
        """
        Determine if the given point is in this canvas;'s range

        :param point: Point
        :return: bool
        """

        if (
            point.x > self.min_x
            and point.x < self.max_x
            and point.y > self.min_y
            and point.y < self.max_y
        ):
            return True
        else:
            return False
