from sqlite3 import connect
from os import path
from sys import platform
from scene import Texture
if platform == "ios":
    from scene import Vector2
else:
    class Vector2:
        def __init__(self, x, y):
            self.x = x
            self.y = y
#from tablegen import showfile

import socket
import struct
from struct import pack, unpack
from _thread import *
DEFULTBLOCK = bytearray([1 for i in range(32 * 32)])

# for i in range(32):
# DEFULTBLOCK[i] = 201
# DEFULTBLOCK[i] = 200
# DEFULTBLOCK[i*32] = 200
# DEFULTBLOCK[(i*32)-1] = 200
DEFULTBLOCK[0] = 253


class Parser:
    def __init__(self, file):
        self.data = file
        self.bytes = 0
        self.handles = {
            1: self.newPlayer,
            3: self.update,
            2: self.use,
            4: self.inventory

        }
        self.sizes = {
            3: 1032

        }

    def parse(self, data):
        if self.bytes:
            data = self.bytes + data
        while data:
            num = data[0]
            self.bytes = data # store if we need more data from nxst call
            data = data[1:] # the type of data

            if self.sizes[num] <= len(data): # will it fit?

                data = self.handles[num](data)
                if not data:
                    self.bytes = 0
            else:
                data = 0 # get more data


    def newPlayer(self, data):
        return data[:]

    def update(self, data):
        x, y, *b = unpack("=ii1024B", data[:1032])
        self.data.pads[(x, y)] = bytearray(b)
        #print((x, y))
        self.data.root.tiles.up = True
        #self.data.root.tiles._offset.y = 0.1
        #print("data out")
        return data[(32*32)+8:]

    def use(self, data):
        pass

    def inventory(self, data):
        pass

