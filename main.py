#!/bin/env python3
import argparse
import logging
from pathlib import Path
import select
import sys
import termios
import tty
from z80 import Z80Machine, JP
from disk import DiskFile
from z80nx import Z80nx

def main():
    logging.basicConfig(level=logging.DEBUG,
                        handlers=[logging.FileHandler("emulator.log")])
    z80nx = Z80nx()
    z80nx.disks[0] = DiskFile(z80nx, "disk_a.img")
    print(z80nx)
    z80nx.run()    




if __name__ == "__main__":
    main()