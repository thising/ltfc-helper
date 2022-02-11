# -*- coding=utf-8 -*-

import re
import os
from urllib.request import urlretrieve
from operator import itemgetter
from PIL import Image

SCRIPT = "./script.curl"
DEST = "./LTFC/"
INCLUDE = "/18/"

def script_item_info(command):
    parts = command.split(" ")
    for item in parts:
        if item.startswith("'https://") and INCLUDE in item:
            match = re.match( r'(.*)/(.*).jpg.*', item, re.M|re.I)
            if match:
                name = match.group(2)
                number = name.split("_")
                return (int(number[0]), int(number[1]), item[1:-1])
    return (-1, -1, None)

def process_curl_script(path):
    ret = []
    columns = 0
    rows = 0
    with open(path, "r") as f:
        buf = f.read()
        scripts = buf.split(" ;")
        for item in scripts:
            col, row, url = script_item_info(item)
            if col > columns:
                columns = col
            if row > rows:
                rows = row
            if col >= 0:
                name = "%d_%d.jpg" % (col, row)
                ret.append((col, row, url, name))
    return (columns + 1, rows + 1, ret)

def tidy(columns, rows, urls):
    total = columns * rows
    miss = total
    ret = [[(-1, -1, "x", "x") for i in range(rows)] for j in range(columns)]
    for (col, row, url, name) in urls:
        if ret[col][row][0] < 0:
            ret[col][row] = (col, row, url, name)
            miss -= 1
    return (total, miss, ret)

def validate(columns, rows, urls):
    total, miss, last = tidy(columns, rows, urls)
    if miss > 0:
        print("* MISS %3d image urls:" % (miss))
        print("(COL, ROW) -> URL, NAME")
    else:
        print("* Get %3d(%2d * %2d) image urls successfully!" % (total, columns, rows))
    for i in range(columns):
        for j in range(rows):
            url = last[i][j][2]
            name = last[i][j][3]
            if url == "x":
                print("(%2d, %2d) -> %s, \t%s" % (i, j, url, name))
    return ((miss == 0), last)

def urllib_download(url, path):
    urlretrieve(url, path)

def download(images):
    for col in images:
        for row in col:
            url = row[2]
            name = row[3]
            path = os.path.join(DEST, name)
            print("Downloading", url, "->", path)
            urllib_download(url, path)

def contact_images(cols, rows, images):
    image_data_list = []
    width = 0;
    height = 0;
    for i in range(cols):
        col_data = []
        for j in range(rows):
            path = os.path.join(DEST, images[i][j][3])
            # path = os.path.join(DEST, "%d_%d.jpg" % (i, j))
            tmp = Image.open(path)
            data = tmp.copy()
            col_data.append(data)
            tmp.close()
            w, h = data.size
            if j == 0:
                width += w
            if i == 0:
                height += h
        image_data_list.append(col_data)
    print("Image size: %d * %d pixes" % (width, height))
    target = Image.new(image_data_list[0][0].mode, (width, height))
    offset_w = 0
    for i in range(cols):
        offset_h = 0
        tmp = 0
        for j in range(rows):
            data = image_data_list[i][j]
            w, h = data.size
            target.paste(data, (offset_w, offset_h))
            offset_h += h
            tmp = w
        offset_w += tmp
    target.save(os.path.join(DEST, "target.jpg"), "jpeg")

def contact_local_images(cols, rows, start = 0):
    image_data_list = []
    width = 0;
    height = 0;
    for i in range(start, start + cols):
        col_data = []
        for j in range(rows):
            path = os.path.join(DEST, "%d_%d.jpg" % (i, j))
            tmp = Image.open(path)
            data = tmp.copy()
            col_data.append(data)
            tmp.close()
            w, h = data.size
            if j == 0:
                width += w
            if i == start:
                height += h
        image_data_list.append(col_data)
    print("Image size: %d * %d pixes" % (width, height))
    target = Image.new(image_data_list[0][0].mode, (width, height))
    offset_w = 0
    for i in range(cols):
        offset_h = 0
        tmp = 0
        for j in range(rows):
            data = image_data_list[i][j]
            w, h = data.size
            target.paste(data, (offset_w, offset_h))
            offset_h += h
            tmp = w
        offset_w += tmp
    target.save(os.path.join(DEST, "target.png"), "png")

if __name__ == '__main__':
    # os.makedirs(DEST, exist_ok=True)
    # columns, rows, urls = process_curl_script(SCRIPT)
    # valid, images = validate(columns, rows, urls)
    # if not valid:
    #     print("Please check your script!")
    # else:
    #     download(images)
    #     contact_images(columns, rows, images)
    contact_local_images(321, 15)