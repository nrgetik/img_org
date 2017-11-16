#!/usr/bin/env python
# -*- coding: utf-8 -*-

import click
import os
from exifread import process_file
from random import randint
from re import search, IGNORECASE
from shutil import copy2
from sys import exit


@click.command()
@click.option("-s", "--source", help="Source path", required=True)
@click.option("-d", "--destination", help="Destination path", required=True)
@click.option("-y", "--yearly", help="Organize into yearly subfolders", is_flag=True)
@click.option("-m", "--monthly", help="Organize into monthly subfolders (implies yearly)", is_flag=True)
def main(source, destination, yearly, monthly):
    src = os.path.normpath(source)
    dst = os.path.normpath(destination)
    if not (os.path.isdir(src) and os.path.isdir(dst)):
        exit("fatal: ensure both source and destination directories exist")

    months = {"01": "01-January",
              "02": "02-February",
              "03": "03-March",
              "04": "04-April",
              "05": "05-May",
              "06": "06-June",
              "07": "07-July",
              "08": "08-August",
              "09": "09-September",
              "10": "10-October",
              "11": "11-November",
              "12": "12-December"}

    for root, dirs, files in os.walk(src):
        for src_fn in files:
            if search("\.jpg|\.jpeg", src_fn, IGNORECASE):
                # Reset this variable on each iteration so that
                # subsequent os.path.join()s operate as intended
                dst = os.path.normpath(destination)
                src_path = os.path.join(root, src_fn)
                with open(src_path) as f:
                    tags = process_file(f, details=False)
                    try:
                        ctime = str(tags["EXIF DateTimeOriginal"])\
                            .replace(":", "")\
                            .replace(" ", "_")
                    except KeyError:
                        ctime = False
                    try:
                        subsecond = tags["EXIF SubSecTimeOriginal"]
                    except KeyError:
                        subsecond = False
                if ctime:
                    dst_fn = "{ct}.{ss}-{x}.JPG".format(
                        ct=ctime, ss=subsecond if subsecond else randint(100, 999), x=randint(100, 999))
                    if yearly:
                        dst = os.path.normpath(os.path.join(dst, ctime[:4]))
                    elif monthly:
                        dst = os.path.normpath(os.path.join(dst, ctime[:4], months[ctime[4:6]]))
                    if not os.path.isdir(dst):
                        os.makedirs(dst)
                    dst_path = os.path.normpath(os.path.join(dst, dst_fn))
                else:
                    print("{sfn} problematic; ctime = {ct}, subsecond = {ss}"
                          .format(sfn=src_fn, ct=ctime, ss=subsecond))
                    unknown_dst = os.path.normpath(os.path.join(dst, "unknown"))
                    if not os.path.exists(unknown_dst):
                        os.makedirs(unknown_dst)
                    dst_path = os.path.normpath(
                        os.path.join(unknown_dst, src_fn))
                if not os.path.exists(dst_path):
                    copy2(src_path, dst_path)
                else:
                    exit("fatal: somehow, {dfn} already exists; source is {sfn}".format(
                        dfn=dst_fn, sfn=src_fn))

if __name__ == "__main__":
    main()
