#!/usr/bin/env python
# -*- coding: utf-8 -*-

import click
import os
import subprocess
from exifread import process_file
from random import randint
from re import compile, search, IGNORECASE
from shutil import copy2
from shlex import quote
from sys import exit


def get_exiftool_creation_datetime(media_path):
    possible_tags = ["CreationDate", "DateTimeOriginal"]
    try:
        for tag in possible_tags:
            proc = subprocess.Popen("exiftool -S -t -{t} {mp}".format(mp=media_path, t=tag),
                                    stdin=subprocess.PIPE,
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE,
                                    shell=True)
            out, err = proc.communicate()
            if out:
                break
        if proc.returncode != 0:
            exit("fatal: {e}".format(e=err))
    except OSError as e:
        exit("fatal exception: {e}".format(e=e.strerror))
    return out.decode("utf-8").strip().split("+")[0].split("-")[0].replace(":", "").replace(" ", "_")


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

    ext_p = compile("\.jpg$|\.jpeg$|\.mov$|\.avi$", IGNORECASE)
    jpg_p = compile("\.jpg$|\.jpeg$", IGNORECASE)
    avi_p = compile("\.avi$", IGNORECASE)
    # mov_p = compile("\.mov$", IGNORECASE)

    for root, dirs, files in os.walk(src):
        for src_fn in files:
            if ext_p.search(src_fn) and not src_fn.startswith("."):
                # Reset this variable on each iteration so that
                # subsequent os.path.join()s operate as intended
                dst = os.path.normpath(destination)
                src_path = os.path.join(root, src_fn)
                if jpg_p.search(src_fn):
                    with open(src_path, "rb") as f:
                        ext = "JPG"
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
                else:
                    ext = "AVI" if avi_p.search(src_fn) else "MOV"
                    ctime = get_exiftool_creation_datetime(quote(src_path))
                    subsecond = False
                if ctime:
                    dst_fn = "{ct}.{ss}-{x}.{e}".format(
                        ct=ctime,
                        ss=subsecond if subsecond else randint(100, 999),
                        x=randint(100, 999),
                        e=ext)
                    if yearly:
                        dst = os.path.normpath(os.path.join(dst, ctime[:4]))
                    elif monthly:
                        dst = os.path.normpath(os.path.join(dst, ctime[:4], months[ctime[4:6]]))
                    if not os.path.isdir(dst):
                        os.makedirs(dst)
                    dst_path = os.path.normpath(os.path.join(dst, dst_fn))
                else:
                    unknown_dst = os.path.normpath(os.path.join(dst, "unknown"))
                    print("can't find relevant metadata for {sp}, moving to {ud}".format(
                        sp=src_path, ud=unknown_dst))
                    if not os.path.exists(unknown_dst):
                        os.makedirs(unknown_dst)
                    dst_path = os.path.normpath(
                        os.path.join(unknown_dst, src_fn))
                if not os.path.exists(dst_path):
                    copy2(src_path, dst_path)
                else:
                    exit("fatal: somehow, {dp} already exists; source is {sp}".format(
                        dp=dst_path, sp=src_path))


if __name__ == "__main__":
    main()
