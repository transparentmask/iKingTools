#!/usr/bin/env python
# -*- encoding: utf-8 -*-
import pefile
import os
import argparse
import json
from iking_utils import iKingUtils
from progressive.bar import Bar


GAME_PATH = 'iKing'
# GAME_PATH = 'iKing_1.4'
PNG_HEADER = ['\x89', '\x50', '\x4E', '\x47', '\x0D', '\x0A', '\x1A', '\x0A']
BITMAP_ID = 0x02


class RES_TYPE:
    ZBM = 'ZBM'
    PNG = 'PNG'
    BMP = 'Bitmap'


def write_bitmap(output_folder, data, name, ext='bmp'):
    final_data = bytearray()
    final_data.extend([0x42, 0x4D])
    final_data.extend(iKingUtils.int2hex(0x0E + len(data), bigEndian=False))
    final_data.extend([0x00, 0x00, 0x00, 0x00])
    palette_data_len = iKingUtils.hex2int(bytearray(data[0x14:0x18]), bigEndian=False)
    final_data.extend(iKingUtils.int2hex(len(data) - palette_data_len + 0x0E, bigEndian=False))
    final_data.extend(data)

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    out_path = os.path.join(output_folder, "%s.%s" % (name, ext))
    with open(out_path, "wb") as file:
        file.write(final_data)
        file.close()
    return out_path


def write_png(output_folder, data, name, ext='png'):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    out_path = os.path.join(output_folder, "%s.%s" % (name, ext))
    with open(out_path, "wb") as file:
        file.write(data)
        file.close()
    return out_path


def write_zbm(output_folder, data, name, ext='res'):
    output_folder_res = os.path.join(output_folder, "res")
    if not os.path.exists(output_folder_res):
        os.makedirs(output_folder_res)

    with open(os.path.join(output_folder_res, "%s.%s" % (name, ext)), "wb") as file:
        file.write(data)
        file.close()

    # convert zbm to bmp, and output
    data_ba = bytearray(data)
    bitmap_data_len = iKingUtils.hex2int(data_ba[0:4], False)
    bitmap_data = data_ba[4:4 + bitmap_data_len]
    palette_data = data_ba[4 + bitmap_data_len:]
    final_data = bytearray()
    '''424D FULL LENS 0000 0000 3604'''
    final_data.extend([0x42, 0x4D])
    final_data.extend(iKingUtils.int2hex(0x0E + len(palette_data) + len(bitmap_data), bigEndian=False))
    final_data.extend([0x00, 0x00, 0x00, 0x00])
    final_data.extend(iKingUtils.int2hex(0x0E + len(palette_data), bigEndian=False))
    final_data.extend(palette_data)
    final_data.extend(bitmap_data)

    out_path = os.path.join(output_folder, "%s.%s" % (name, 'bmp'))
    with open(out_path, "wb") as file:
        file.write(final_data)
        file.close()
    return out_path


def process_dll(iking_path, dll_name, output_path, mapping):
    dll_path = os.path.join(iking_path, dll_name)
    # print(dll_path)
    pe = pefile.PE(dll_path)
    if hasattr(pe, "DIRECTORY_ENTRY_RESOURCE") is False:
        return

    dll_basename = os.path.splitext(dll_name)[0]
    for base_dir in pe.DIRECTORY_ENTRY_RESOURCE.entries:
        folder = None
        ext = None
        res_type = None
        if str(base_dir.name) == 'ZBM':
            res_type = RES_TYPE.ZBM
            folder = str(base_dir.name)
            ext = "res"
        elif str(base_dir.name) == 'PNG':
            res_type = RES_TYPE.PNG
            folder = str(base_dir.name)
            ext = "png"
        elif base_dir.id == BITMAP_ID:
            res_type = RES_TYPE.BMP
            folder = "Bitmap"
            ext = "bmp"
        else:
            continue

        for rsrc in base_dir.directory.entries:
            if rsrc.name is not None and str(rsrc.name).startswith("RID"):
                entry = rsrc.directory.entries[0]
                data_rva = entry.data.struct.OffsetToData
                size = entry.data.struct.Size
                data = pe.get_memory_mapped_image()[data_rva:data_rva + size]
                output_folder = os.path.join(output_path, dll_name.replace(".", "_"), folder)

                out_path = None
                if res_type is RES_TYPE.BMP:
                    out_path = write_bitmap(output_folder, data, rsrc.name, ext)
                elif res_type is RES_TYPE.PNG:
                    out_path = write_png(output_folder, data, rsrc.name, ext)
                else:
                    out_path = write_zbm(output_folder, data, rsrc.name, ext)

                if dll_basename not in mapping:
                    mapping[dll_basename] = {}
                mapping[dll_basename][str(rsrc.name)] = out_path


if __name__ == '__main__':
    parse = argparse.ArgumentParser()
    parse.add_argument('--iking', help='iking game folder', dest='iking_path', default='iKing', type=str)
    parse.add_argument('--output', '-o', help='resources output', dest='output_path', default='Resources1', type=str)
    args = parse.parse_args()

    mapping = {}
    all_in_folder = os.listdir(args.iking_path)
    all_dlls = filter(lambda f: f.endswith("dll"), all_in_folder)
    bar = Bar(max_value=len(all_dlls), fallback=True)
    bar.cursor.clear_lines(3)
    bar.cursor.save()
    for index, dll_file in enumerate(all_dlls):
        process_dll(args.iking_path, dll_file, args.output_path, mapping)
        bar.cursor.restore()
        bar.draw(value=(index + 1))

    with open("resources1.json", "wb") as file:
        json.dump(mapping, file, indent=4)
        file.close()

    # process_dll(args.iking_path, 'GobBmp01.dll', args.output_path)
    # process_dll(args.iking_path, 'MapPattern02_1.dll', args.output_path)
