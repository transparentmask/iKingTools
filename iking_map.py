#!/usr/bin/env python
# -*- encoding: utf-8 -*-
from iking_utils import iKingUtils
from iking_data import *
import os.path


class iKingGob(object):
    gobs = {}

    def __init__(self):
        with open('GobName.dat', 'rb') as file:
            count = iKingUtils.hex2int(bytearray(file.read(2)), False)
            # print count
            for i in range(0, count):
                key = iKingUtils.hex2int(bytearray(file.read(4)), False)
                name = file.read(0x10).decode('big5').encode('utf-8')
                self.gobs[key] = name
                # print "%d(%s): %s" % (key, iKingUtils.dump_bytearray(iKingUtils.int2hex(key, 2), ret=True), name)
                # break


class MapGridData(object):
    PIXEL_WIDTH = 80
    PIXEL_HEIGHT = 40

    def __init__(self, x, y, map_grid_data):
        self.x = x
        self.y = y

        self.offset_hex = None
        self.item_hex = map_grid_data[0:2]
        self.ground_hex = map_grid_data[2:4]

        self.item = iKingUtils.hex2int(self.item_hex)
        self.ground = iKingUtils.hex2int(self.ground_hex)

    def get_data(self):
        return self.item_hex + self.ground_hex

    def desc(self):
        return "%.2X%.2X_%.2X%.2X" % (self.item_hex[0], self.item_hex[1], self.ground_hex[0], self.ground_hex[1])


class MapAddonItem(object):
    def __init__(self, map_addon_data):
        self.data = map_addon_data

        self.x = iKingUtils.hex2int(map_addon_data[0:2])
        self.y = iKingUtils.hex2int(map_addon_data[2:4])
        self.y = int(self.y / 2)
        self.offset = iKingUtils.hex2int(map_addon_data[4:6])
        self.item_hex = map_addon_data[6:8]
        self.item = iKingUtils.hex2int(self.item_hex)

    # def desc(self):
    #     return "%.2X%.2X_%.2X%.2X" % (self.item_hex[0], self.item_hex[1], self.ground_hex[0], self.ground_hex[1])


