#!/usr/bin/env python
# -*- encoding: utf-8 -*-
from iking_utils import iKingUtils
from iking_map import *
import argparse
import json
from PIL import Image, ImageDraw
from progressive.bar import Bar


class GobInfo():
    def __init__(self, gob_name='GobName.dat', gob_locate='GobLocate.dat', res_mapping='resources.json'):
        self.gobs = {}
        with open(res_mapping, "rb") as file:
            res_mapping = json.load(file)
            file.close()

        with open(gob_locate, "rb") as file:
            locate_data = bytearray(file.read())
            file.close()

        name_dict = {}
        with open(gob_name, 'rb') as file:
            count = iKingUtils.hex2int(bytearray(file.read(2)), False)
            # print count
            for i in range(0, count):
                key = iKingUtils.hex2int(bytearray(file.read(4)), False)
                name = file.read(0x10).decode('big5').encode('utf-8')
                name_dict[key] = name
            file.close()

        gob_count = len(locate_data) / 4
        for i in range(1, gob_count):
            gob_info = {}
            key = i
            res_path = self.get_resource(res_mapping, 'gobbmp', key)
            if res_path is not None:
                gob_info['path'] = res_path
            if key in name_dict:
                gob_info['name'] = name_dict[key]
            offset = i * 4
            gob_info['locate_x'] = iKingUtils.hex2int(locate_data[offset:offset + 2], False, True)
            gob_info['locate_y'] = iKingUtils.hex2int(locate_data[offset + 2:offset + 4], False, True)
            # if key == 1713:
            #     print gob_info
            #     iKingUtils.dump_bytearray(locate_data[offset:offset + 2])
            #     iKingUtils.dump_bytearray(locate_data[offset + 2:offset + 4])
            self.gobs[key] = gob_info

    def get_resource(self, res_mapping, category, res_id):
        res_key = "RID%d" % (res_id)
        for (category_key, dictionary) in res_mapping.iteritems():
            if category_key.lower().startswith(category) and res_key in dictionary:
                image_path = dictionary[res_key]
                return image_path
        return None


