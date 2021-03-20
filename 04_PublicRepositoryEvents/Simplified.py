import tkinter as tk
from functools import partial
from tkinter.messagebox import showinfo


def decode_axis(axis, axis_name):
    # idx.weight+size
    info = {
        'weight': 1,
        'size': 0
    }

    if '+' in axis:
        axis, info['size'] = axis.split('+')

    if '.' in axis:
        axis, info['weight'] = axis.split('.')

    info['idx'] = axis

    return {axis_name + '_' + key: int(value) for key, value in info.items()}


def decode_geometry(geometry):
    info = {
        'gravity': 'NEWS'
    }

    if '/' in geometry:
        geometry, info['gravity'] = geometry.split('/')

    row, col = geometry.split(':')
    info.update(decode_axis(row, 'row'))
    info.update(decode_axis(col, 'col'))

    return info


def wrap_widget(widget):
    class WrappedWidget(widget):
        def __init__(self, master=None, geometry='0:0', **kwargs):
            super().__init__(master, **kwargs)

            if geometry is not None:
                self.geometry = decode_geometry(geometry)
                self.grid(
                    row=self.geometry['row_idx'],
                    rowspan=self.geometry['row_size'] + 1,
                    column=self.geometry['col_idx'],
                    columnspan=self.geometry['col_size'] + 1,
                    sticky=self.geometry['gravity']
                )
                self.master.grid_rowconfigure(
                    self.geometry['row_idx'],
                    weight=self.geometry['row_weight']
                )
                self.master.grid_columnconfigure(
                    self.geometry['col_idx'],
                    weight=self.geometry['col_weight']
                )

            self.createWidgets()

        def createWidget(self, name, constructor, geometry, **kwargs):
            self.__setattr__(name, wrap_widget(constructor)(self, geometry, **kwargs))
            return self.__getattribute__(name)

        def createWidgets(self):
            pass

        def __getattr__(self, name):
            return partial(self.createWidget, name)

    return WrappedWidget


@wrap_widget
class Application(tk.Frame):
    def __init__(self, *args, title, **kwargs):
        super().__init__(*args, **kwargs)
        self.master.title(title)


class App(Application):
    def createWidgets(self):
        self.message = "Congratulations!\nYou've found a sercet level!"
        self.F1(tk.LabelFrame, "1:0", text="Frame 1")
        self.F1.B1(tk.Button, "0:0/NW", text="1")
        self.F1.B2(tk.Button, "0:1/NE", text="2")
        self.F1.B3(tk.Button, "1:0+1/SEW", text="3")
        self.F2(tk.LabelFrame, "1:1", text="Frame 2")
        self.F2.B1(tk.Button, "0:0/N", text="4")
        self.F2.B2(tk.Button, "0+1:1/SEN", text="5")
        self.F2.B3(tk.Button, "1:0/S", text="6")
        self.Q(tk.Button, "2.0:1.2/SE", text="Quit", command=self.quit)
        self.F1.B3.bind("<Any-Key>", lambda event: showinfo(self.message.split()[0], self.message))

app = App(title="Sample application")
app.mainloop()
