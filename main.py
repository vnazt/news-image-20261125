#!/usr/bin/env python3
"""Copy entry.png into the grader output directory.

The output directory comes from MAKEFUN_OUTPUT_DIR and falls back to
/output when the variable is not set. Only entry.png is copied, and
only when it sits next to this file.
"""
import os
import shutil

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "entry.png")


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    dst = os.path.join(out_dir, "entry.png")
    shutil.copyfile(SRC, dst)
    print("copied entry.png ->", dst)


if __name__ == "__main__":
    main()
