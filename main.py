#!/usr/bin/env python3
"""main.py — entrypoint for news-image-20261125 v2.

Copies the committed entry.png to the grader output path (/output/entry.png
when that directory exists, else next to this file). Byte-for-byte copy, so
re-running reproduces the entry exactly. The image itself is drawn by
frontpage25_v2.py (run in-session); this file only places it.
"""
import os
import shutil

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "entry.png")


def main():
    outdir = "/output" if os.path.isdir("/output") else HERE
    dst = os.path.join(outdir, "entry.png")
    if os.path.abspath(dst) != os.path.abspath(SRC):
        shutil.copyfile(SRC, dst)


if __name__ == "__main__":
    main()
