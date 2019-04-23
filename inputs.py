from scene import SpriteNode, Texture, Vector2, Node, LabelNode


class DPad(SpriteNode):
    def __init__(self,  *args, **kargs):
        kargs["size"] = (250,250)
        kargs["position"] = (0, 0)
        super().__init__(Texture('resorces/dpad.PNG'), *args, **kargs)

        self.anchor_point = (0, 0)
        self.alpha = 0.95

        self.middle = SpriteNode(Texture('resorces/dstick.PNG'), position=self.size/2, size=(50, 50), parent=self)
        self.middle.alpha = 0.9
        self.value = Vector2(0, 0)


    def move(self, to):
        if to:
            p = to - self.size/2
            self.middle.position = (p / abs(p)) * min(abs(p), 125) + (
                125, 125)

            value = (to * (1 / 125, 1 / 125)) - (1, 1)
            self.value.x = max(min(value[0], 1), -1)
            self.value.y = max(min(value[1], 1), -1)
        else:
            self.value = Vector2(0, 0)
            self.middle.position = self.size/2

class Ui(Node):
    def __init__(self, *args, **kargs):
        super().__init__(*args, **kargs)
        self.dpad = DPad(parent=self)
        self.hotbar = ItemMenu(parent=self, num=(10, 1))


class ItemMenu(SpriteNode):
    def __init__(self, datafiles, data, taps, *args, num=(1, 10), offset=0, **kargs):
        super().__init__(*args, **kargs)
        self.tapid = None
        self._parent = kargs["parent"]
        self.offset = offset
        self.ITEMSIZE = 64
        self.BW = 3
        self.bg = SpriteNode(size=((num[0]*(self.ITEMSIZE+self.BW))+self.BW, (num[1]*(self.ITEMSIZE+self.BW))+self.BW), parent=self)# dont know why i cant use selfs sprite stuff
        self.bg.anchor_point = (0, 0)
        self.size = ((num[0]*(self.ITEMSIZE+self.BW))+self.BW, (num[1]*(self.ITEMSIZE+self.BW))+self.BW)

        self.data = data # for geting data
        self.taps = taps # for tap events

        self.__hide = False
        self.datafiles = datafiles
        self.id = 1
        self.size = num
        self.drager = SpriteNode()
        self.other = None
        self.icons = []
        self.counts = []
        self.tapslot = False
        self.data.items_load(self.id, self.size[0]*self.size[1])
        print(self.data.items, "l")

        for x in range(int(self.size[0])):
            for y in range(int(self.size[1])):
                i = y+(int(x*self.size[1]))
                ii = int(self.get_item(i)[0])
                t = self.datafiles.block[ii]
                self.icons.append(SpriteNode(t,
                                             parent=self,
                                             position=(x*(self.ITEMSIZE+self.BW)+self.BW, y*(self.ITEMSIZE+self.BW)+self.BW),
                                             size=(self.ITEMSIZE, self.ITEMSIZE)
                                             )
                                  )
                self.icons[-1].anchor_point = (0, 0)

                self.counts.append(LabelNode(str(int(self.get_item(i)[1])),
                                             parent=self,
                                             position=(x * (self.ITEMSIZE + self.BW) + self.BW,
                                                       y * (self.ITEMSIZE + self.BW) + self.BW),

                                             )
                                   )
                self.counts[-1].anchor_point = (0, 0)
        #self.hide = True

    @property
    def hide(self):
        return self.__hide

    @hide.setter
    def hide(self, h):
        if h:
            self.remove_from_parent()
            self.taps.layer(self.tapid, -1)
        else:
            self._parent.add_child(self)
            self.taps.layer(self.tapid, 1)

        self.__hide = h

    def touch_began(self, t):
        point = self.point_from_scene(self.taps.touchb.location)
        for i, j in enumerate(self.icons):
            if point in j.bbox:
                item = self.get_item(i)
                if item[0]:
                    self.drager.position = point
                    self.drager.texture = self.datafiles.block[item[0]]
                    self.drager.size = (64, 64)

                    #find slot
                    self.tapslot = i+1 # the index of the box tapped, need to know for when it is dropped

    def drag(self, touch): # remove var pass

        if self.tapslot:
            self.add_child(self.drager)
            self.drager.z_position = 10
            self.drager.position = self.point_from_scene(touch.location)  # point -> scene

    def drop(self, touch, other):
        self.drager.remove_from_parent()
        if self.tapslot:
            start = self.tapslot - 1
            self.tapslot = False
            pos = other.point_from_scene(touch.location)
            for i, j in enumerate(other.icons):
                if pos in j.bbox:
                    end = i
                    items = [self.get_item(start), other.get_item(end)]
                    break
            else:
                return


            if items[0][0] == items[1][0]: # if the items are the same we move as much as we can over, else we just swap
                if items[0][1] + items[1][1] != 255*2:
                    total = items[0][1] + items[1][1]
                    if total > 255:
                        self.set_item(start, id=items[0][0], value=total % 255)
                        other.set_item(end, id=items[0][0], value=255)
                    else:
                        self.set_item(start, id=0, value=0)
                        other.set_item(end, id=items[0][0], value=total)


            else:
                self.set_item(start, id=items[1][0], value=items[1][1])
                other.set_item(end, id=items[0][0], value=items[0][1])

            #self.icons[start].texture = self.datafiles.block[self.get_item(start)[0]]
            #self.icons[start].size = (64, 64)
            #self.counts[start].text = str(self.get_item(start)[1]) # todo

            #other.icons[end].texture = self.datafiles.block[other.get_item(end)[0]]
            #other.icons[end].size = (64, 64)
            #other.counts[end].text = str(other.get_item(end)[1])

    def _refresh(self, address):
        self.icons[address].texture = self.datafiles.block[self.get_item(address)[0]]
        self.icons[address].size = (64, 64)
        self.counts[address].text = str(self.get_item(address)[1])

    def set_item(self, address, id=None, value=None):  # todo
        address += self.offset
        if value is not None:
            self.data.items[self.id][2 * address + 1] = value
            if not value:
                self.data.items[self.id][2 * address] = 0
        if id is not None:
            self.data.items[self.id][2 * address] = id
        self._refresh(address-self.offset)

    def get_item(self, address): #todo
        address += self.offset
        return self.data.items[self.id][2 * address], self.data.items[self.id][2 * address + 1]


class HotBar(ItemMenu):
    def __init__(self, *args, **kargs):
        super().__init__(*args, **kargs, num=(10, 1))
        self.select = SpriteNode(Texture('emj:Anger_Symbol'), position=(0, 0), size=(75, 69), parent=self)
        self.select.anchor_point = (0, 0)
        self.select.alpha = 0.95
        self.select.position = (self.BW, self.BW)
        self.holding = 0

    def hold(self, id):
        self.holding = id
        self.select.position = (id * (self.ITEMSIZE + self.BW), 0)

    def drop(self, touch, other):
        if self.taps.touchb.location == touch.location:
            for i, j in enumerate(self.icons):
                if self.point_from_scene(touch.location) in j.bbox:
                    self.hold(i)
        else:
            super().drop(touch, other)







