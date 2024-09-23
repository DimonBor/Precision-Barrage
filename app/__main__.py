import gi
import sys
import math

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, Graphene


APP_NAME = "PrecisionBarrage"


class Line():
    def __init__(self):
        self.start = Graphene.Point()
        self.end = Graphene.Point()


scale_line = Line()
firing_line = Line()


class MainWindow(Gtk.ApplicationWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.set_opacity(0.5)

        self.grid = Gtk.Grid(
            row_spacing=6, column_spacing=6,
            column_homogeneous=True)

        self.info_box = Gtk.Box(spacing=15)

        self.scale_label = Gtk.Label().new(("  Scale"))
        self.scale_entry = Gtk.Entry()
        self.scale_separator = Gtk.Separator().new(Gtk.Orientation(1))
        self.range_label = Gtk.Label().new(("Range: "))
        self.range_value = Gtk.Label()
        self.range_separator = Gtk.Separator().new(Gtk.Orientation(1))
        self.azimuth_label = Gtk.Label().new(("Azimuth: "))
        self.azimuth_value = Gtk.Label()
        self.azimuth_separator = Gtk.Separator().new(Gtk.Orientation(0))

        self.info_box.append(self.scale_label)
        self.info_box.append(self.scale_entry)
        self.info_box.append(self.scale_separator)
        self.info_box.append(self.range_label)
        self.info_box.append(self.range_value)
        self.info_box.append(self.range_separator)
        self.info_box.append(self.azimuth_label)
        self.info_box.append(self.azimuth_value)

        self.grid.attach(self.info_box, 0, 0, 1, 1)
        self.grid.attach(self.azimuth_separator, 0, 1, 1, 1)

        self.map_area = MapArea()
        self.map_area.queue_draw()
        self.grid.attach(self.map_area, 0, 2, 1, 1)
        self.set_child(self.grid)

        self.middle_press_event = Gtk.GestureClick()
        self.middle_press_event.set_button(2)
        self.middle_press_event.connect('pressed', self.set_scale_1)

        self.middle_release_event = Gtk.GestureClick()
        self.middle_release_event.set_button(2)
        self.middle_release_event.connect('released', self.set_scale_2)

        self.right_press_event = Gtk.GestureClick()
        self.right_press_event.set_button(3)
        self.right_press_event.connect('released', self.set_firing_1)

        self.left_press_event = Gtk.GestureClick()
        self.left_press_event.set_button(1)
        self.left_press_event.connect('pressed', self.set_firing_2)

        self.add_controller(self.middle_press_event)
        self.add_controller(self.middle_release_event)
        self.add_controller(self.left_press_event)
        self.add_controller(self.right_press_event)

    def set_scale_1(self, gesture_click, n_press, x, y):
        scale_line.start = self.compute_point(
            target=self.map_area, point=Graphene.Point().init(x, y))[1]

    def set_scale_2(self, gesture_click, n_press, x, y):
        scale_line.end = self.compute_point(
            target=self.map_area, point=Graphene.Point().init(x, y))[1]
        self.map_area.queue_draw()
        self.compute_firing()

    def set_firing_1(self, gesture_click, n_press, x, y):
        firing_line.start = self.compute_point(
            target=self.map_area, point=Graphene.Point().init(x, y))[1]
        self.map_area.queue_draw()
        self.compute_firing()

    def set_firing_2(self, gesture_click, n_press, x, y):
        firing_line.end = self.compute_point(
            target=self.map_area, point=Graphene.Point().init(x, y))[1]
        self.map_area.queue_draw()
        self.compute_firing()

    def compute_firing(self):
        map_scale = int(self.scale_entry.get_buffer().get_text())
        m_per_pixel = map_scale/scale_line.start.distance(scale_line.end)[0]
        firing_distance_pixels = firing_line.start.distance(firing_line.end)[0]
        self.range_value.set_label(
                f"{firing_distance_pixels*m_per_pixel:.2f}"
            )

        radians_on_target = math.atan2(
                firing_line.end.x - firing_line.start.x,
                firing_line.start.y - firing_line.end.y,
            )
        self.azimuth_value.set_label(
                f"{math.degrees(radians_on_target)
                   if math.degrees(radians_on_target) > 0
                   else math.degrees(radians_on_target) + 360:.2f}"
            )


class MapArea(Gtk.DrawingArea):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.set_hexpand(True)
        self.set_vexpand(True)
        self.set_draw_func(self.draw, None)

    def draw(self, area, context, w, h, user_data):
        context.set_source_rgb(50.0/255, 168.0/255, 82.0/255)
        context.move_to(scale_line.start.x, scale_line.start.y)
        context.line_to(scale_line.end.x, scale_line.end.y)
        context.stroke()
        context.set_source_rgb(207.0/255, 12.0/255, 38.0/255)
        context.move_to(firing_line.start.x, firing_line.start.y)
        context.line_to(firing_line.end.x, firing_line.end.y)
        context.stroke()

        return False


class MainApp(Gtk.Application):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.connect('activate', self.on_activate)

    def on_activate(self, app):
        self.win = MainWindow(application=app, title=APP_NAME)
        self.win.present()


app = MainApp(application_id="com.cyberbydlo.PrecisionBarrage")
app.run(sys.argv)