class Lanfile:
    def __init__(self, root):
        self.root = root
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect(("192.168.1.122", 5555))
        self.ex = 'saves/'
        self.name = "" # add selector
        self.pads = {}
        self.x = 0
        self.y = 0
        #self.pos = [0, 0]
        #self.v = [0, 0]
        self.player = Player([0, 0, 'person1', bytearray(200), 1])
        self.player.newplayer()
        self.items = {}
        self.parser = Parser(self)

    def block_set(self, xy, data):
        p = (int(xy[0] // 32), int(xy[1] // 32))
        a = ((int(xy[0]) % 32) + (int(xy[1]) % 32) * 32)
        self.pads[p][a] = data
        self.socket.send(pack("=BiiB", 3, int(xy[0]), int(xy[1]), data))

    def block_get(self, xy):
        p = (xy[0] // 32, xy[1] // 32)
        if p not in self.pads:
            return 2
        return self.pads[p][((xy[0] & 31) + ((xy[1] & 31) * 32))]

    def loop(self):
        start_new_thread(self._loop, ())

    def _loop(self):
        try:
            x, y = 0, 0
            while True:
                data = self.socket.recv(100)
                if data:#    get update
                    #print("get;", data)
                    self.parser.parse(data)



        except Exception as e:
            print(e)

    def pp(self):
        if abs(self.x - self.player.pos.x) > 0.1 or abs(self.y - self.player.pos.y) > 0.1:
            self.x = self.player.pos.x
            self.y = self.player.pos.y
            #print(self.x, self.y)
            self.socket.send(pack("=Bii", 1, int(self.x), int(self.y)))


    def items_load(self, id, size):
        self.items[id] = self.player.inv

    def save(self):
        print("qiute sever")




class worldfile:
    def __init__(self, name):
        self.name = name
        self.ex = 'saves/'
        if not path.exists(self.ex + self.name):
            conn = connect(self.ex + self.name)
            c = conn.cursor()
            c.execute('CREATE TABLE pos (key INTEGER PRIMARY KEY AUTOINCREMENT, x INTEGER, y INTEGER )')
            c.execute('CREATE TABLE pad (x INTEGER, y INTEGER, data BLOB )')
            c.execute('CREATE TABLE players (x INTEGER, y INTEGER, name TEXT, inv INTEGER, hotbar INTEGER, id INTEGER PRIMARY KEY AUTOINCREMENT)')
            c.execute('CREATE TABLE entity (pos INTEGER, type )')
            c.execute('CREATE TABLE holds (id INTEGER PRIMARY KEY AUTOINCREMENT, data BLOB)')
            # c.execute('CREATE TABLE globaldata (stuff)')
            c.execute('INSERT INTO players VALUES (?,?,?,?,?,?)', (0, 0, 'person1', bytearray(32), bytearray(32), 1,))
            conn.commit()
            conn.close()

        self.seed = '123456789'
        self.conn = connect(self.ex + self.name, check_same_thread = False)
        self.c = self.conn.cursor()
        # self.c.execute('CREATE TABLE holds (data BLOB, id INTERGER )')
        self.items = {}
        #self.items[1] = bytearray(220)
        self.pads = {}
        self.players = []
        self.entitys = []
        self.pos = (0, 0)
        with self.conn:
            self.c.execute('SELECT * FROM players')
            temp = self.c.fetchone()
            if not temp:
                temp = [0, 0, 'person1', bytearray(32), 1, ]
                self.c.execute('INSERT INTO players VALUES (?,?,?,?,?)', (0, 0, 'person1', bytearray(32), 1,))
            self.player = Player(temp)

            self.c.execute('SELECT data FROM holds WHERE id = ?', (1,))
            temp = self.c.fetchone()
            if not temp:
                temp = bytearray(220)
                self.c.execute('INSERT INTO holds VALUES (?,?)', (1, temp, ))
            #self.items[1] = bytearray(temp[0])
        self.block_get((0, 0))  # lode in to file

    def show(self):  # for debugging, do not use with big worlds
        pass
        #showfile(self.ex + self.name)

    def block_set(self, xy, data):
        p = (int(xy[0] // 32), int(xy[1] // 32))
        a = ((int(xy[0]) % 32) + (int(xy[1]) % 32) * 32)
        self.pads[p][a] = data

    def block_get(self, xy): # del usless code
        p = (xy[0] // 32, xy[1] // 32)
        if p not in self.pads:
            self.c.execute('SELECT data FROM pad WHERE x=? and y=?', (p[0], p[1],))
            data = self.c.fetchone()
            if not data:
                with self.conn:
                    self.c.execute('INSERT INTO pad VALUES (?,?,?)', (p[0], p[1], DEFULTBLOCK,))
                    data = bytearray(DEFULTBLOCK)
            else:
                data = bytearray(data[0])
            self.pads[p] = data

        return self.pads[p][((xy[0] & 31) + ((xy[1] & 31) * 32))]

    def load_pad(self, p):
        if p not in self.pads:
            self.c.execute('SELECT data FROM pad WHERE x=? and y=?', (p[0], p[1],))
            data = self.c.fetchone()
            if not data:
                with self.conn:
                    self.c.execute('INSERT INTO pad VALUES (?,?,?)', (p[0], p[1], DEFULTBLOCK,))
                    data = bytearray(DEFULTBLOCK)
            else:
                data = bytearray(data[0])
            self.pads[p] = data
            return data
        return self.pads[p]

    def items_load(self, id, size):
        if id in self.items.keys():
            return False
        self.c.execute('SELECT data FROM holds WHERE id = ?', (id,))
        temp = self.c.fetchone()[0]
        if not temp:
            temp = bytearray(size*2)
            self.c.execute('INSERT INTO holds VALUES (?,?)', (temp, id,))
            self.items[id] = temp
            return True
        self.items[id] = bytearray(temp)
        return False

    def save(self):
        with self.conn:
            self.c.executemany('UPDATE pad SET data = (?) WHERE x=(?) AND y=(?)',
                               [(self.pads[i], i[0], i[1],) for i in self.pads])
            p = self.player
            self.c.execute('UPDATE players SET x=(?), y=(?), inv=(?) WHERE id=(?)', (p.pos.x, p.pos.y, p.inv, p.id))
            for i in self.items.keys():

                self.c.execute('UPDATE holds SET data = ? WHERE id = ?', (self.items[i], i,))

        print('saved as ' + self.name)

    def newplayer(self, name):
        self.c.execute('SELECT * FROM players WHERE name=(?)', name)
        temp = self.c.fetchone()
        if not temp:
            temp = [0, 0, 'person1', bytearray(200), 1]
            self.c.execute('INSERT INTO players VALUES (?,?,?,?,?)', (0, 0, name, bytearray(32), 1,))
        self.player = Player(temp)

        self.c.execute('SELECT data FROM holds WHERE id = ?', (1,))
        temp = self.c.fetchone()
        if not temp:
            temp = bytearray(220)
            self.c.execute('INSERT INTO holds VALUES (?,?)', (temp, 1,))

        return 1 # add funk
        # self.items[1] = bytearray(temp[0])

    def pp(self):
        pass

class Player:
    def __init__(self, data):
        self.pos = Vector2(data[0], data[1])
        self.v = Vector2(0, 0)
        print(data)
        self.id = data[4]
        self.name = data[2]
        self.inv = bytearray(data[3])  # bytearray(32)# 16 ids with 255 stack
        self.cash = 100
        self.update = True

    def item(self, index):
        if self.inv[index * 2]:
            return self.inv[(index * 2) + 1]
        return 0

    def count(self, index):
        return self.inv[index * 2]

    def set(self, index, id, n):
        self.inv[index * 2] = n
        self.inv[(index * 2) + 1] = id

    def use(self, index):
        if self.inv[(index * 2) + 1] <= 0:
            self.inv[(index * 2) + 1] -= 1
        else:
            self.inv[index * 2] = 0

    def append(self, id, n):
        for i in range(len(self.inv)):
            if id == self.inv[i * 2]:
                if n + self.inv[(i * 2) + 1] <= 255:
                    return
                else:
                    return
    def newplayer(self):
        self.set(0, 255, 255)
        self.set(1, 1, 255)
        # self.data.player.set(2,2,2)
        self.set(3, 3, 255)
        self.set(4, 6, 255)
        self.set(5, 7, 255)
        self.set(6, 254, 254)
        self.set(7, 100, 200)
        self.set(8, 117, 200)

class datafiles:
    def __init__(self, debug=False):
        self.path = 'resorces/'

        if debug:
            self.blocks = Texture(self.path + 'BLOCKS.PNG')
        else:
            self.blocks = Texture(self.path + 'IMG_4287.PNG')

        self.block = []

        for x in range(16):
            for y in range(16):
                self.block.append(
                    self.blocks.subtexture(((y / 16), 1 - ((x + 1) / 16), 1 / 16, 1 / 16)))
                self.block[-1].filtering_mode = 1

    def get_values(self, name):
        my_list = []
        with open(self.path + name, 'r') as f:
            for i in f.readlines():
                my_list.append(float(i))
        return my_list

    def get(self, file):
        with open(self.path + file, 'r') as data:
            return data.read()


if __name__ == '__main__':
    import os

    # input('sup')
    t = 'test62.db'
    '''
    if not os.path.exists('saves/'+t):
        conn = connect('saves/'+t)
        c = conn.cursor()
        c.execute('CREATE TABLE pos (key INTEGER PRIMARY KEY AUTOINCREMENT, x INTEGER, y INTEGER )')
        c.execute('CREATE TABLE pad (x INTEGER, y INTEGER, data BLOB )')
        c.execute('CREATE TABLE players (x INTEGER, y INTEGER, name TEXT, inv BLOB , id INTEGER PRIMARY KEY AUTOINCREMENT)')
        c.execute('CREATE TABLE entity (pos INTEGER, type )')
        #c.execute('CREATE TABLE globaldata (stuff)')
        conn.commit()
        conn.close()
        print('made new world')
    '''
    w = worldfile(t)
    #w.show()
    w.c.execute('SELECT data FROM pad WHERE x=? and y=?', (0, 0,))
    data = w.c.fetchone()
    print(data)
    print('world object at var "w" and file ', w.name)