class MapInfo(object):
    MAP_FOLDER = "maps"

    def __init__(self, map_enterance_data=None, map_id=None):
        self.map_id = ""
        self.map_file = ""
        self.player_id = ""
        self.map_bounds = [-1, -1]
        self.map_grids_max = [-1, -1]
        self.map_datas = None
        self.map_pos = [-1, -1]
        self.addon_items = []
        self.clickable_items = []

        self.init_map(map_enterance_data, map_id)

    def fill_empty_map(self):
        self.map_datas = [[MapGridData(0, 0, bytearray('\x00\x00\x00\x00')) for i in range(self.map_grids_max[0])] for i in range(self.map_grids_max[1])]

    def load_local_map(self):
        if os.path.exists(self.map_file):
            with open(self.map_file, "rb") as file:
                data = bytearray(file.read())
                file.close()
                if str(data[0:4]) == "KMAP":
                    data_offset = iKingUtils.hex2int(data[4:8], bigEndian=False)
                    (map_id, tn) = iKingUtils.export_string(data, 8)
                    self.map_bounds[0] = iKingUtils.hex2int(data[tn:tn + 2], bigEndian=False)
                    self.map_bounds[1] = iKingUtils.hex2int(data[tn + 2:tn + 4], bigEndian=False)
                    self.map_grids_max = [self.map_bounds[0], self.map_bounds[1] / 2]
                    if self.map_datas is None:
                        self.fill_empty_map()
                    grid_count = iKingUtils.hex2int(data[data_offset:data_offset + 4], bigEndian=False)
                    self.parse_map_datas_(data[data_offset + 4:], self.map_grids_max[0] * self.map_grids_max[1], range(self.map_grids_max[0]), range(self.map_grids_max[1]))

                    offset = data_offset + 4 + grid_count * 4
                    addon_count = iKingUtils.hex2int(data[offset:offset + 4], bigEndian=False)
                    offset += 4
                    for i in range(addon_count):
                        self.addon_items.append(MapAddonItem(data[offset:offset + 8]))
                        offset += 8

                    clickable_count = iKingUtils.hex2int(data[offset:offset + 4], bigEndian=False)
                    offset += 4
                    for i in range(clickable_count):
                        item_length = iKingUtils.hex2int(data[offset:offset + 2], bigEndian=False)
                        offset += 2
                        self.clickable_items.append(iKingGroundItem(data[offset:offset + item_length]))
                        offset += item_length

    def save_map(self):
        if not os.path.exists(MapInfo.MAP_FOLDER):
            os.mkdir(MapInfo.MAP_FOLDER)

        with open(self.map_file, "wb") as file:
            file.write("KMAP")
            file.write(iKingUtils.int2hex(4 + 4 + len(self.map_id) + 1 + 2 + 2, bigEndian=False))
            file.write(self.map_id + "\x00")
            file.write(iKingUtils.int2hex(self.map_bounds[0], 2, bigEndian=False))
            file.write(iKingUtils.int2hex(self.map_bounds[1], 2, bigEndian=False))
            file.write(iKingUtils.int2hex(self.map_grids_max[0] * self.map_grids_max[1], bigEndian=False))
            for map_line in self.map_datas:
                for map_grid in map_line:
                    file.write(map_grid.get_data())

            file.write(iKingUtils.int2hex(len(self.addon_items), bigEndian=False))
            if len(self.addon_items) > 0:
                self.addon_items.sort(key=lambda item: item.y * self.map_grids_max[0] + item.x)
                for addon_item in self.addon_items:
                    file.write(addon_item.data)

            file.write(iKingUtils.int2hex(len(self.clickable_items), bigEndian=False))
            if len(self.clickable_items) > 0:
                self.clickable_items.sort(key=lambda item: item.y * self.map_grids_max[0] + item.x)
                for clickable_item in self.clickable_items:
                    file.write(iKingUtils.int2hex(len(clickable_item.data), length=2, bigEndian=False))
                    file.write(clickable_item.data)

            file.close()

    def init_map(self, map_enterance_data=None, map_id=None):
        self.addon_items = []
        self.clickable_items = []
        if map_enterance_data is not None:
            (grid_count, map_datas) = self.enter_map(map_enterance_data)
            self.load_local_map()
            self.parse_map_datas(map_datas, grid_count)
        elif map_id is not None:
            self.map_id = map_id
            self.map_file = os.path.join(MapInfo.MAP_FOLDER, "%s.map" % map_id)
            self.load_local_map()

    def enter_map(self, map_enterance_data):
        self.map_pos[0] = iKingUtils.hex2int(map_enterance_data[0:2])
        self.map_pos[1] = iKingUtils.hex2int(map_enterance_data[2:4])
        (map_player, tn) = iKingUtils.export_string(map_enterance_data, 4)
        (self.map_id, self.player_id) = map_player.strip('\x00').split(' ', 1)
        self.map_file = os.path.join(MapInfo.MAP_FOLDER, "%s.map" % self.map_id)
        self.map_bounds[0] = iKingUtils.hex2int(map_enterance_data[tn:tn + 2])
        self.map_bounds[1] = iKingUtils.hex2int(map_enterance_data[tn + 2:tn + 4])
        self.map_grids_max = [self.map_bounds[0], self.map_bounds[1] / 2]
        self.fill_empty_map()
        grid_count = iKingUtils.hex2int(map_enterance_data[tn + 4:tn + 8])
        return (grid_count, map_enterance_data[tn + 8:])

    def moveon_map(self, map_datas):
        direction = map_datas[0]
        grid_count = iKingUtils.hex2int(map_datas[1:5])
        # print "---------%s----%d" % (iKingUtils.direction_desc(direction), grid_count)
        self.parse_map_datas(map_datas[5:], grid_count, direction)

    def is_out_door(self):
        x = self.map_pos[0]
        y = int(self.map_pos[1] / 2)
        map_data = self.map_datas[y][x]
        ground = map_data.ground >> 2
        if ground < 0x1600:
            if ground < 0xB00:
                return (True, "outdoor")
            elif ground >= 1100:
                return (True, "outdoor")
            else:
                return (False, "indoor")
        elif ground < 0x1E00:
            print (False, "indoor")
        else:
            return (True, "outdoor")

        return (None, "Unknown")

    def parse_addon_item(self, map_datas):
        # kk_type_0019(0x1C): 0x00 0x01 0x00 0x19 0x00 0x00 0x00 0x14
        # 0x00 0x00 0x00 0x04 0x00 0x3F 0x00 0x6D 0x00 0x00 0x14 0x20 0x00 0x44 0x00 0x6F 0x00 0x00 0x14 0x22
        count = iKingUtils.hex2int(map_datas[0:4])
        offset = 4
        if count != 4:
            print "****----****0019-count: %d" % (count)
        while offset < len(map_datas):
            addon_item = MapAddonItem(map_datas[offset:offset + 8])
            if len(filter(lambda item: item.x == addon_item.x and item.y == addon_item.y, self.addon_items)) == 0:
                self.addon_items.append(addon_item)
            # x = iKingUtils.hex2int(map_datas[offset + 0:offset + 2])
            # y = iKingUtils.hex2int(map_datas[offset + 2:offset + 4])
            t = iKingUtils.hex2int(map_datas[offset + 4:offset + 6])
            if t != 0:
                print "****----****0019-unknown: %d" % (t)
            # item = iKingUtils.hex2int(map_datas[offset + 6:offset + 8])
            # print "%d, %d: %d" % (x, y, item)
            # # self.addon_items[y] = {x: item}
            # self.addon_items.append(map_datas[offset:offset + 8])
            # # print "[%d, %d](%d, %d): %s" % (x, y, x, int(y / 2), self.map_datas[int(y / 2)][x].desc())
            # # self.map_datas[int(y / 2)][x].item_hex = map_datas[offset + 6:offset + 8]
            # # self.map_datas[int(y / 2)][x].item = item
            # # print "[%d, %d](%d, %d): %s" % (x, y, x, int(y / 2), self.map_datas[int(y / 2)][x].desc())
            offset += 8

    def add_clickable_item(self, ground_item):
        if len(filter(lambda item: item.x == ground_item.x and item.y == ground_item.y, self.clickable_items)) == 0:
            self.clickable_items.append(ground_item)

    def parse_map_datas(self, map_datas, grid_count, direction=-1):
        # print '0006     \tenter map(%s)(size: [%d, %d]) @ [%d, %d], count: %d(0x%.2X)' % (self.map_id, self.map_bounds[0], map_max_y, x, y, count, count)
        # iKingMap.parse(data[tn + 8:])
        if direction == -1:
            # 0006
            x_range = range(self.map_pos[0] - 5, self.map_pos[0] + 6)
            y_range = range(int(self.map_pos[1] / 2) - 5, int(self.map_pos[1] / 2) + 15)
            self.parse_map_datas_(map_datas, grid_count, x_range, y_range)
        else:
            # 0003
            # 0->e, 1->w, 2->s, 3->n, 4->ne, 5->se, 6->nw, 7->sw
            x, y = iKingUtils.move_cal(self.map_pos[0], self.map_pos[1], direction)
            self.map_pos = [x, y]
            y_odd = (y % 2 == 1)
            y = int(y / 2)

            if direction >= 4:
                if direction == 4:
                    # ne
                    if y_odd:
                        direction = 3
                    else:
                        direction = 0
                elif direction == 5:
                    # se
                    if y_odd:
                        x_range = y_range = []
                elif direction == 6:
                    # nw
                    if not y_odd:
                        x_range = y_range = []
                elif direction == 7:
                    # sw
                    if y_odd:
                        direction = 1
                    else:
                        direction = 2

            if direction <= 3:
                if direction == 0:
                    # e
                    x_range = range(x + 5, x + 6)
                    y_range = range(y - 5, y + 15)
                elif direction == 1:
                    # w
                    x_range = range(x - 5, x - 4)
                    y_range = range(y - 5, y + 15)
                elif direction == 2:
                    # s
                    x_range = range(x - 5, x + 6)
                    y_range = range(y + 14, y + 15)
                elif direction == 3:
                    # n
                    x_range = range(x - 5, x + 6)
                    y_range = range(y - 5, y - 4)

                self.parse_map_datas_(map_datas, grid_count, x_range, y_range)
            else:
                if direction == 5 and not y_odd and grid_count == 31:
                    # se
                    # e
                    x_range = range(x + 5, x + 6)
                    y_range = range(y - 5, y + 15)
                    self.parse_map_datas_(map_datas[:20 * 4], 20, x_range, y_range)
                    # s
                    x_range = range(x - 5, x + 6)
                    y_range = range(y + 14, y + 15)
                    self.parse_map_datas_(map_datas[20 * 4:], 11, x_range, y_range)
                if direction == 6 and y_odd and grid_count == 31:
                    # nw
                    # w
                    x_range = range(x - 5, x - 4)
                    y_range = range(y - 5, y + 15)
                    self.parse_map_datas_(map_datas[:20 * 4], 20, x_range, y_range)
                    # n
                    x_range = range(x - 5, x + 6)
                    y_range = range(y - 5, y - 4)
                    self.parse_map_datas_(map_datas[20 * 4:], 11, x_range, y_range)

    def parse_map_datas_(self, map_datas, grid_count, x_range, y_range):
        x = x_range[0]
        y = y_range[0]
        # line_grids = []
        for index in range(grid_count):
            offset = index * 4
            map_data = MapGridData(x, y, map_datas[offset:offset + 4])
            if x >= 0 and x < self.map_grids_max[0] and y >= 0 and y < self.map_grids_max[1]:
                self.map_datas[y][x] = map_data

            x = x + 1
            if x > x_range[-1]:
                x = x_range[0]
                y = y + 1


if __name__ == '__main__':
    gob = iKingGob()
