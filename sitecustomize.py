"""XENOVA Tkinter compatibility patch.

The custom Canvas rounded-rectangle helper historically passed Tkinter arc
start/extent values positionally. Tkinter treats all positional arguments
before keyword options as coordinates, so those calls raise:
    TclError: wrong # coordinates: expected 0 or 4, got 6

Keep the existing UI code intact while normalising the legacy six-coordinate
form at the Canvas boundary. This can be removed once interface.py uses
start= and extent= everywhere.
"""

import tkinter as tk

_original_create_arc = tk.Canvas.create_arc


def _xenova_create_arc(self, *args, **kwargs):
    # Legacy XENOVA form:
    #   create_arc(x1, y1, x2, y2, start, extent, ...)
    # Convert the two angle arguments into proper Tkinter options.
    if len(args) >= 6:
        try:
            float(args[0])
            float(args[1])
            float(args[2])
            float(args[3])
            start = args[4]
            extent = args[5]
            args = args[:4] + args[6:]
            kwargs.setdefault("start", start)
            kwargs.setdefault("extent", extent)
        except (TypeError, ValueError):
            pass

    return _original_create_arc(self, *args, **kwargs)


# Patch only the Tkinter Canvas method used by XENOVA.
tk.Canvas.create_arc = _xenova_create_arc