class MapRender(object):
    GobBmp_BK = (0xFF, 0x00, 0xFF, 0x00)
    LOG_FILE = "%s/render.log" % (MapInfo.MAP_FOLDER)

    def __init__(self, map_id, resource_mapping_file):
        self.gob_infos = GobInfo()
        self.map = MapInfo(map_id=map_id)
        with open(resource_mapping_file, "rb") as file:
            self.res_mapping = json.load(file)
            file.close()

    def render_ground(self):
        pass

    def render_item(self, map_image, x, y, item_id, image_cache, use_addon, log):
        if item_id in image_cache:
            item_image = image_cache[item_id]
        else:
            item_image = self.get_item_image(item_id)
            image_cache[item_id] = item_image

        if item_image is not None:
            width, height = item_image.size
            x_offset = y_offset = 0
            if item_id in self.gob_infos.gobs:
                gob = self.gob_infos.gobs[item_id]
                x_offset = gob['locate_x'] - width
                y_offset = gob['locate_y'] - height
                if use_addon:
                    x_offset += MapGridData.PIXEL_WIDTH / 2
                    y_offset += MapGridData.PIXEL_HEIGHT / 2
            # elif item_id in self.gob_infos.gobs:
            #     x_offset = gob['locate_x'] - width
            #     y_offset = gob['locate_y'] - height
            map_image.paste(item_image, (int(x_offset + x * MapGridData.PIXEL_WIDTH), int(y_offset + y * MapGridData.PIXEL_HEIGHT)), item_image)
        else:
            log.write("not found item: [%d, %d] %d\n" % (x, y, item_id))

    def render(self, img_format="png", draw_grids=False):
        MAX_VALUE = self.map.map_grids_max[0] * self.map.map_grids_max[1]

        addon_items = {}
        for item in self.map.addon_items:
            if item.y not in addon_items:
                addon_items[item.y] = {}
            addon_items[item.y][item.x] = item

        clickable_items = {}

        for item in self.map.clickable_items:
            y = int(item.y / 2)
            if y not in clickable_items:
                clickable_items[y] = {}
            clickable_items[y][item.x] = item

        bar = Bar(max_value=MAX_VALUE, fallback=True)

        map_image = Image.new('RGBA', (self.map.map_grids_max[0] * MapGridData.PIXEL_WIDTH, self.map.map_grids_max[1] * MapGridData.PIXEL_HEIGHT))

        log = open(MapRender.LOG_FILE, "w")
        log.write("render: %s\n" % self.map.map_id)

        print "Render %s:" % self.map.map_id

        if draw_grids is True:
            mask_poly = Image.new('RGBA', (MapGridData.PIXEL_WIDTH, MapGridData.PIXEL_HEIGHT))
            draw = ImageDraw.Draw(mask_poly)
            draw.polygon([(0, 0), (0, MapGridData.PIXEL_HEIGHT), (MapGridData.PIXEL_WIDTH, MapGridData.PIXEL_HEIGHT), (MapGridData.PIXEL_WIDTH, 0)], fill=(255, 255, 255, 127), outline=(255, 255, 255, 255))

        print "Draw Grounds:"
        bar.cursor.clear_lines(2)
        bar.cursor.save()
        image_cache = {}
        items = []
        for (y, line) in enumerate(self.map.map_datas):
            for (x, map_grid) in enumerate(self.map.map_datas[y]):
                map_grid = self.map.map_datas[y][x]
                if map_grid.ground != 0:
                    ground_id = map_grid.ground >> 2
                    if ground_id in image_cache:
                        ground_image = image_cache[ground_id]
                    else:
                        ground_image = self.get_ground_image(ground_id)
                        image_cache[ground_id] = ground_image

                    if ground_image is not None:
                        map_image.paste(ground_image, (x * MapGridData.PIXEL_WIDTH, y * MapGridData.PIXEL_HEIGHT))
                    else:
                        log.write("not found ground: [%d, %d] %d -> %d\n" % (x, y, map_grid.ground, ground_id))

                    if y in addon_items and x in addon_items[y]:
                        items.append("%d_%d" % (x, y))
                    elif y in clickable_items and x in clickable_items[y]:
                        items.append("%d_%d" % (x, y))
                    elif map_grid.item != 0 and map_grid.item in self.gob_infos.gobs:
                        items.append("%d_%d" % (x, y))
                bar.cursor.restore()
                bar.draw(value=y * self.map.map_grids_max[0] + x + 1)

        if len(items) > 0:
            print "Draw Items:"
            bar.max_value = len(items)
            bar.cursor.clear_lines(2)
            bar.cursor.save()

            image_cache = {}

            for (i, s) in enumerate(items):
                x, y = map(lambda p: int(p), s.split("_"))
                map_grid = self.map.map_datas[y][x]
                if map_grid.item != 0:
                    self.render_item(map_image, x, y, map_grid.item, image_cache, False, log)

                if y in addon_items and x in addon_items[y]:
                    addon_item = addon_items[y][x]
                    self.render_item(map_image, x, y, addon_item.item, image_cache, True, log)

                if y in clickable_items and x in clickable_items[y]:
                    clickable_item = clickable_items[y][x]
                    log.write("clickable: [%d, %d] %d\n" % (x, y, clickable_item.item_id))
                    self.render_item(map_image, x, y, clickable_item.item_id, image_cache, False, log)

                bar.cursor.restore()
                bar.draw(value=i + 1)

            if draw_grids is True:
                for (i, s) in enumerate(items):
                    x, y = map(lambda p: int(p), s.split("_"))
                    map_grid = self.map.map_datas[y][x]
                    # if map_grid.item != 0 and map_grid.item in self.gob_infos.gobs:
                    # if draw_grids and map_grid.item != 0:
                    # log.write("found item %d on [%d, %d] %d -> %d\n" % (map_grid.item, x, y, map_grid.ground, ground_id))
                    map_image.paste(mask_poly, (x * MapGridData.PIXEL_WIDTH, y * MapGridData.PIXEL_HEIGHT), mask_poly)

        if draw_grids is True:
            draw = ImageDraw.Draw(map_image)
            for x in range(1, self.map.map_grids_max[0]):
                draw.line([(x * MapGridData.PIXEL_WIDTH, 0), (x * MapGridData.PIXEL_WIDTH, self.map.map_grids_max[1] * MapGridData.PIXEL_HEIGHT)], fill=(0x80, 0x81, 0x00))

            for y in range(1, self.map.map_grids_max[1]):
                draw.line([(0, y * MapGridData.PIXEL_HEIGHT), (self.map.map_grids_max[0] * MapGridData.PIXEL_WIDTH, y * MapGridData.PIXEL_HEIGHT)], fill=(0x80, 0x81, 0x00))

        map_image.convert('RGB').save('maps/%s.%s' % (self.map.map_id, img_format))
        map_image.close()
        log.flush()
        log.close()

    def get_image(self, category, res_id):
        res_key = "RID%d" % (res_id)
        for (category_key, dictionary) in self.res_mapping.iteritems():
            if category_key.lower().startswith(category) and res_key in dictionary:
                image_path = dictionary[res_key]
                return Image.open(image_path)
        return None

    def get_ground_image(self, ground_id):
        image = self.get_image("mappattern", ground_id)
        if image is not None:
            image = image.convert("RGBA")
        return image

    def get_item_image(self, item_id, transparency=True):
        image = self.get_image("gobbmp", item_id)
        if image is not None:
            image = image.convert("RGBA")
            if transparency:
                datas = image.getdata()
                newData = []

                for item in datas:
                    if item[:3] == MapRender.GobBmp_BK[:3]:
                        newData.append(MapRender.GobBmp_BK)
                    else:
                        newData.append(item)

                image.putdata(newData)
        return image


