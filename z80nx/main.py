#!/bin/env python3
import argparse
import logging
from pathlib import Path
from .disk import DiskFile, DiskNone
from .system import System
import yaml

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--debug", action="store_true", help="Turn on debugging")
    parser.add_argument("config", type=Path, help="Config file", default="z80nx.conf")
    args = parser.parse_args()

    with open(args.config) as f:
        config = yaml.safe_load(f)

    logfile = config.get('logfile', None)
    if logfile is None:
        log_handler = None
    else:
        log_handler = [logging.FileHandler(logfile)]

    logging.basicConfig(level=logging.DEBUG if args.debug else logging.INFO,
                        handlers=log_handler)
    
    system = System(config.get('romfile', 'system.rom'))
    for i, diskcfg in enumerate(config.get('disks', [])):
        if i > 2:
            logging.error("A maximum of 3 disks can be defined")
            exit(1)
        type = diskcfg['type']
        if type == 'file':
            system.disks[i] = DiskFile(system, diskcfg)
    system.run()    




if __name__ == "__main__":
    main()