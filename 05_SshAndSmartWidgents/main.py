import tkinter as tk


class GraphWindow(tk.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.object_builders = {
            'oval': self.create_oval,
            'rectangle': self.create_rectangle,
            'arc': self.create_arc,
        }

        self.default_param = {
            'type': 'oval',
            'coords': (0, 0, 0, 0),
            'border_width': 1,
            'border_color': 'khaki',
            'fill_color': 'goldenrod4',
        }

        self.objects = []
        self.objects_params = []

        self.creating_object = False
        self.moving_object = False
        self.bind('<Button-1>', self._button_click)
        self.bind('<Motion>', self._mouse_move)
        self.bind('<ButtonRelease-1>', self._button_release)

    def create_object(self, param):
        builder = self.object_builders[param['type']]

        return builder(
            *param['coords'],
            fill=param['fill_color'],
            outline=param['border_color'],
            width=param['border_width']
        )

    def set(self, params):
        new_objects = []
        try:
            for idx, param in enumerate(params):
                obj = self.create_object(param)
                new_objects.append(obj)
        except Exception as e:  # Well, I don't know what kind of exception might be raised so whatever
            for obj in new_objects:
                self.delete(obj)

            return idx

        for obj in self.objects:
            self.delete(obj)

        self.objects_params = params
        self.objects = new_objects

    def _button_click(self, event):
        res = self.find_overlapping(event.x, event.y, event.x, event.y)

        if len(res) == 0:
            self._start_object(event)
        else:
            self._start_move(event)

    def _mouse_move(self, event):
        if self.creating_object:
            self._resize_object(event)
        elif self.moving_object:
            self._move_object(event)

    def _button_release(self, event):
        if self.creating_object:
            self._end_object(event)
        elif self.moving_object:
            self._end_move(event)

    def _start_object(self, event):
        self.creating_object = True

        self.current_param = self.default_param.copy()
        self.current_param['coords'] = (event.x, event.y, event.x, event.y)

        self.current_object = self.create_object(self.current_param)

    def _resize_object(self, event):
        self.current_param['coords'] = (
            *self.current_param['coords'][:2],
            event.x, event.y
        )

        self.delete(self.current_object)
        self.current_object = self.create_object(self.current_param)

    def _end_object(self, event):
        self.objects.append(self.current_object)
        del self.current_object

        self.objects_params.append(self.current_param)

        self.creating_object = False
        self.event_generate('<<GraphObjectCreated>>', when='tail')

    def _start_move(self, event):
        self.moving_object = True
        self.prev_pos = (event.x, event.y)
        self.current_object = self.find_overlapping(event.x, event.y, event.x, event.y)[-1]

    def _move_object(self, event):
        self.move(self.current_object, event.x - self.prev_pos[0], event.y - self.prev_pos[1])
        self.prev_pos = (event.x, event.y)

    def _end_move(self, event):
        idx = self.objects.index(self.current_object)
        self.objects_params[idx]['coords'] = tuple(self.coords(self.current_object))

        del self.current_object
        self.moving_object = False
        self.event_generate('<<GraphObjectCreated>>', when='tail')


class TextWindow(tk.Text):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.tag_configure('error', background='red')

        self.objects_params = []

        self.bind('<<Modified>>', self.update_objects)

    @staticmethod
    def _param_to_text(param):
        return '{type} {coords} {border_width} {border_color} {fill_color}'.format(**param)

    @staticmethod
    def _text_to_param(text):
        object_type, *coords, border_width, border_color, fill_color = text.split(' ')
        coords = [x.replace('(', '').replace(',', '').replace(')', '') for x in coords]

        return {
            'type': object_type,
            'coords': tuple(float(x) for x in coords),
            'border_width': float(border_width),
            'border_color': border_color,
            'fill_color': fill_color,
        }

    def set(self, objects_params):
        self.objects_params = objects_params

        self.delete(1.0, 'end')
        for param in self.objects_params:
            self.insert('end', self._param_to_text(param) + '\n')

    def update_objects(self, _):
        self.tag_remove('error', 1.0, 'end')
        texts = self.get(1.0, tk.END).splitlines()

        self.objects_params = []

        idx = 0
        self.param2line = {}
        for line, text in enumerate(texts):
            if len(text.strip()) == 0:
                continue

            self.param2line[idx] = line
            idx += 1

            try:
                param = self._text_to_param(text)
            except ValueError:
                self.set_error_line(line + 1)
            else:
                self.objects_params.append(param)

        self.event_generate('<<TextObjectCreated>>', when='tail')
        self.edit_modified(False)

    def set_error_line(self, line):
        self.tag_add('error', '{}.0'.format(line), '{}.end'.format(line))

    def set_error_param(self, param_idx):
        line = self.param2line[param_idx] + 1
        self.set_error_line(line)


class GraphEditor(tk.Frame):
    def __init__(self):
        super().__init__()

        self.objects_params = []

        self.text_window = TextWindow(self, borderwidth=5)
        self.text_window.grid(row=0, column=0, sticky=tk.NSEW)
        self.text_window.bind('<<TextObjectCreated>>', self._update_from_text)

        self.graph_window = GraphWindow(self, borderwidth=5, background='gray')
        self.graph_window.grid(row=0, column=1, sticky=tk.NSEW)
        self.graph_window.bind('<<GraphObjectCreated>>', self._update_from_graph)

        self.quit_button = tk.Button(self, text='Quit', command=self.quit)
        self.quit_button.grid(row=1, column=1, sticky=tk.NE)

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

    def _update_from_graph(self, _):
        self.objects_params = self.graph_window.objects_params

        self.text_window.set(self.objects_params)

    def _update_from_text(self, _):
        res = self.graph_window.set(self.text_window.objects_params)
        if res is None:
            self.objects_params = self.text_window.objects_params
        else:
            self.text_window.set_error_param(res)


def main():
    graph_editor = GraphEditor()
    graph_editor.grid(sticky=tk.NSEW)
    graph_editor.master.grid_rowconfigure(0, weight=1)
    graph_editor.master.grid_columnconfigure(0, weight=1)

    graph_editor.mainloop()


if __name__ == '__main__':
    main()
