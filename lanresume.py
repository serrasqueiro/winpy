#!/usr/bin/env python3
"""
lanresume.py

Command-line tool to summarize network interfaces using winpy.lanman.
Supports filtering by --wifi, --ethernet, --virtual-box
"""

import argparse
import sys
#import os.path
#sys.path.append(os.path.dirname(__file__))
import winpy.lanman

def main(argv=None):
    """Main entry point."""
    code, _, _ = script(sys.argv[1:])
    return code


def script(argv):
    args = parse_args(argv)
    interfaces = winpy.lanman.get_interfaces()
    alle = []
    for kind in sorted(interfaces):
        what_to = interfaces[kind]
        filtered = filter_interfaces(what_to, args, kind)
        if filtered:
            alle.append((kind, filtered))
    list_seq(alle)
    return 0, interfaces, alle


def parse_args(argv):
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Summarize network interfaces (Wi-Fi, Ethernet, VirtualBox)."
    )
    parser.add_argument(
        "--wifi",
        action="store_true",
        help="Show only Wi-Fi interfaces",
    )
    parser.add_argument(
        "--ethernet", "--eth",
        action="store_true",
        help="Show only Ethernet interfaces",
    )
    parser.add_argument(
        "--virtual-box",
        action="store_true",
        help="Show only VirtualBox interfaces",
    )
    parser.add_argument("interfaces", nargs="*", help="Optional interface names")
    return parser.parse_args(argv)


def list_seq(all_ifs, sep=None):
    line_sep = "---\n" if sep is None else "\n"
    for tup in all_ifs:
        kind, ifc = tup
        print(f"{kind} ({len(ifc)})", end=(":\n" if ifc else "\n"))
        list_them(ifc, pre=" " * 4)
        print(end=line_sep)


def list_them(ifc, pre=""):
    for key in sorted(ifc):
        item = ifc[key]
        print(pre + key, item, end="\n\n")


def filter_interfaces(interfaces, args, kind=""):
    """ Filter interfaces based on command-line options. """
    result = {}
    got_it = []
    if not kind:
        kind = "own"
    for name, info in interfaces.items():
        desc = info.get("caption", "") or info.get("description", "") or name
        simple = simplest(desc)
        store, bare = {}, False
        if not simple:
            continue
        assert isinstance(info, dict), f"Wow: {info}"
        if args.wifi and "Wi-Fi" in desc:
            store = info
        elif args.ethernet and "Ethernet" in desc:
            store = info
        elif args.virtual_box and kind in ("virtual",):
            store = info
        elif not any([args.wifi, args.ethernet, args.virtual_box]):
            # No filter specified: include all, from specific interface
            store = info
            bare = True
        if args.interfaces:
            later = [aba for aba in args.interfaces if simple.startswith(simplest(aba))]
            perfect = len(later) == 1  and simple == simplest(args.interfaces[0])
            if not later:
                continue
            if perfect:
                got_it = [(9, name, info)]
            elif not got_it or got_it[0][0] < 9:
                got_it.append((1, name, info))
            continue
        if store:
            result[name] = store
    if not got_it:
        return result
    # Check if there was a perfect match, only return that one, or otherwise return all substrings:
    for tup in got_it:
        name, info = tup[1:]
        result[name] = info
        if got_it[0][0] == 9:
            break
    return result


def simplest(astr):
    res = astr.lower().replace(" ", "")
    for ignored in "*-":
        res = res.replace(ignored, "")
    return res


if __name__ == "__main__":
    main()
