import logging
from pathlib import Path
import select
import sys
import termios
import tty

from z80 import Z80Machine




class Z80nx:
    def __init__(self):
        self.m = Z80Machine()
        self.m.set_input_callback(lambda port: self.handle_input(port))
        self.m.set_output_callback(lambda port, value: self.handle_output(port, value))
        self.load_rom("system.rom")
        self.memory_reset()
        self.disk = 0
        self.track = 0
        self.sector = 1
        self.dma = 0

        # test scaffold
        self.original_terminal = termios.tcgetattr(sys.stdin.fileno())
        tty.setraw(sys.stdin.fileno())

        self.disks = [None, None, None]
        



    def run(self):
        logging.debug("Starting emulation")
        while not self.m.halted:
            self.m.run()
        logging.debug(f"Ended emulation: {self.m.pc:04x}, {self.m.pc}")

    def handle_input(self, port: int) -> int:
        logging.debug(f"Reading port {port}")
        pass

    def handle_output(self, port: int, value: int):
        logging.debug(f"Writing port {port & 0xff} with value {value}")
        svc_names = ["cold boot", "warm boot", "console status", "console input",
                     "console_output", "list output", "punch output", "reader in",
                     "home disk", "select disk", "set track", "set sector", "set dma",
                     "read block", "write block", "list status", "sector translate"]
        port &= 0xff
        if port > len(svc_names) - 1:
            service = "unknown"
        else:
            service = svc_names[port]
        logging.debug(f"Port write {port:02x} ({service}), value {value:02x}.  PC={self.m.pc:04x}, AF={self.m.af:04x}, BC={self.m.bc:04x}, DE={self.m.de:04x}, SP={self.m.sp:04x}, HL={self.m.hl:04x}")
        match port:
            case 1:
                # warm boot
                self.memory_reset()
                # self.disk_reset()
            case 2:
                # console status, 0xff is something is waiting
                s = select.select([sys.stdin.fileno()], [], [], 0)
                if not len(s[0]):
                    self.m.a = 0
                else:
                    self.m.a = 0xff
            case 3:
                # console read
                x = sys.stdin.read(1)
                self.m.a = ord(x)
                if self.m.a == 0x03:
                    print("CTRL-C")
                    termios.tcsetattr(sys.stdin.fileno(), termios.TCSANOW, self.original_terminal)
                    #tty.setraw(sys.stdin.fileno(), )
                    #return
                    self.m.halted = True
            case 4:
                # console write
                sys.stdout.write(chr(self.m.c))
                sys.stdout.flush()
            case 5:
                # list out
                pass
            case 6:
                # punch out
                pass
            case 7:
                # reader in
                pass
            case 8:
                # home disk
                self.disks[self.disk].home()
                self.track = 0
            case 9:
                # select disk
                dsk = self.m.c
                if dsk < 0 or dsk > len(self.disks) -1 or self.disks[dsk] is None:
                    self.m.hl = 0
                else:
                    self.drive = dsk
                    # TODO: if bit zero of E is 0 then it's a new disk, otherwise it's been seen before...
                    self.m.hl = self.dpbase + dsk * 16
            case 10:
                # set track
                self.track = self.m.bc
            case 11:
                # set sector
                self.sector = self.m.bc
            case 12:
                # set dma
                self.dma = self.m.bc
            case 13:
                # read block
                self.disks[self.disk].read()
                pass
            case 14:
                # write block
                self.disks[self.disk].write()
                pass
            case 15:
                # list status
                pass
            case 16:
                # translate sector
                # we translate 1:1
                self.m.hl = self.m.bc
            case _:
                logging.debug(f"Unknown port {port:02x} write")

    def load_rom(self, filename: str):
        self.rom = Path(filename).read_bytes()
        def leword(data: bytes, addr: int) -> int:
            return data[addr] + 256 * data[addr + 1]

        sig = leword(self.rom, len(self.rom) - 2)
        logging.debug(f"Signature: {sig:x}")
    
        self.dpbase = leword(self.rom, len(self.rom) - 4)
        self.bbase = leword(self.rom, len(self.rom) - 6)
        self.fbase = leword(self.rom, len(self.rom) - 8)
        self.cbase = leword(self.rom, len(self.rom) - 10)

        logging.debug(f"Bases loaded: dpbase: {self.dpbase:x}, bbase: {self.bbase:x}, fbase: {self.fbase:x}, cbase: {self.cbase:x}")

    def mem_read_byte(self, addr: int) -> int:
        return self.m.memory[addr]

    def mem_read_word(self, addr: int) -> int:
        return self.m.memory[addr] + 256 * self.m.memory[addr + 1]

    def mem_write_byte(self, addr: int, value: int):
        self.m.memory[addr] = value

    def mem_write_word(self, addr: int, value: int):
        self.m.memory[addr] = value & 0xff
        self.m.memory[addr + 1] = (value >> 8) & 0xff

    def memory_reset(self):
        # reload rom
        self.m.set_memory_block(self.cbase, self.rom)
        self.mem_write_byte(0, 0xc3)
        self.mem_write_word(1, self.bbase)
        self.mem_write_byte(5, 0xc3)
        self.mem_write_word(6, self.fbase)
        