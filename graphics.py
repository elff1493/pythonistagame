from filedata import worldfile, datafiles, Lanfile
from scene import run, Scene, Texture, SpriteNode, Touch, Vector2, LANDSCAPE, LabelNode, Node
import tile_shader
import inputs


def ro(i):
    if i < 0:
        return int(i - 1)
    return int(i)

def resizep(a,b,c,id):
    a = Vector2(a[0], a[1])
    b = Vector2(b[0], b[1])
    c = Vector2(c[0], c[1])

    a = (a / b) * c
    x1, y1 = a[0], a[1]
    x2, y2 = (a / b) * c
    t = Touch(x1, y1, x2, y2, id)
    print(x1, y1, x2, y2)
    return Touch(x1, y1, x2, y2, id)

class scren(Scene):
    def __init__(self, *args, name='defultworld', lan=False, **kwargs):
        self.init = False
        self.setupinit = False
        self.name = name
        self.lan = lan
        super().__init__(*args, **kwargs)
        if lan:
            self.data = Lanfile(self)

        else:
            self.data = worldfile(self.name)

        self.datafiles = datafiles(debug=False)
        self.taps = taps()

        #self.pos = Vector2(0, 0)
        self.v = Vector2(0, 0)
        self.speed = 6


        self.slots = []
        self.SLOTS = []
        self.lb = []
        self.entity = []

        # nodes
        self.tiles = None
        self.bar = None

        self.texu = []

        for x in range(16):
            for y in range(16):
                self.texu.append(
                    self.datafiles.blocks.subtexture(((y / 16), 1 - ((x + 1) / 16), 1 / 16, 1 / 16)))
                self.texu[-1].filtering_mode = 1
        self.MU = self.datafiles.get_values("mu.txt")

        self.blockv = self.datafiles.get_values("values.txt")

        self.init = True
        self.zize = 0 #?



    def setup(self):
        print("setup")
        #self.bace = self
        self.zize = (1, 1)
        self.bace = Node(parent=self, position=(0, 0))
        self.bace.size = Vector2(1024, 768)
        self.tsize = Vector2(1024, 768)
        self.zize = Vector2(self.size[0] / 1024, self.size[1] / 768)
        self.bace.x_scale = self.size[0] / 1024
        self.bace.y_scale = self.size[1] / 768



        self.tiles = tile_shader.TileShader(parent=self.bace, data=self.data)
        self.data.player.newplayer()
        self.hotbar = inputs.HotBar(self.datafiles, self.data, self.taps, parent=self.bace, position=(300, 14))
        self.invintory = inputs.ItemMenu(self.datafiles, self.data, self.taps, num=(9, 4), parent=self.bace, position=(300, 80), offset=10)
        self.hotbar.other = self.invintory
        self.invintory.other = self.hotbar
        self.ham = SpriteNode(Texture("iow:arrow_right_b_256"), parent = self.bace, position = self.hotbar.bbox.origin + self.hotbar.bbox.size)
        self.ham.anchor_point = (0.3, 0.75)
        self.ham.x_scale = 0.5
        self.ham.y_scale = 0.5
        self.invintory.anchor_point = (0, 0)

        self.select = SpriteNode(Texture('emj:Anger_Symbol'), position=(0, 0), size=(75, 69), parent=self.bace)
        self.select.anchor_point = (1, 0)
        self.select.alpha = 0.95

        self.directionpad = inputs.DPad(parent=self.bace)

        self.cash = LabelNode(str(self.data.player.cash), position=(0, self.bace.size[1]), parent=self.bace)
        self.cash.anchor_point = (0, 1)

        self.player = SpriteNode(Texture('emj:Hamster_Face'), position=self.bace.size / 2, size=(20, 20), parent=self.bace)

        self.HOTBAR = self.taps.add(self.hotbar.bbox)
        self.INV = self.taps.add(self.invintory.bbox)
        self.DPAD = self.taps.add(self.directionpad.bbox)
        self.CASH = self.taps.add(self.cash.bbox)
        self.HAM = self.taps.add(self.ham.bbox, layer=2)

        self.invintory.tapid = self.INV

        self.taps.size = self.size
        self.taps.zize = self.tsize

        if self.init:
            self.setupinit = True
        if self.lan:
            self.data.loop()
        self.invintory.hide = True
        self.tiles._refresh()

    def update(self):
        if not self.init or not self.setupinit:
            qui = self.view
            while qui.superview:
                qui = qui.superview
            qui.close()
        #caluate
        if not self.taps.now:
            self.v = self.v * (0.98, 0.98)
        pos = self.data.player.pos
        #mu = [0, 0]
        po = (self.tsize / 2 - pos) + (32, 32)

        b = self.data.block_get((ro((po[0]) / 32), ro(po[1] / 32)))
        mu = [self.MU[b], self.MU[b]]

        b = self.data.block_get((ro((po[0] + (self.v[0] * mu[0])) / 32), ro(po[1] / 32)))
        mu[0] = self.MU[b]
        if b == 117:
            if self.v[0] < 0:
                mu[0] = 0
            else:
                mu[0] = 1

        b = self.data.block_get((ro((po[0] / 32)), ro(((po[1] + (self.v[1] * mu[1])) / 32))))

        mu[1] = self.MU[b]

        if b == 117:
            if self.v[1] < 0:
                mu[1] = 0
            else:
                mu[1] = 1

        # applay
        pos -= self.v * mu

        # show
        self.tiles._pos = pos
        self.tiles._refresh() # make setter

        #temp v
        self.data.player.pos = pos
        self.data.pp()


    def touch_began(self, t):
        if not self.init or not self.setupinit:
            qui = self.view
            while qui.superview:
                qui = qui.superview
            qui.close()
        self.view.close()

        pick = self.taps.start(t)
        if pick:
            pass
        if pick == self.HOTBAR:
            self.hotbar.touch_began(self.taps.touch)
        if pick == self.INV and not self.invintory.hide:
            self.invintory.touch_began(self.taps.touch)

    def touch_moved(self, t):
        pick = self.taps.move(t)
        if self.taps.ns == self.DPAD:
            self.directionpad.move(self.taps.touch.location)
            self.v = self.directionpad.value * self.speed

        elif pick == -1 and self.taps.ns == -1:
            self.place()

        if (self.taps.ns == self.INV or self.taps.ns == self.HOTBAR) and (self.taps.now in (self.INV, self.HOTBAR)):
            self.hotbar.drag(self.taps.touch)
            if not self.invintory.hide:
                self.invintory.drag(self.taps.touch)

    def touch_ended(self, t):
        pick = self.taps.end(t)

        self.directionpad.move(False)

        if pick == -1 and (not self.taps.count):
            self.place()
            #self.tiles.newblocks()

        elif pick == self.CASH:
            print('quit')
            self.data.save()
            qui = self.view
            while qui.superview:
                qui = qui.superview
            qui.close()

        elif self.taps.ns == self.INV and not self.invintory.hide:
            if pick == self.INV:
                self.invintory.drop(self.taps.touch, self.invintory)
            elif pick == self.HOTBAR:
                self.invintory.drop(self.taps.touch, self.hotbar)

        elif self.taps.ns == self.HOTBAR:
            if pick == self.INV and not self.invintory.hide:
                self.hotbar.drop(self.taps.touch, self.invintory)
            else:
                self.hotbar.drop(self.taps.touch, self.hotbar)
        elif pick == self.HAM:
            if self.taps.ns == self.HAM:
                self.invintory.hide = not self.invintory.hide

    def place(self):
        if self.hotbar.get_item(self.hotbar.holding)[1]:
            x = self.taps.touch.location + (32, 32)
            a = x - self.data.player.pos

            a = (ro(a[0] / 32), ro(a[1] / 32))
            b = self.data.block_get(a)
            if self.hotbar.get_item(self.hotbar.holding)[0] != b:
                self.data.player.cash += self.blockv[b] #add diffrance

                self.cash.text = str(self.data.player.cash)
                # self.lb[self.num].text = str(self.data.player.count(self.num))

                self.data.block_set(a, self.hotbar.get_item(self.hotbar.holding)[0])
                self.hotbar.set_item(self.hotbar.holding, value=self.hotbar.get_item(self.hotbar.holding)[1]-1)
                #self.data.player.set(self.hotbar.holding, self.data.player.item(self.hotbar.holding), self.data.player.count(self.num) - 1)
                self.tiles.newblocks()

    def stop(self):
        self.data.save()

    def run(self):
        run(self, show_fps=True, orientation=LANDSCAPE, multi_touch=True)


