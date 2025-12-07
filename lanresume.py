#!/usr/bin/env python3
"""
lanresume.py

Command-line tool to summarize network interfaces using winpy.lanman.
Supports filtering by --wifi, --ethernet, --virtual-box
"""

import argparse
import sys
import os.path
sys.path.append(os.path.dirname(__file__))
import winpy.lanman

def main(argv=None):
    """Main entry point."""
    code, _, _ = script(sys.argv[1:])
    return code

def script(argv):
    args = parse_args(argv)
    interfaces = winpy.lanman.get_interfaces()
    filtered = filter_interfaces(interfaces, args)
    #for name, info in filtered.items(): print(f"{name}: {info}")
    list_them(filtered)
    return 0, interfaces, filtered

def list_them(ifs, sep=None):
    line_sep = "---\n" if sep is None else "\n"
    for name in sorted(ifs):
        here = ifs[name]
        print(f"{name} ({len(here)})", end=(":\n" if here else "\n"))
        for key in sorted(here):
            item = here[key]
            print(" " * 3, key, item, end="\n\n")
        print(end=line_sep)

def parse_args(argv):
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Summarize network interfaces (Wi-Fi, Ethernet, VirtualBox)."
    )
    parser.add_argument(
        "--wifi",
        action="store_true",
        help="Show only Wi-Fi interfaces"
    )
    parser.add_argument(
        "--ethernet",
        action="store_true",
        help="Show only Ethernet interfaces"
    )
    parser.add_argument(
        "--virtual-box",
        action="store_true",
        help="Show only VirtualBox interfaces"
    )
    return parser.parse_args(argv)


def filter_interfaces(interfaces, args):
    """Filter interfaces based on command-line options."""
    result = {}
    for name, info in interfaces.items():
        desc = info.get("caption", "") or info.get("description", "") or name
        if args.wifi and "Wi-Fi" in desc:
            result[name] = info
        elif args.ethernet and "Ethernet" in desc:
            result[name] = info
        elif args.virtual_box and "VirtualBox" in desc:
            result[name] = info
        elif not (args.wifi or args.ethernet or args.virtual_box):
            # No filter specified → include all
            result[name] = info
    return result

if __name__ == "__main__":
    main()
