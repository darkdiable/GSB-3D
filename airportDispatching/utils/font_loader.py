import os
from panda3d.core import *


CHINESE_FONT_PATHS = [
    "/System/Library/Fonts/STHeiti Medium.ttc",
    "/System/Library/Fonts/Hiragino Sans GB.ttc",
    "/System/Library/Fonts/AppleSDGothicNeo.ttc",
    "/System/Library/Fonts/PingFang.ttc",
    "/Library/Fonts/Arial Unicode.ttf",
    "/Library/Fonts/Songti.ttc",
]


def load_chinese_font(loader, size=12):
    font = None
    for font_path in CHINESE_FONT_PATHS:
        if os.path.exists(font_path):
            try:
                font = loader.loadFont(font_path, okMissing=True)
                if font:
                    font.setPixelsPerUnit(size)
                    font.setPageSize(512, 512)
                    return font
            except:
                continue
    return None


def get_font(loader, size=12):
    font = load_chinese_font(loader, size)
    return font
