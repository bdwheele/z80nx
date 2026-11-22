import os
from .system import System

class Disk:
    def __init__(self, system: System, params: dict):
        self.system = system

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

    def get_lbn_from_dts(self):
        "Return the LBN from the BIOS disk parameter table"
        dpb_addr = self.system.mem_read_word(self.system.dpbase + self.system.disk * 16 + 10)
        track_len = self.system.mem_read_word(dpb_addr)
        lbn = track_len * self.system.track + self.system.sector
        return lbn


class DiskNone(Disk):
    def read(self):
        return 1

    def write(self):
        return 1

    def home(self):
        return 0xff


class DiskDevice(Disk):
    pass

class DiskHardware(Disk):
    pass


class DiskFile(Disk):
    def __init__(self, system: System, config: dict):
        self.system = system
        self.filename = config['file']
        self.fd = open(config['file'], "r+b")
        #print(f'Opening disk file {config["file"]} for fd {self.fd}')
    
    def read(self):
        offset = self.get_lbn_from_dts() * 128
        #print(f"Reading {self.filename}@{offset}, {self.system.disk}")
        self.fd.seek(offset, os.SEEK_SET)
        self.system.m.set_memory_block(self.system.dma, self.fd.read(128))
        return 0

    def write(self):
        # 0=ok 1=physical, 2=r/o, 0xff=media change
        sec = bytearray()
        for i in range(128):
            sec.append(self.system.m.memory[self.system.dma + i])
        offset = self.get_lbn_from_dts() * 128
        #print(f"Writing {self.filename}@{offset}, {self.system.disk}")
        self.fd.seek(offset, os.SEEK_SET)
        self.fd.write(sec)
        self.fd.flush()
        return 0