class MapThumbnailRender(object):
    def __init__(self, map_id):
        self.gob_infos = GobInfo()
        self.map = MapInfo(map_id=map_id)
        self.colors = [
            [0x00, 0x00, 0x00, 0x00], [0x00, 0xA4, 0xA8, 0x00], [0x13, 0x84, 0x52, 0x00], [0x0B, 0x5F, 0x3A, 0x00],
            [0x36, 0x66, 0x8C, 0x00], [0x6E, 0xA4, 0xC8, 0x00], [0x00, 0x68, 0xA0, 0x00], [0x22, 0x4D, 0x73, 0x00],
            [0xF4, 0xCF, 0x8D, 0x00], [0xEB, 0xB2, 0x00, 0x00], [0xB3, 0x69, 0x00, 0x00], [0x95, 0x43, 0x32, 0x00],
            [0x29, 0x2A, 0x33, 0x00], [0x55, 0x64, 0x76, 0x00], [0x75, 0x8B, 0x9E, 0x00], [0x58, 0x5F, 0x99, 0x00],
            [0x73, 0x73, 0x73, 0x00], [0x73, 0x73, 0x73, 0x00], [0x73, 0x73, 0x73, 0x00], [0x6F, 0x61, 0x00, 0x00],
            [0x02, 0xD3, 0xCC, 0x00], [0x5E, 0xC4, 0xB2, 0x00], [0x00, 0x4A, 0x74, 0x00], [0x19, 0x49, 0xA9, 0x00],
            [0x33, 0x33, 0x33, 0x00], [0xA8, 0xE9, 0xF9, 0x00], [0x4F, 0x83, 0xA9, 0x00], [0x77, 0xBC, 0xD5, 0x00],
            [0x00, 0x64, 0x00, 0x00], [0x3C, 0x44, 0x52, 0x00], [0xBF, 0xBF, 0xBF, 0x00], [0xE6, 0xE6, 0xE6, 0x00],
            [0x00, 0x47, 0xE4, 0x00], [0x6A, 0x41, 0x47, 0x00], [0x3E, 0x00, 0x80, 0x00], [0x82, 0x82, 0x82, 0x00],
            [0x6A, 0x6D, 0x2B, 0x00], [0x57, 0x44, 0x0E, 0x00], [0xFF, 0xFF, 0xFF, 0x00], [0x42, 0x31, 0x42, 0x00],
            [0x3C, 0x3C, 0x64, 0x00], [0x3C, 0x3C, 0x6E, 0x00], [0xF7, 0x73, 0x29, 0x00], [0x3D, 0x2D, 0x08, 0x00],
            [0x53, 0x4A, 0x4D, 0x00], [0x35, 0x29, 0x39, 0x00], [0x28, 0xD8, 0x10, 0x00]
        ]
        self.convert_table = [
            0x00, 0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08, 0x0A,
            0x0B, 0x0C, 0x0D, 0x0E, 0x0F, 0x13, 0x14, 0x15, 0x03, 0x21,
            0x1D, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
            0x00, 0x00, 0x01, 0x03, 0x06, 0x02, 0x02, 0x07, 0x02, 0x05,
            0x04, 0x06, 0x06, 0x06, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
            0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
            0x00, 0x00, 0x00, 0x00, 0x01, 0x02, 0x03, 0x05, 0x06, 0x00,
            0x00, 0x00, 0x0A, 0x05, 0x0B, 0x02, 0x08, 0x02, 0x08, 0x09,
            0x0B, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x10, 0x10,
            0x11, 0x11, 0x11, 0x11, 0x12, 0x12, 0x16, 0x17, 0x18, 0x18,
            0x18, 0x18, 0x19, 0x1B, 0x11, 0x11, 0x17, 0x1A, 0x1B, 0x00,
            0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x23, 0x00,
            0x0C, 0x0D, 0x0E, 0x0F, 0x0C, 0x0D, 0x0E, 0x0F, 0x0D, 0x0F,
            0x0E, 0x0C, 0x0C, 0x0D, 0x0E, 0x0F, 0x08, 0x08, 0x14, 0x14,
            0x15, 0x15, 0x15, 0x15, 0x15, 0x15, 0x0D, 0x0D, 0x04, 0x04,
            0x03, 0x03, 0x03, 0x03, 0x21, 0x21, 0x21, 0x21, 0x21, 0x21
        ]

    def render(self, img_format="png", pixel_size=4):
        MAX_VALUE = self.map.map_grids_max[0] * self.map.map_grids_max[1]

        bar = Bar(max_value=MAX_VALUE, fallback=True)

        map_image = Image.new('RGB', (self.map.map_grids_max[0] * pixel_size, self.map.map_grids_max[1] * pixel_size))
        thumbnail_file = open('maps/%s_thumbnail.map' % (self.map.map_id), "wb")
        thumbnail_file.write(iKingUtils.int2hex(self.map.map_grids_max[0], 2, bigEndian=False))
        thumbnail_file.write(iKingUtils.int2hex(self.map.map_grids_max[1] * 2, 2, bigEndian=False))

        print "Render thumbnail %s:" % self.map.map_id

        addon_items = {}
        for item in self.map.addon_items:
            if item.y not in addon_items:
                addon_items[item.y] = {}
            addon_items[item.y][item.x] = item

        bar.cursor.clear_lines(2)
        bar.cursor.save()
        for (y, line) in enumerate(self.map.map_datas):
            for (x, map_grid) in enumerate(self.map.map_datas[y]):
                map_grid = self.map.map_datas[y][x]
                color_id = self.convert((map_grid.item << 0x10) + map_grid.ground)
                # if map_grid.item == 0 and y in addon_items and x in addon_items[y]:
                #     color_id = self.convert((addon_items[y][x].item << 0x10) + map_grid.ground)
                # if x == 90 and y == 10:
                #     ii = iKingUtils.int2hex(map_grid.item, 2)
                #     ai = 0
                #     if y in addon_items and x in addon_items[y]:
                #         ai = addon_items[y][x].item
                #     ai = iKingUtils.int2hex(ai, 2)
                #     gi = iKingUtils.int2hex(map_grid.ground, 2)  # 8D 5D
                #     i = iKingUtils.int2hex((map_grid.item << 0x10) + map_grid.ground, 4)  # 8D 5D
                #     ci = iKingUtils.int2hex(color_id, 1)  # 15 (1C)
                #     if y in addon_items and x in addon_items[y]:
                #         cia = self.convert((map_grid.item << 0x10) + map_grid.ground)
                #         ci += iKingUtils.int2hex(cia, 1)
                color = self.colors[color_id]
                thumbnail_file.write(iKingUtils.int2hex(color_id, 1, bigEndian=False))

                color_image = Image.new('RGB', (pixel_size, pixel_size), (color[2], color[1], color[0]))
                map_image.paste(color_image, (x * pixel_size, y * pixel_size))
                color_image.close()

                bar.cursor.restore()
                bar.draw(value=y * self.map.map_grids_max[0] + x + 1)

        # print "\n%s, map_grid.item: %s, map_grid.ground: %s addon_item: %s, color_id: %s\n" % (iKingUtils.dump_bytearray(i, ret=True), iKingUtils.dump_bytearray(ii, ret=True), iKingUtils.dump_bytearray(gi, ret=True), iKingUtils.dump_bytearray(ai, ret=True), iKingUtils.dump_bytearray(ci, ret=True))
        map_image.save('maps/%s_thumbnail.%s' % (self.map.map_id, img_format))
        map_image.close()
        thumbnail_file.close()

    def convert(self, ground_id):
        if ground_id == 0:
            return 0
        hiword = (ground_id >> 0x10) & 0xFFFF
        byte1 = ((ground_id & 0xffff) >> 0x08) & 0xff

        if hiword >= 0x321 and hiword <= 0x36E:
            return 0x1E
        if byte1 >= 0x58 and byte1 <= 0x67:
            return self.convert_table[byte1]
        if hiword >= 0x2328:
            return self.convert_table[byte1]
        if hiword >= 0x01 and hiword <= 0x40:
            return 0x1C
        if hiword >= 0x41 and hiword <= 0x60:
            return 0x1D
        if hiword >= 0xF1 and hiword <= 0x130:
            return 0x1F
        if hiword >= 0x60F and hiword <= 0x64F:
            return 0x1F
        if hiword >= 0xC8 and hiword <= 0x154:
            return 0x11
        if hiword >= 0x579 and hiword <= 0x658:
            return 0x11
        if hiword != 0:
            return 0x1E
        if byte1 > 0xDC and byte1 < 0xED:
            return self.convert2(byte1, ((ground_id >> 2) & 0x3F) + 0x01)

        if byte1 < 0xA0 or byte1 > 0xA5:
            if byte1 < 0xED or byte1 > 0xFF:
                if byte1 >= 0xCE and byte1 <= 0xD1:
                    return 0x28
                if byte1 >= 0xD2 and byte1 <= 0xD4:
                    return 0x29
                if byte1 < 0xC9 or byte1 > 0xD2:
                    if byte1 < 0x15 or byte1 > 0x15:
                        if byte1 < 0x1E or byte1 > 0x1F:
                            if byte1 >= 0xA6 and byte1 <= 0xB7:
                                return 0x27
                            if byte1 >= 0xB8 and byte1 <= 0xBA:
                                return 0x2A
                            if byte1 >= 0xBB and byte1 <= 0xBC:
                                return 0x2B
                            if byte1 >= 0xBD and byte1 <= 0xC0 or byte1 >= 0xC2 and byte1 <= 0xC5:
                                return 0x2C
                            if byte1 == 0xC1:
                                return 0x2D
                            if byte1 >= 0xD5 and byte1 <= 0xD7:
                                return 0x2E
                            if byte1 >= 0xD8 and byte1 <= 0xD9:
                                return 0x2B
                        else:
                            v2 = ground_id >> 2
                            if v2 >= 0x780 and v2 <= 0x797 or v2 >= 0x7C0 and v2 <= 0x7D7:
                                return 0x02
                    else:
                        v3 = ground_id >> 2
                        if v3 >= 0x540 and v3 <= 0x557:
                            return 0x26
                else:
                    v4 = ground_id >> 2
                    if v4 >= 0x3240 and v4 <= 0x3343:
                        return 0x20
            else:
                v5 = ground_id >> 2
                if v5 >= 0x3B40 and v5 <= 0x3C7F:
                    return 0x25
                if v5 >= 0x3C80 and v5 <= 0x3DBF:
                    return 0x24
                if v5 >= 0x3DC0 and v5 <= 0x3F9F:
                    return 0x22
        else:
            v6 = ground_id >> 2
            if v6 >= 0x2800 and v6 <= 0x287F:
                return 0x02
            if v6 >= 0x2880 and v6 <= 0x28FF:
                return 0x06
            if v6 >= 0x2900 and v6 <= 0x291F:
                return 0x05
            if v6 >= 0x2920 and v6 <= 0x293F:
                return 0x08
            if v6 >= 0x2940 and v6 <= 0x295F:
                return 0x02
        if byte1 >= 0xA0:
            return 0x00

        return self.convert_table[byte1]

    def convert2(self, par1, par2):
        result = 0x09
        if par1 == 0xE0 or par1 == 0xE1 or par1 == 0xE2:
            return result if par2 < 0x01 or par2 > 0x03 else 0x02
        elif par1 == 0xE5:
            if (par2 < 0x01 or par2 > 0x07) and (par2 < 0x0B or par2 > 0x0E) and \
               (par2 < 0x13 or par2 > 0x15) and (par2 < 0x1B or par2 > 0x1C) and \
               par2 != 0x23 and par2 != 0x24 and (par2 < 0x2A or par2 > 0x2C):
                return result
            return 0x02
        elif par1 == 0xE6:
            if (par2 < 0x01 or par2 > 0x02) and (par2 < 0x08 or par2 > 0x09) and \
               (par2 < 0x16 or par2 > 0x17) and (par2 < 0x1D or par2 > 0x1E) and \
               (par2 < 0x2A or par2 > 0x2B) and (par2 < 0x30 or par2 > 0x31) and par2 != 0x24:
                return result
            return 0x02
        elif par1 == 0xE7:
            if (par2 < 0x01 or par2 > 0x0B) and (par2 < 0x0F or par2 > 0x11) and \
               (par2 < 0x21 or par2 > 0x23) and (par2 < 0x27 or par2 > 0x2A) and \
               (par2 < 0x2C or par2 > 0x31) and par2 != 0x15 and par2 != 0x1C:
                return result
            return 0x02
        elif par1 == 0xE8:
            if (par2 < 0x06 or par2 > 0x08) and (par2 < 0x0D or par2 > 0x0F) and \
               (par2 < 0x15 or par2 > 0x17) and (par2 < 0x1D or par2 > 0x1F) and \
               (par2 < 0x24 or par2 > 0x27) and (par2 < 0x2B or par2 > 0x2F) and par2 != 0x01:
                return result
            return 0x02

        return result


