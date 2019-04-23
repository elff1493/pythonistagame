from scene import *

import ui
import filedata
class test(Scene):
    def setup(self):
        self.data = filedata.worldfile('undergrouwnd.db')
        self.tap = Touch(0,0,0,0,0)
        self.pos = Point(0,0)
        self.v = Point(0,0)
        self.offset = Point(0,0)
        with ui.ImageContext(34, 26) as ctx:
            data = ctx.get_image()
            self.tiles = SpriteNode(Texture(data), parent=self, size=self.size + (64, 64), position=self.size/2)
        with open("resorces/shaders/tiles") as file:
            self.tiles.shader = Shader(file.read())
        i = Texture('resorces/IMG_4287.PNG')
        #i = Texture('resorces/BLOCKS.PNG')
        i.filtering_mode = 1
        self.tiles.shader.set_uniform("map", i)
        self.tiles.shader.set_uniform("scale", (16/34, 16/26))
        self.newblocks()

    def update(self):
        v = 0.01
        pos = self.pos + (self.v )
        p = self.pos + self.v
        offset = Point(pos.x // 32, pos.y // 32)
        self.tiles.position = (p.x%32, p.y%32) + (self.size/2)
        #offset = Point(self.pos.x // 64, self.pos.y // 64)
        #print(self.offset, "t")
        if offset[0] != self.offset[0] or offset[1] != self.offset[1]:
            print(offset)
            self.tiles.position = Vector2(p.x % 32, p.y % 32) + (self.size / 2)
            self.offset = offset
            self.newblocks()

    def newblocks(self):
        with ui.ImageContext(34, 26) as ctx:
            for x in range(34):
                for y in range(26):
                    d = self.data.block((int(x - self.offset.x), int(y + self.offset.y)))
                    #d = self.data.block((8,0))


                    #d2,d1 = 1,0

                    ui.set_color((((d % 16)/15), 1 - ((d // 16)/15), 1, 1))
                    #ui.set_color(3/16)
                    ui.fill_rect(x, y, 1, 1)
            data = ctx.get_image()

        i = Texture(data)
        i.filtering_mode = 1
        self.tiles.shader.set_uniform("data", i)

    def touch_began(self, t):
        self.tap = t

    def touch_moved(self, t):
        self.v = (t.location - self.tap.location)
        #self.offset += (1,0)
        #self.newblocks()

    def touch_ended(self, t):
        self.pos += self.v
        self.v = Point(0,0)

class TileShader(SpriteNode):
    def __init__(self, parent=None, data=None):
        self.up = False
        self.data = data
        if parent:
            with ui.ImageContext(34, 26) as ctx:
                data = ctx.get_image()
                super().__init__(Texture(data), parent=parent, size=parent.size + (64, 64), position=parent.size/2)
        else:
            super().__init__()
        self._pos = Vector2(0,0)
        self._offset = Point(0, 0)
        with open("resorces/shaders/tiles") as file:
            self.shader = Shader(file.read())
        i = Texture('resorces/IMG_4287.PNG')
        # i = Texture('resorces/BLOCKS.PNG')
        i.filtering_mode = 1
        self.shader.set_uniform("map", i)
        self.shader.set_uniform("scale", (16 / 34, 16 / 26))

        #self._offset.x = self._pos.x // 32
        #self._offset.y = self._pos.y // 32
        #self.newblocks()

    def _refresh(self):
        #offset = Point(self._pos.x // 32, self._pos.y // 32)
        self.position = Vector2(self._pos.x % 32, self._pos.y % 32) + (self.size / 2) - (32, 32)
        # offset = Point(self.pos.x // 64, self.pos.y // 64)
        # print(self.offset, "t")
        if self._pos.x // 32 != self._offset[0] or self._pos.y // 32 != self._offset[1] or self.up:
            self._offset.x = self._pos.x // 32
            self._offset.y = self._pos.y // 32
            self.newblocks()
            self.up = False

    def newblocks(self):
        # get new data
        with ui.ImageContext(34, 26) as ctx:
            for x in range(34):
                for y in range(26):
                    d = self.data.block_get((int(x - self._offset.x), int(y - self._offset.y)))
                    #d = 45
                    ui.set_color((((d % 16)/15), 1 - ((d // 16)/15), 1, 1))
                    ui.fill_rect(x, 25-y, 1, 1)
            data = ctx.get_image()

        i = Texture(data)
        i.filtering_mode = 1
        self.shader.set_uniform("data", i)


#t = test()
#run(t)