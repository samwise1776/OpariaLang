
import importlib.util
import types
from pathlib import Path


class Namespace:
    def __init__(self, **values):
        self.__dict__.update(values)


class LangClass:
    def __init__(self, name, fields=None):
        self.name = name
        self.fields = dict(fields or {})

    def new(self):
        return Namespace(**self.fields)


class LibraryManager:
    def __init__(self):
        self.cache = {}

    def load(self, filename):
        path = Path(str(filename)).resolve()

        if not path.is_file():
            raise FileNotFoundError(path)

        if path.suffix != ".py":
            raise ValueError(
                "Python extension libraries must end in .py"
            )

        if path in self.cache:
            return self.cache[path]

        spec = importlib.util.spec_from_file_location(
            "local_lang_" + str(abs(hash(str(path)))),
            path
        )

        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        self.cache[path] = module
        return module


class GUI:
    def __init__(self):
        self.Gtk = None
        self.Gdk = None
        self.GLib = None
        self.window = None
        self.root = None
        self.widgets = {}
        self.counter = 0
        self.loop = None
        self.callbacks = []
        self.css_provider = None

    def init(self):
        if self.Gtk is not None:
            return self

        import gi
        gi.require_version("Gtk", "4.0")
        gi.require_version("Gdk", "4.0")

        from gi.repository import Gtk, Gdk, GLib

        self.Gtk = Gtk
        self.Gdk = Gdk
        self.GLib = GLib

        self.window = Gtk.Window()
        self.window.set_title("Language GTK4")
        self.window.set_default_size(800, 500)

        self.root = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL,
            spacing=8
        )
        self.root.set_margin_top(12)
        self.root.set_margin_bottom(12)
        self.root.set_margin_start(12)
        self.root.set_margin_end(12)

        self.window.set_child(self.root)
        self.widgets["window"] = self.window
        self.widgets["root"] = self.root
        return self

    def _ensure(self):
        if self.Gtk is None:
            self.init()

    def _id(self, name):
        if name is None:
            self.counter += 1
            return "widget_" + str(self.counter)
        return str(name)

    def _widget(self, name):
        if isinstance(name, str):
            if name not in self.widgets:
                raise ValueError(
                    "Unknown GUI widget: " + name
                )
            return self.widgets[name]
        return name

    def _add(self, widget, name=None, parent="root"):
        key = self._id(name)
        if key in self.widgets:
            raise ValueError("Duplicate widget ID: " + key)

        container = self._widget(parent)

        if isinstance(container, self.Gtk.Box):
            container.append(widget)
        elif isinstance(container, self.Gtk.Grid):
            raise ValueError(
                "Use gui.attach() for grid children"
            )
        elif hasattr(container, "set_child"):
            container.set_child(widget)
        else:
            raise ValueError(
                "Parent does not support children"
            )

        self.widgets[key] = widget
        return key

    def title(self, text):
        self._ensure()
        self.window.set_title(str(text))

    def size(self, width, height):
        self._ensure()
        self.window.set_default_size(
            int(width), int(height)
        )

    def label(self, text="", name=None, parent="root"):
        self._ensure()
        widget = self.Gtk.Label(label=str(text))
        return self._add(widget, name, parent)

    def button(self, text="", name=None, parent="root"):
        self._ensure()
        widget = self.Gtk.Button(label=str(text))
        return self._add(widget, name, parent)

    def entry(self, placeholder="", name=None, parent="root"):
        self._ensure()
        widget = self.Gtk.Entry()
        widget.set_placeholder_text(str(placeholder))
        return self._add(widget, name, parent)

    def checkbox(self, text="", name=None, parent="root"):
        self._ensure()
        widget = self.Gtk.CheckButton(label=str(text))
        return self._add(widget, name, parent)

    def switch(self, name=None, parent="root"):
        self._ensure()
        return self._add(
            self.Gtk.Switch(), name, parent
        )

    def slider(self, minimum=0, maximum=100,
               step=1, name=None, parent="root"):
        self._ensure()
        widget = self.Gtk.Scale.new_with_range(
            self.Gtk.Orientation.HORIZONTAL,
            float(minimum),
            float(maximum),
            float(step)
        )
        return self._add(widget, name, parent)

    def progress(self, name=None, parent="root"):
        self._ensure()
        return self._add(
            self.Gtk.ProgressBar(), name, parent
        )

    def spinner(self, name=None, parent="root"):
        self._ensure()
        widget = self.Gtk.Spinner()
        widget.start()
        return self._add(widget, name, parent)

    def separator(self, name=None, parent="root"):
        self._ensure()
        return self._add(
            self.Gtk.Separator(
                orientation=self.Gtk.Orientation.HORIZONTAL
            ),
            name, parent
        )

    def image(self, filename, name=None, parent="root"):
        self._ensure()
        widget = self.Gtk.Image.new_from_file(
            str(filename)
        )
        return self._add(widget, name, parent)

    def box(self, name=None, vertical=True,
            spacing=8, parent="root"):
        self._ensure()
        widget = self.Gtk.Box(
            orientation=(
                self.Gtk.Orientation.VERTICAL
                if vertical
                else self.Gtk.Orientation.HORIZONTAL
            ),
            spacing=int(spacing)
        )
        return self._add(widget, name, parent)

    def grid(self, name=None, parent="root"):
        self._ensure()
        return self._add(
            self.Gtk.Grid(), name, parent
        )

    def attach(self, grid, child, column, row,
               width=1, height=1):
        self._widget(grid).attach(
            self._widget(child),
            int(column), int(row),
            int(width), int(height)
        )

    def textview(self, name=None, parent="root"):
        self._ensure()
        return self._add(
            self.Gtk.TextView(), name, parent
        )

    def dropdown(self, options, name=None, parent="root"):
        self._ensure()
        widget = self.Gtk.DropDown.new_from_strings(
            [str(item) for item in options]
        )
        return self._add(widget, name, parent)

    def set_text(self, name, text):
        widget = self._widget(name)
        text = str(text)

        if isinstance(widget, self.Gtk.TextView):
            widget.get_buffer().set_text(text)
        elif hasattr(widget, "set_text"):
            widget.set_text(text)
        elif hasattr(widget, "set_label"):
            widget.set_label(text)
        else:
            raise ValueError("Widget has no text setter")

    def get_text(self, name):
        widget = self._widget(name)

        if isinstance(widget, self.Gtk.TextView):
            buffer = widget.get_buffer()
            return buffer.get_text(
                buffer.get_start_iter(),
                buffer.get_end_iter(),
                False
            )

        if hasattr(widget, "get_text"):
            return widget.get_text()

        if hasattr(widget, "get_label"):
            return widget.get_label()

        raise ValueError("Widget has no text getter")

    def set_value(self, name, value):
        widget = self._widget(name)

        if hasattr(widget, "set_value"):
            widget.set_value(float(value))
        elif hasattr(widget, "set_fraction"):
            widget.set_fraction(float(value))
        elif hasattr(widget, "set_active"):
            widget.set_active(bool(value))
        else:
            raise ValueError("Widget has no value setter")

    def get_value(self, name):
        widget = self._widget(name)

        if hasattr(widget, "get_value"):
            return widget.get_value()
        if hasattr(widget, "get_fraction"):
            return widget.get_fraction()
        if hasattr(widget, "get_active"):
            return widget.get_active()

        raise ValueError("Widget has no value getter")

    def on(self, name, signal, callback):
        widget = self._widget(name)

        if not callable(callback):
            raise TypeError("Callback must be callable")

        def handler(*args):
            return callback()

        self.callbacks.append(handler)
        return widget.connect(str(signal), handler)

    def css(self, stylesheet):
        self._ensure()
        provider = self.Gtk.CssProvider()
        provider.load_from_data(
            str(stylesheet).encode("utf-8")
        )

        display = self.Gdk.Display.get_default()
        if display is None:
            raise RuntimeError("No GTK display available")

        self.Gtk.StyleContext.add_provider_for_display(
            display,
            provider,
            self.Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )
        self.css_provider = provider

    def add_class(self, name, css_class):
        self._widget(name).add_css_class(str(css_class))

    def remove_class(self, name, css_class):
        self._widget(name).remove_css_class(
            str(css_class)
        )

    def show(self):
        self._ensure()
        self.window.present()

    def close(self):
        if self.window:
            self.window.close()

    def quit(self):
        if self.loop and self.loop.is_running():
            self.loop.quit()

    def run(self):
        self._ensure()
        self.loop = self.GLib.MainLoop()

        def closed(*args):
            self.quit()

        self.window.connect("close-request", closed)
        self.window.present()
        self.loop.run()

    def call(self, name, method, *args):
        """
        Access public GTK widget methods.

        Example:
        gui.call("my_button", "set_sensitive", False)
        """
        widget = self._widget(name)
        method = str(method)

        if method.startswith("_"):
            raise ValueError("Private methods unavailable")

        target = getattr(widget, method, None)

        if not callable(target):
            raise ValueError(
                "Unknown GTK method: " + method
            )

        return target(*args)

    def methods(self, name):
        widget = self._widget(name)

        return sorted(
            method
            for method in dir(widget)
            if not method.startswith("_")
            and callable(getattr(widget, method, None))
        )


gui = GUI()
libraries = LibraryManager()


def namespace(**values):
    return Namespace(**values)


def create_class(name, fields=None):
    return LangClass(name, fields)


def load_library(filename):
    return libraries.load(filename)