def test():
    map_image = Image.new('RGBA', (300, 300))

    img = Image.open('Resources/MapPattern01_dll/ZBM/RID128.bmp').convert('RGBA')
    map_image.paste(img, (150, 150))

    gob = GobInfo().gobs[2]
    tree = Image.open(gob['path'])
    tree = tree.convert("RGBA")
    datas = tree.getdata()
    newData = []

    for item in datas:
        # print "0x%.2X 0x%.2X 0x%.2X" % (item[0], item[1], item[2])
        if item[:3] == MapRender.GobBmp_BK[:3]:
            newData.append(MapRender.GobBmp_BK)
        else:
            newData.append(item)

    tree.putdata(newData)
    width, height = tree.size
    map_image.paste(tree, (gob['locate_x'] - width + 150, gob['locate_y'] - height + 150), tree)
    map_image.save("ta.png")


def render_map(map_id, res_dict, format_="jpg", draw_grids=False, show_log=False):
    render = MapRender(map_id, res_dict)
    render.render(format_, draw_grids)

    render = MapThumbnailRender(map_id)
    render.render(pixel_size=8)

    if show_log:
        os.system('cat %s' % MapRender.LOG_FILE)


def show_list(all_map_datas, all_maps_dict):
    for d in all_map_datas:
        d_name = os.path.splitext(d)[0]
        if d_name in all_maps_dict:
            d_time = os.path.getmtime(os.path.join(MapInfo.MAP_FOLDER, "%s" % d))
            m_time = os.path.getmtime(os.path.join(MapInfo.MAP_FOLDER, "%s" % all_maps_dict[d_name]))
            if m_time > d_time:
                print "%s rendered!" % d_name.ljust(20, " ")
            else:
                print "%s rendered, but data updated!" % d_name.ljust(20, " ")
        else:
            print "%s not rendered!" % d_name.ljust(20, " ")


