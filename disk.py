


import os

from z80nx import Z80nx


class Disk:
    def __init__(self, z80nx):
        pass

    def reset(self):
        "Reset the disk"
        pass

    def motor(self, state: bool):
        pass


    def read(self):
        pass

    def write(self):
        pass

    def home(self):
        pass


class DiskFile(Disk):
    def __init__(self, z80nx: Z80nx, filename):
        self.z80nx = z80nx
        self.fd = open(filename, "r+b")
        # we can look up the disk parameter table and
        # figure out our disk parameters here.



    def read(self):
        track = self.z80nx.track
        sector = self.z80nx.sector
        offset = track * (512 * 18) + 128 * sector
        self.fd.seek(offset, os.SEEK_SET)
        self.z80nx.m.set_memory_block(self.z80nx.dma, self.fd.read(128))

    def write(self):
        pass