class taps:
    def __init__(self):
        self.size = None
        self.zize = None
        self.touch = Touch(0, 0, 0, 0, 0)
        self.count = 0
        self.locations = []
        self.now = False
        self.n = -1
        self.ns = -1
        self.nm = -1
        self.ne = -1

    def resizep(self, t):
        #return t
        a = Vector2(t.location[0], t.location[1])
        b = Vector2(self.size[0], self.size[1])
        c = self.zize
        c = Vector2(c[0], c[1])

        #b = [1, 1]
        #c = [1, 1]
        b, c = c, b

        x1 = (b[0] / c[0]) * a[0]
        y1 = (b[1] / c[1]) * a[1]

        a = Vector2(t.prev_location[0], t.prev_location[1])

        x2 = (b[0] / c[0]) * a[0]
        y2 = (b[1] / c[1]) * a[1]
        #print(x1, y1, x2, y2)

        return Touch(x1, y1, x2, y2, t.touch_id)

    def start(self, t):
        t = self.resizep(t)
        self.now = True
        self.touchb = t
        self.touch = t
        self.count = 0
        self.ns = -1
        l = 0
        for i, j in enumerate(self.locations):
            if j[0].contains_point(t.location):
                if j[1] > l:
                    self.ns = i
                    l = j[1]
        return self.ns

    def move(self, t):
        t = self.resizep(t)
        self.now = True
        self.touchm = t
        self.touch = t
        self.count += 1
        self.nm = -1
        l = 0
        for i, j in enumerate(self.locations):
            if j[0].contains_point(t.location):
                if j[1] > l:
                    self.nm = i
                    l = j[1]
        return self.nm

    def end(self, t):
        t = self.resizep(t)
        self.now = False
        self.touche = t
        self.touch = t
        self.ne = -1
        l = 0
        for i, j in enumerate(self.locations):
            if j[0].contains_point(t.location):
                if j[1] > l:
                    self.ne = i
                    l = j[1]
        return self.ne

    def add(self, item, layer=1):
        self.locations.append((item, layer))
        return len(self.locations) - 1

    def layer(self, id, l):
        self.locations[id] = (self.locations[id][0], l)

if __name__ == '__main__':
    # import main
    print("=" * 15)
    print('graphics run')
    screen = scren(name='undergrouwnd.db')
    screen.run()
    print("world started at", screen.data.name)

    '''
    todo be do
    
    remove textuer map at spawn _ done
    cleen code _ done
    class for tap inputs _ done
    colistion detection done
    d pad for movement _ done
    player sprght done
    improve tap for placeing blocks - done
    whrightup canced - might do documentation 
    
    cleen code _ done
    main menu _ wip, paused
    hot-bar _ wip, will replace 
    inventory manager _ wip
    
    upgrade block placeing to add items and remaping(to mine)
    bugs
        
    autosaves
        options for autosaves time
    
    deleat space from ram thats not near the playsers location
        blocks
        entity's 
    
    entitys
        bad guys
        other players
        
    store more infirmation to file
        player pos
        chests
        entitiys
    
    pealing noise
        terrain generation
        
    helth bar
        mana/stamina/food/xp/other system bars
        combat
        
    upgrade tap system to event baced
    
    shop
        
    servers 
    multilayer
    
    '''
