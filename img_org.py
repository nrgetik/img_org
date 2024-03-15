#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Trivially organizes and renames some media files chronologically
according to creation date/time available in metadata
"""

from os import makedirs, walk
from os.path import exists, isdir, join, normpath, splitext
from random import randint
from shutil import copy
from exiftool import ExifToolHelper
import click

# (Maybe)
SUPPORTED_FILETYPES = \
    ["3gp",
     "avi",
     "cr2",
     "dng",
     "heic",
     "jpeg",
     "jpg",
     "mov",
     "mp4",
     "mpeg",
     "mpeg4",
     "mpg",
     "nef",
     "png"]
# Order matters here
POSSIBLE_TAGS = ["Composite:SubSecDateTimeOriginal", "EXIF:DateTimeOriginal",
                "EXIF:CreateDate", "QuickTime:CreateDate", "XMP:MetadataDate"]
MONTHS = \
    {"01": "01-January","02": "02-February","03": "03-March","04": "04-April",
    "05": "05-May","06": "06-June","07": "07-July","08": "08-August",
    "09": "09-September","10": "10-October","11": "11-November","12": "12-December"}

@click.command()
@click.option("-s", "--source", help="Source path", required=True)
@click.option("-d", "--destination", help="Destination path", required=True)
@click.option("-y", "--yearly", help="Organize into yearly subfolders", is_flag=True)
@click.option("-m", "--monthly",
                help="Organize into monthly subfolders (implies yearly)", is_flag=True)
def main(source, destination, yearly, monthly):
    """This is the main function"""
    src = normpath(source)
    dst = normpath(destination)
    if not (isdir(src) and isdir(dst)):
        raise SystemExit("fatal: one or both source/destination directories do not exist")

    src_file_paths = []
    for root, dirs, files in walk(src):
        for src_fn in files:
            if not src_fn.startswith("."):
                src_path = join(root, src_fn)
                src_ext = splitext(src_path)[1].lower()
                if any(ftype in src_ext for ftype in SUPPORTED_FILETYPES):
                    src_file_paths.append(src_path)

    with ExifToolHelper() as exif_tool:
        all_files_metadata = exif_tool.get_metadata(src_file_paths)

    for metadata in all_files_metadata:
        # Reset this variable on each iteration so that
        # subsequent os.path.join()s operate as intended
        dst = normpath(destination)
        src_fn = metadata["File:FileName"]
        src_path = metadata["SourceFile"]
        src_ext = splitext(src_path)[1].lower()
        dst_ext = src_ext.upper()
        if any(tag in metadata for tag in POSSIBLE_TAGS):
            for search_tag in POSSIBLE_TAGS:
                if search_tag in metadata:
                    tag = search_tag
                    break # we found the most preferable tag, break out!
            c_time = (metadata[tag]
                        .split("+", maxsplit=1)[0]
                        .split("-", maxsplit=1)[0]
                        .replace(":", "")
                        .replace(" ", "_"))
            dst_fn = "{ct}{ss}-{x}{e}".format(
                        ct=c_time,
                        ss="" if "SubSec" in tag else f".{randint(100, 999)}",
                        x=randint(100, 999),
                        e=dst_ext)
            if yearly:
                dst = normpath(join(dst, c_time[:4]))
            elif monthly:
                dst = normpath(join(dst, c_time[:4], MONTHS[c_time[4:6]]))
            if not isdir(dst):
                makedirs(dst)
            dst_path = normpath(join(dst, dst_fn))
        else:
            unknown_dst = normpath(join(dst, "datetime_unknown"))
            print(f"can't find good metadata for {src_path}, moving to {unknown_dst}")
            if not isdir(unknown_dst):
                makedirs(unknown_dst)
            dst_path = normpath(join(unknown_dst, src_fn))
        if not exists(dst_path):
            copy(src_path, dst_path)
        else:
            randy = randint(100, 999)
            print(f"{dst_path} already exists, moving to {dst_path}.{randy}\nsource file is {src_path}")
            copy(src_path, f"{dst_path}.{randy}")

if __name__ == "__main__":
    main()
