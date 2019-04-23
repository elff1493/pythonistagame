from socket import *
from _thread import *
from threading import Thread
import struct
from struct import pack, unpack
#from filedata import worldfile
#DEFULTBLOCK = bytearray([4 for i in range(32 * 32)])

#for i in range(32):
 #   DEFULTBLOCK[i] = 201
  #  DEFULTBLOCK[i] = 200
   # DEFULTBLOCK[i*32] = 200
    #DEFULTBLOCK[(i*32)-1] = 200

class Vector2:
    def __init__(self, x, y):
        self.x = x
        self.y = y

from filedata import worldfile

def ro(i):
    if i < 0:
        return int(i - 1)
    return int(i)

class server:
    def __init__(self, max_players=2, name="undergrouwnd.db"):
        self.file = worldfile(name=name)
        self.output = True
        self.players = []
        self.events = []  # (from, data)
        self.joinloopthread = None
        self.mainloopthread = None
        self.run = True

        #  socket stuff
        self.max_players = max_players
        self.socket = socket(AF_INET, SOCK_STREAM)
        self.socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        self.address = ("", 5555)


        with socket(AF_INET, SOCK_DGRAM) as s:
            s.connect(('google.com', 80))
            self.ip = s.getsockname()[0]
            self.address = (self.ip, 5555)

        self.print("ip is: ", self.ip)

        try:
            self.socket.bind(self.address)

        except error as e:
            self.print(str(e), p=3)

        self.socket.listen(self.max_players)

        self.struct = [(0, "=h", self.player_join),
                       (8, "=ii", self.player_move),
                       (1024, "=1024B", self.player_inv),
                       (9, "=iiB", self.player_use_item)]

    def print(self, *args, p=0, **kargs):
        """
        custom print
        p=1: sever        vilot
        p=2: player event blue2
        p=3: error        red
        p=4:

        :param args:
        :param kargs:
        :return:
        """
        if not self.output:
            return

        out = "".join([str(i) for i in args]) + '\33[0m'
        if p ==0:
            print(out, **kargs)
        elif p == 1:
            print('\33[35m' + out, **kargs)
        elif p == 2:
            print('\33[34m' + out, **kargs)
        elif p == 3:
            print('\33[31m' + out, **kargs)

    def mainloop(self):
        self.mainloopthread = Thread(target=self._mainloop())
        self.mainloopthread.start()

    def _mainloop(self):
        while self.run:
            if len(self.events):
                player, data, id = self.events.pop()
                self.struct[id][2](player, unpack(self.struct[id][1], data))

    def _join_loop(self):
        while self.run:
            conn, addr = self.socket.accept()
            self.print("Connected to: ", addr, p=1)

            new = ClientThread(conn, self.file, self)
            self.players.append(new)
            #new.loop()

            #start_new_thread(new.loop, ())

    def join_loop(self):
        self.joinloopthread = Thread(target=self._join_loop)
        self.joinloopthread.start()

    def player_move(self, player, args):  # make a bettter loding
        #self.print(player.id, ": moved to ", args, p=2)
        #x, y = unpack("=ii", data)  # get pos

        x, y = args
        pos = (x, y)
        xy = (ro(x) / 32, ro(y) / 32)
        pad = (-(xy[0] - 16) // 32, -(xy[1] - 16) // 32)

        if pad != player.pad:
            player.pad = pad
            for i in range(-2, 2):
                for j in range(-2, 2):
                    self.send_pads(player, pad[0] + i, pad[1] + j)
                    #if (pad[0] + i, pad[1] + j) not in player.loaded_pads:
                        # self.sent.add((self.xy[0] + i, self.xy[1] + j))

    def send_pads(self, player, x, y, overide=False):

        if ((x, y) not in player.loaded_pads) or overide:
            self.print(player.id, ": pad at ", (x, y))
            player.loaded_pads.add((x, y))
            if (x, y) in self.file.pads:
                pad = self.file.pads[(x, y)]
            else:
                pad = self.file.load_pad((int(x), int(y)))
                self.file.pads[(x, y)] = pad

            player.conn.send(pack("=Bii1024B", 3, int(x), int(y), *pad))

    def player_join(self):
        pass

    def player_inv(self):
        pass

    def player_use_item(self, player, args):
        x, y, b = args
        self.print(player.id, ": used ", b, " at ", (x, y))
        self.file.block_set((x, y), b)
        for i in self.players:
            #d = (i.pos[0] - player.pos[0])**2 + (i.pos[1] - player.pos[1])**2
            #if (x//32, y//32) in i.loaded_pads:
             #   i.loaded_pads.remove((x//32, y//32))
            if abs(i.xy[0] - x) < 64 and abs(i.xy[1] - y) < 64:
                self.send_pads(i, x//32, y//32, overide=True)

        # test for close players


# client
class ClientThread:
    ID = 0
    def __init__(self, conn, file, server):
        self.server = server
        self.file = file
        self.conn = conn
        self.name = ""
        self.auth = 0
        self.id = ClientThread.ID
        ClientThread.ID += 1
        #self.parser = Parser(self)
        self.pos = (0, 0)
        self.xy = (0, 0)
        self.pad = (0, 0)
        self.loaded_pads = set()

        self.run = True
        self.thread = Thread(target=self.loop)
        self.thread.start()

    def loop(self):
        for i in [-1, 0, 1]:
            for j in [-1, 0, 1]:
                self.conn.send(pack("=bii1024B", 3, i, j, *self.file.load_pad((i, j))))

        sizes = [0, 8, 0, 9]
        data = bytes()
        while self.run:
            try:
                data = data + self.conn.recv(1024) # get update
            except ConnectionResetError:
                self.server.print(self.id, ": ConnectionResetError")
                self.quit()
            if data:
                while data:
                    num = data[0]
                    if num in [1, 3]:
                        if sizes[num]+1 <= len(data):  # need more data?
                            data = data[1:]
                            self.server.events.insert(0, (self, data[:sizes[num]], num))
                            data = data[sizes[num]:]
                    else:
                        self.server.print("event id not valid ", num, p=3)
                        self.quit() # kick you and your evil packets >:(
                        return

            else:
                self.server.print("quit conn for", self.id, p=1)
                self.quit()
                return
        self.quit()


    def quit(self):
        self.run = False
        self.conn.close()
        self.server.players.remove(self)
        self.server.print(self.id, ": left the sever", p=2)

from tkinter import Tk, Button, Menu

class controler:
    def __init__(self, server):
        self.server = server
        self.root = Tk()
        #self.butt = Button(self.root, text="save", command=self.save)
        #self.butt.pack()
        self.menubar = Menu(self.root)
        self.filemenu = Menu(self.menubar, tearoff=0)
        self.filemenu.add_command(label="Open", command=self.open)
        self.filemenu.add_command(label="Save", command=self.save)
        self.filemenu.add_separator()
        self.filemenu.add_command(label="Exit", command=self.quit)
        self.menubar.add_cascade(label="File", menu=self.filemenu)
        # display the menu
        self.root.config(menu=self.menubar)

    def print(self, *arg, r=0, **kargs):
        print(*arg, r, **kargs)

    def open(self):
        print("open not working  yet")

    def quit(self):
        self.save()
        self.server.run = False
        for i in self.server.players:
            i.quit()
        self.root.quit()

    def save(self):
        print("save")
        self.server.file.save()

if __name__ == "__main__":
    s = server()
    s.join_loop()
    s.mainloop()
    #Thread(target=s.mainloop).start()
    controler(s).root.mainloop()
    #s.mainloop()

"""
0: command: chars
1: set new player: name(char), skin(byte)
2: update player;   pos x y (dubble dublle) speed x, y (short) #
3: use item: id, x, y                                          #
4: invinory set
5: entiy: id, x, y, xv, yv, ani skin| H, int, int, H, H, H











"""














