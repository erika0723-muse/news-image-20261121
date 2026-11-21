#!/usr/bin/env python3
"""Entry program for make.fun: 'Sum up 20 November's world news in one image'.

Copies the pre-rendered front-page image (assets/entry.png) to
/output/entry.png. Standard library only, no network access, and fully
deterministic: the output bytes are exactly the asset bytes on every run.

The image itself was drawn by render.py (see README.md).
"""

import os
import shutil

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "assets", "entry.png")
DST_DIR = "/output"
DST = os.path.join(DST_DIR, "entry.png")


def main():
    os.makedirs(DST_DIR, exist_ok=True)
    shutil.copyfile(SRC, DST)


if __name__ == "__main__":
    main()
