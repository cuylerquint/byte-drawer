import flask
from flask import Flask, render_template, flash

from byte_drawer import Processor

app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'


@app.route("/", methods=["GET", "POST"])
def index():
    if flask.request.method == "POST":
        try:
            bytes = flask.request.values.get("bytes") or flask.request.values.get(
                "example_bytes"
            )
            if bytes:
                processor = Processor(draw_input_stream=bytes, display=False)
                return render_template(
                    "index.html",
                    bytes=bytes,
                    show_grid=True,
                    pen_up_points=[
                        point.__dict__ for point in processor.parser.pen_up_points
                    ],
                    pen_down_points=[
                        point.__dict__ for point in processor.parser.pen_down_points
                    ],
                    lines=[line.__dict__() for line in processor.parser.draw_lines],
                    canvas_range={
                        "min_x": processor.parser.canvas.min_x - 300,
                        "max_x": processor.parser.canvas.max_x + 300,
                        "min_y": processor.parser.canvas.min_y - 300,
                        "max_y": processor.parser.canvas.max_y + 300,
                    },
                    commands_ops=processor.parser.result,
                )
            else:
                return render_template("index.html", bytes="", show_grid=False)

        except ValueError as err:
            flash("Something went wrong! {}".format(err))
            return render_template("index.html", bytes=bytes, show_grid=False)
        except RuntimeError as err:
            flash("Something went wrong! {}".format(err))
            return render_template("index.html", bytes=bytes, show_grid=False)
        except:
            flash("Something unknown went wrong! Were on it!")
            return render_template("index.html", bytes=bytes, show_grid=False)

    else:
        return render_template("index.html", bytes="", show_grid=False)


if __name__ == "__main__":
    app.run()