def render_all(all_map_datas, res_dict, format_="jpg", draw_grids=False, show_log=False):
    for d in all_map_datas:
        d_name = os.path.splitext(d)[0]
        render_map(d_name, res_dict, format_, draw_grids, show_log)


def render_all_new(all_map_datas, all_maps_dict, res_dict, format_="jpg", draw_grids=False, show_log=False):
    all_new = []
    for d in all_map_datas:
        d_name = os.path.splitext(d)[0]
        if d_name in all_maps_dict:
            d_time = os.path.getmtime(os.path.join(MapInfo.MAP_FOLDER, "%s" % d))
            m_time = os.path.getmtime(os.path.join(MapInfo.MAP_FOLDER, "%s" % all_maps_dict[d_name]))
            if m_time <= d_time:
                all_new.append(d_name)
        else:
            all_new.append(d_name)

    if len(all_new) > 0:
        for d_name in all_new:
            render_map(d_name, res_dict, format_, draw_grids, show_log)
    else:
        print "No map need render!"


if __name__ == '__main__':
    support_formats = ["jpg", "png", "bmp"]

    parse = argparse.ArgumentParser()
    parse.add_argument('--map', '-m', help='map id', dest='map_id', default=None, type=str)
    parse.add_argument('--res', '-r', help='resource dict', dest='res_dict', default='resources.json', type=str)
    parse.add_argument('--format', '-f', help='output format, support [%s]' % ", ".join(support_formats), dest='format', default='jpg', type=str)
    parse.add_argument('--grids', '-g', help='[DEBUG]render grids in map', dest='draw_grids', action='store_true')
    parse.add_argument('--log', help='[DEBUG]show render log when finish', dest='show_log', action='store_true')
    parse.add_argument('--list', '-l', help='list all map datas', dest='list', action='store_true')
    parse.add_argument('--all', '-a', help='render all maps', dest='all', action='store_true')
    parse.add_argument('--new', '-n', help='render all maps with new datas', dest='new', action='store_true')
    args = parse.parse_args()

    need_show_help = True
    if args.map_id is not None:
        if os.path.exists(os.path.join(MapInfo.MAP_FOLDER, "%s.map" % args.map_id)):
            if args.format in support_formats:
                render_map(args.map_id, args.res_dict, args.format, args.draw_grids, args.show_log)
                need_show_help = False
            else:
                print "render format not supported!! %s" % args.format
                exit(1)
        else:
            print "map data file not exists!! %s" % args.map_id
            exit(1)
    elif args.list or args.all or args.new:
        all_in_map_folder = os.listdir(MapInfo.MAP_FOLDER)
        all_map_datas = filter(lambda f: f.endswith("map"), all_in_map_folder)
        all_maps = filter(lambda f: f.split(".")[-1] in support_formats, all_in_map_folder)
        all_maps_dict = dict(zip(map(lambda m: os.path.splitext(m)[0], all_maps), all_maps))

        if args.list:
            show_list(all_map_datas, all_maps_dict)
        elif args.all:
            render_all(all_map_datas, args.res_dict, args.format, args.draw_grids, args.show_log)
        elif args.new:
            render_all_new(all_map_datas, all_maps_dict, args.res_dict, args.format, args.draw_grids, args.show_log)
    else:
        parse.print_help()

    # test()

    # GobInfo()

    # print GobInfo().gobs[1]
    # print GobInfo().gobs[98]
    # print GobInfo().gobs[593]
    # print iKingUtils.int2hex(GobInfo().gobs[1713]['locate_x'], 2)
