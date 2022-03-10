#!/usr/bin/env python
# -*- coding: utf-8 -*-


import random
import re
import shlex
import shutil
import sys
import subprocess
import os
import click
import exifread


def get_exiftool_creation_datetime(media_path):
    '''does what the function name says'''
    possible_tags = ["CreationDate", "DateTimeOriginal", "ProfileDateTime"]
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
            sys.exit("fatal: {e}".format(e=err))
    except OSError as error:
        sys.exit("fatal exception: {e}".format(e=error.strerror))
    return out.decode("utf-8").strip().split("+", maxsplit=1)[0].split("-")[0].replace(":", "").replace(" ", "_")


@click.command()
@click.option("-s", "--source", help="Source path", required=True)
@click.option("-d", "--destination", help="Destination path", required=True)
@click.option("-y", "--yearly", help="Organize into yearly subfolders", is_flag=True)
@click.option("-m", "--monthly", help="Organize into monthly subfolders (implies yearly)", is_flag=True)
@click.option("-x", "--delete", help="Delete original files as they are moved (destructtive)", is_flag=True)
def main(source, destination, yearly, monthly, delete):
    '''dis mane'''
    src = os.path.normpath(source)
    dst = os.path.normpath(destination)
    if not (os.path.isdir(src) and os.path.isdir(dst)):
        sys.exit("fatal: ensure both source and destination directories exist")

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

    ext_p = re.compile(r"\.jpg$|\.jpeg$|\.heic$|\.png$|\.mov$|\.mp4$|\.avi$|\.cr2$|\.nef$|\.dng$", re.IGNORECASE)
    jpg_p = re.compile(r"\.jpg$|\.jpeg$", re.IGNORECASE)
    png_p = re.compile(r"\.png$", re.IGNORECASE)
    raw_p = re.compile(r"\.cr2$|\.nef$|\.dng$", re.IGNORECASE)
    hei_p = re.compile(r"\.heic$", re.IGNORECASE)
    avi_p = re.compile(r"\.avi$", re.IGNORECASE)
    # mov_p = re.compile("\.mov$", re.IGNORECASE)

    for root, dirs, files in os.walk(src):
        for src_fn in files:
            if ext_p.search(src_fn) and not src_fn.startswith("."):
                # Reset this variable on each iteration so that
                # subsequent os.path.join()s operate as intended
                dst = os.path.normpath(destination)
                src_path = os.path.join(root, src_fn)
                if jpg_p.search(src_fn):
                    with open(src_path, "rb") as fyl:
                        ext = "JPG"
                        tags = exifread.process_file(fyl, details=False)
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
                elif raw_p.search(src_fn):
                    with open(src_path, "rb") as fyl:
                        ext = src_fn[-3:].upper()
                        tags = exifread.process_file(fyl, details=False)
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
                elif hei_p.search(src_fn):
                    with open(src_path, "rb") as fyl:
                        ext = "HEIC"
                        tags = exifread.process_file(fyl, details=False)
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
                elif png_p.search(src_fn):
                    ext = "PNG"
                    ctime = get_exiftool_creation_datetime(shlex.quote(src_path))
                    subsecond = False
                else:
                    ext = "AVI" if avi_p.search(src_fn) else "MOV"
                    ctime = get_exiftool_creation_datetime(shlex.quote(src_path))
                    subsecond = False
                if ctime:
                    dst_fn = "{ct}.{ss}-{x}.{e}".format(
                        ct=ctime,
                        ss=subsecond if subsecond else random.randint(100, 999),
                        x=random.randint(100, 999),
                        e=ext)
                    if yearly:
                        dst = os.path.normpath(os.path.join(dst, ctime[:4]))
                    elif monthly:
                        dst = os.path.normpath(os.path.join(dst, ctime[:4], months[ctime[4:6]]))
                    if not os.path.isdir(dst):
                        os.makedirs(dst)
                    dst_path = os.path.normpath(os.path.join(dst, dst_fn))
                else:
                    unknown_dst = os.path.normpath(os.path.join(dst, "datetime_unknown"))
                    print("can't find relevant metadata for {sp}, moving to {ud}".format(
                        sp=src_path, ud=unknown_dst))
                    if not os.path.exists(unknown_dst):
                        os.makedirs(unknown_dst)
                    dst_path = os.path.normpath(
                        os.path.join(unknown_dst, src_fn))
                if not os.path.exists(dst_path):
                    shutil.copy2(src_path, dst_path)
                    if delete:
                        # print("gonna delete {}".format(src_path))
                        os.remove(src_path)
                else:
                    sys.exit("fatal: somehow, {dp} already exists; source is {sp}".format(
                        dp=dst_path, sp=src_path))


if __name__ == "__main__":
    main()
