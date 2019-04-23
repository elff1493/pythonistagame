from graphics import scren
from ui import View, load_view, get_window_size, Button, ListDataSource
from scene import SceneView
from os import listdir


class app(View):
    def init(self):
        self.main = load_view('mainmenu.pyui')
        self.lanui = load_view('lan.pyui')
        self.game = SceneView()
        self.game.shows_fps = True
        self.game.frame = (0, 0, get_window_size()[0], get_window_size()[1])

        self.main['worlds'].data_source.items = listdir('saves')

        self.add_subview(self.main)

    def setWorld(self, event):
        self.main['worldl'].text = str(event.items[event.selected_row])

    def start(self, event):
        self.remove_subview(self.main)
        self.game.scene = scren(name=self.main['worldl'].text)
        self.add_subview(self.game)
        print('game loded as ' + self.main['worldl'].text)
    def lan(self, r):
        self.remove_subview(self.main)
        self.add_subview(self.lanui)
    def start_lan(self, event):
        self.remove_subview(self.main)
        self.game.scene = scren(lan=True)
        self.add_subview(self.game)

        print("connecting to sever")

    def _close(self, event):
        self.close()


print('=' * 15)
print('program started')

v = app()
v.init()
v.present('full_screen', hide_title_bar=True, orientations='landscape')
