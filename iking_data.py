#!/usr/bin/env python
# -*- encoding: utf-8 -*-
import threading
from abc import ABCMeta, abstractmethod
from iking_utils import iKingUtils
from iking_magic import *


'''
name
nickname
race
gender
class
rank
item_name
gold
exp
mud_age
hp
sp
max_hp
max_sp
str
dex
con
int
kar
sta
max_damage
max_damage2
armor_class
weapon_class
weapon_class2
load
max_load
level
defense_bonus
'''


class iKingGameInfos:
    def __init__(self):
        self.mobs = {}
        self.mobs_lock = threading.Lock()
        self.ground_items = {}
        self.ground_items_lock = threading.Lock()
        self.player_items = []
        self.player_items_lock = threading.Lock()


class Pos(object):
    def __init__(self, x=None, y=None, pos_data=None):
        if x is not None and y is not None:
            self.x = x
            self.y = y
        elif pos_data is not None:
            self.x = iKingUtils.hex2int(pos_data[0:2])
            self.y = iKingUtils.hex2int(pos_data[2:4])
        else:
            self.x = -1
            self.y = -1

    def move(self, direction):
        self.x, self.y = iKingUtils.move_cal(self.x, self.y, direction)


class iKingBaseMod:
    __metaclass__ = ABCMeta

    def __init__(self, data=None):
        if data is not None:
            self.parse(data)

    @abstractmethod
    def parse(self, data):
        pass

    @abstractmethod
    def print_debug(self, type_, addInfo=''):
        pass

    @abstractmethod
    def update(self, data):
        pass


class iKingMob(iKingBaseMod):
    def parse(self, data):
        # mob appear
        # 00 40 X
        # 00 6B Y
        # 06
        # 00 Nick
        # E6 BD 87 E6 B0 B4 00  Name
        # 66 72 65 65 77 65 68 00  ID
        # 00 00 00 09 生物类别?(09=人类?)
        # 00 00 00 01 生物属性?(01=男性, 02=女性, 其他=mob)
        # 00 00 12 07 #帽子
        # 00 10 22 01
        # 00 01 05 03 #衣服
        # 00 00 00 00
        # 00 00 10 09 #鞋子
        # 00 00 70 04 #披风
        # 00 00 00 16 #右手武器
        # 00 00 00 00
        if len(data) == 0:
            self.unknown1 = bytearray()
            self.unknown2 = bytearray()
            return
        self.x = iKingUtils.hex2int(data[0:2])
        self.y = iKingUtils.hex2int(data[2:4])
        self.unknown1 = data[4]
        (self.nick, tn) = iKingUtils.export_string(data, 5)
        (self.name, tnn) = iKingUtils.export_string(data, tn)
        (self.id, ti) = iKingUtils.export_string(data, tnn)
        self.unknown2 = data[-40:]

        self.key = "%d_%d" % (self.x, self.y)
        self.buff_list = []

    def check_pos(self, x=None, y=None, pos=None):
        if pos is not None:
            return self.x == pos.x and self.y == pos.y

        return self.x == x and self.y == y

    def move(self, x=None, y=None, pos=None):
        if pos is not None:
            self.x = pos.x
            self.y = pos.y
        else:
            self.x = x
            self.y = y
        self.key = "%d_%d" % (self.x, self.y)

    def buff_change(self, data):
        buff = data[-1]
        if data[-2] == 0x00:
            self.buff_list.append(buff)
        elif data[-2] == 0x80:
            if buff in self.buff_list:
                self.buff_list.remove(buff)
        else:
            print "WRONG BUFF!!!!!!!!!! 0x%.2X 0x%.2x" % (data[-2], data[-1])

    def print_debug(self, type_='0005', addInfo='appear'):
        print self.desc(type_, addInfo)

    def desc(self, type_='0005', addInfo='appear'):
        s = "%s     \tmob %.6s(0x%.2X): %s @ %s %s " % (type_, addInfo, self.unknown1, self.fullname(), self.pos(), self.pos(True))
        return iKingUtils.dump_bytearray(self.unknown2, s, ret_full=True)

    def fullname(self):
        mob_nick_s = ""
        if hasattr(self, "nick") and len(self.nick) > 1:
            mob_nick_s = '「%s」' % self.nick
        return "%s%s(%s)" % (mob_nick_s, self.name, self.id)

    def pos(self, hex=False):
        if hex:
            return "[0x%.2X,0x%.2X]" % (self.x, self.y)
        else:
            return "[%d,%d]" % (self.x, self.y)

    def update(self, data):
        pass


class iKingPlayer(iKingMob):
    def parse_0A(self, data):
        # 00 3A     X
        # 00 64     Y
        # E4 BA BA E9 A1 9E 00  人类
        # E7 94 B7 E6 80 A7 00  男性
        # E9 AD 94 E6 B3 95 E5 B8 AB 00 魔法师
        # 00 英雄
        # 00 kindgom
        # 00 00 00 13
        # 00 01 level
        # 00 01 str
        # 00 01 dex
        # 00 01 con
        # 00 01 int
        # 00 01 sta
        # 00 01 kar
        # 00 07 伤害力 max_damage
        # 00 00 左手伤害
        # 00 07 右手武器等级 weapon_class
        # 00 00 左手命中
        # 00 09 防御力 armor_class
        # 00 21 最大负重
        # 00 1F 当前负重
        # 00 26 HP_MAX
        # 00 26 HP
        # 00 26 MP_MAX
        # 00 26 MP
        # 00 04 额防 defense_bonus
        # 00 00
        # 00 03
        # 00 00 00 08 Gold
        # 00 00 01 F4 Exp
        # 00 01 94 C5

        # 0x00 0x00 0x00 0x03 0x00 0x00 0x5C 0xE6 0x1F 0x58 0x46 0x68 0x00 0x0E 0x2D 0xA6

        # 0x00 0x75
        # 0x01 0x8A
        # 0xE4 0xBA 0xBA 0xE9 0xA1 0x9E 0x00
        # 0xE7 0x94 0xB7 0xE6 0x80 0xA7 0x00
        # 0xE6 0x88 0xB0 0xE5 0xA3 0xAB 0x00
        # 0x00
        # 0xE9 0xBB 0x91 0xE9 0xBE 0x99 0xE5 0xA0 0xA1 0x20 0x31 0x00
        # 0x00 0x00 0x00 0x13
        # 0x00 0x13
        # 0x00 0x0D 0x00 0x10 0x00 0x0F 0x00 0x0D 0x00 0x12 0x00 0x0E
        # 0x00 0x2D 0x00 0x00
        # 0x00 0x33 0x00 0x00
        # 0x00 0x18
        # 0x00 0x7D 0x00 0x31
        # 0x02 0x30 0x02 0x30
        # 0x00 0x89 0x00 0x89
        # 0x00 0x24
        # 0x00 0x00 0x00 0x03
        # 0x00 0x00 0xCA 0xC0
        # 0x00 0x00 0x08 0xD7
        # 0x00 0x02 0xEB 0x55

        # 0x00 0x58 0x00 0x1F 0xE4 0xBA 0xBA 0xE9 0xA1 0x9E 0x00 0xE5 0xA5 0xB3 0xE6 0x80 0xA7 0x00 0xE8 0xB3 0xA2 0xE8 0x80 0x85 0x00 0xE8 0x8B 0xB1 0xE9 0x9B 0x84 0x00 0xE5 0x8D 0x81 0xE6 0x96 0xB9 0xE6 0xB3 0x95 0xE7 0x95 0x8C 0x20 0x35 0x39 0x00
        # 0x00 0x00 0x00 0x13 0x00 0x23 0x00 0x24 0x00 0x2B 0x00 0x24 0x00 0x42 0x00 0x24 0x00 0x26 0x00 0x28 0x00 0x00 0x00 0x18 0x00 0x00 0x00 0x65 0x00 0xDB 0x00 0xFC 0x03 0x08 0x03 0x08 0x03 0xBC 0x03 0xBC 0x00 0x7E 0x00 0x00 0x00 0x03 0x00 0x01 0xB8 0x35 0x0F 0xF5 0x97 0x8A 0x00 0x01 0xDF 0x26

        # 0x00 0x58 0x00 0x1F 0xE4 0xBA 0xBA 0xE9 0xA1 0x9E 0x00 0xE5 0xA5 0xB3 0xE6 0x80 0xA7 0x00 0xE8 0xB3 0xA2 0xE8 0x80 0x85 0x00 0xE8 0x8B 0xB1 0xE9 0x9B 0x84 0x00 0xE5 0x8D 0x81 0xE6 0x96 0xB9 0xE6 0xB3 0x95 0xE7 0x95 0x8C 0x20 0x35 0x39 0x00
        # 0x00 0x00 0x00 0x13 0x00 0x23 0x00 0x24 0x00 0x2B 0x00 0x24 0x00 0x42 0x00 0x24 0x00 0x26 0x00 0x28 0x00 0x00 0x00 0x18 0x00 0x00 0x00 0x65 0x00 0xDB 0x00 0xFC 0x03 0x08 0x03 0x08 0x03 0xBC 0x03 0xBC 0x00 0x7E 0x00 0x00 0x00 0x03 0x00 0x01 0xB8 0x35 0x0F 0xF5 0x97 0x8A 0x00 0x01 0xDF 0x26

        if data is None or len(data) == 0:
            self.unknown1 = bytearray()
            self.unknown2 = bytearray()
            self.unknown3 = bytearray()
            return

        struct = [
            ['x', 2],
            ['y', 2],
            ['race', -1],
            ['gender', -1],
            ['class_str', -1],
            ['stage', -1],
            ['kindgom', -1],
            ['unknown1', 4, 'bytes'],
            ['level', 2],
            ['str', 2],
            ['dex', 2],
            ['con', 2],
            ['int', 2],
            ['sta', 2],
            ['kar', 2],
            ['damage', 2],
            ['damage_left', 2],
            ['weapon_class', 2],
            ['weapon_class_left', 2],
            ['armor', 2],
            ['load_max', 2],
            ['load', 2],
            ['hp_max', 2],
            ['hp', 2],
            ['mp_max', 2],
            ['mp', 2],
            ['defense_bonus', 2],
            ['unknown2', 2, 'bytes'],
            ['unknown3', 2, 'bytes'],
            ['gold', 4],
            ['exp', 4],
            ['online_times', 4],
        ]

        index = 0
        for attr in struct:
            if attr[1] > -1:
                if len(attr) == 2:
                    setattr(self, attr[0], iKingUtils.hex2int(data[index:index + attr[1]]))
                    index += attr[1]
                else:
                    setattr(self, attr[0], data[index:index + attr[1]])
                    index += attr[1]
            else:
                (tmp, tn) = iKingUtils.export_string(data, index)
                setattr(self, attr[0], tmp)
                index = tn
        if len(self.kindgom) > 0 and ' ' in self.kindgom:
            (self.kindgom, self.kindgom_icon) = self.kindgom.split(' ')
        else:
            self.kindgom_icon = '0'

        self.key = "%d_%d" % (self.x, self.y)

    def print_sc(self):
        print self.get_sc()

    def format_online_times(self):
        # 1H = 3600
        # 1D = 24 * 3600 = 86400
        hours = int(self.online_times / 3600)
        days = int(hours / 24)
        hours = hours - days * 24
        seconds = int(self.online_times % 3600)
        minutes = int(seconds / 60)
        seconds = seconds - minutes * 60
        return "%d 天 %d 小时 %d 天 %d 秒" % (days, hours, minutes, seconds)

    def format_ages(self):
        # 1H = 3600
        # 1D = 24 * 3600 = 86400
        months = int(self.online_times / 0x3840)
        year = int(months / 0x0C)
        month = months - year * 0x0C
        return "%d岁%d月" % (year + 0x0F, month)

    def convert_level(self):
        num = ['十', '一', '二', '三', '四', '五', '六', '七', '八', '九', '十']
        if self.level <= 10:
            return num[self.level]
        else:
            f = int(self.level / 10)
            s = self.level - f * 10
            return '%s十%s' % (num[f] if f >= 2 else '', '' if s == 0 else num[s])

    def get_sc(self):
        s = ""
        s += "【 %s 】%s\n" % (self.class_str, self.fullname())
        kindgom = self.kindgom if self.kindgom != '無國籍' else ''
        s += " 你是一位%s第%s级的%s%s%s%s。\n\n" % (kindgom, self.convert_level(), self.race, self.gender, self.stage, self.class_str)
        s += " 力量﹕[%d]智慧﹕[%d]敏捷﹕[%d]\n" % (self.str, self.int, self.dex)
        s += " 毅力﹕[%d]体质﹕[%d]运气﹕[%d]\n\n" % (self.sta, self.con, self.kar)
        if len(self.buff_list) > 0:
            s += " 身体状况: %s\n\n" % (", ".join(map(lambda b: Buff.name(b), self.buff_list)))
        s += " <体力>  %d/ %d <法力>  %d/ %d\n\n" % (self.hp, self.hp_max, self.mp, self.mp_max)
        s += " 右手武器等级  %d     伤害力  %d\n\n" % (self.weapon_class, self.damage)
        s += " 防御能力等级  %d     额外防御力  %d 战斗经验 %d\n\n" % (self.armor, self.defense_bonus, self.exp)
        s += " 身上带著 %s 枚金币\n\n" % (self.gold)
        s += " 上线时数: %s。\n\n" % (self.format_online_times())
        s += " 角色年龄: %s。\n\n" % (self.format_ages())
        return s

    def update(self, data):
        pass


class ItemType:
    TYPE = {
        0x02: "项链",
        0x03: "衣服",
        0x04: "披风",
        0x05: "手套",
        0x06: "戒指",
        0x07: "帽子",
        0x08: "盾牌",
        0x09: "鞋子",
        0x0A: "单手剑",
        0x0B: "双手剑",
        0x0C: "单手刀",
        0x0D: "双手刀",
        0x0E: "单手斧",
        0x0F: "双手斧",
        0x10: "匕首",
        0x11: "单手锤",
        0x12: "双手锤",
        0x13: "长矛",
        0x14: "法杖",
        0x15: "魔棒",
        0x16: "飞镖",
        0x17: "弓",
        0x18: "十字弓",
        0x19: "枪",
        0x1A: "乐器",
        0x1F: "杂物",
        0x23: "钱包",
        0x3C: "可点击物体",
        0x3D: "尸体",
        0x3E: "腐烂的尸体",
        0x3F: "枯干的尸体",
    }

    @staticmethod
    def type(type_):
        if type_ in ItemType.TYPE:
            return ItemType.TYPE[type_]
        else:
            return "0x%.2X" % type_


class iKingGroundItem(iKingBaseMod):
    def parse(self, data):
        # item appear
        # 00 3D X
        # 00 66 Y
        # E6 96 B0 E6 89 8B E5 86 92 E9 9A AA E8 80 85 E7 9A 84 E5 B1 8D E9 AB 94 00 Name
        # 63 6F 72 70 73 65 00 ID
        # 00 00 20 3D
        self.data = data

        self.x = iKingUtils.hex2int(data[0:2])
        self.y = iKingUtils.hex2int(data[2:4])

        (self.name, tn) = iKingUtils.export_string(data, 4)
        (self.id, ti) = iKingUtils.export_string(data, tn)
        self.unknown = data[ti:ti + 1]
        self.item_id = iKingUtils.hex2int(data[ti + 1:ti + 3])
        self.item_type = iKingUtils.hex2int(data[-1:])

        self.key = "%d_%d" % (self.x, self.y)

    def check_pos(self, x=None, y=None, pos=None):
        if pos is not None:
            return self.x == pos.x and self.y == pos.y

        return self.x == x and self.y == y

    def print_debug(self, type_='0008', addInfo='appear'):
        print self.desc(type_, addInfo)

    def desc(self, type_='0008', addInfo='appear'):
        s = "%s     \titem %.9s: %s(%s) @ [%d,%d] [0x%.2X,0x%.2X]: %s(%d) " % (type_, addInfo, self.name, self.id, self.x, self.y, self.x, self.y, ItemType.type(self.item_type), self.item_id)
        return iKingUtils.dump_bytearray(self.unknown, s, ret_full=True)

    def update(self, data):
        pass


class iKingPlayerItem(iKingBaseMod):
    def parse(self, data):
        # user item
        # type_000B(10):
        # E7 B2 97 E5 B8 83 E9 9E 8B 00 Name(粗布鞋)
        # 10 equipd(==0x10)
        # 00 10 09 00 1F
        (self.name, tn) = iKingUtils.export_string(data)
        self.equip = data[tn] == 0x10
        self.item_id = data[tn + 1: tn + 3]
        self.item_type = iKingUtils.hex2int(data[tn + 3: tn + 4])
        self.current_load = iKingUtils.hex2int(data[-2:])

    def change_status(self, data):
        self.equip = data[0] == 0x10
        self.item_id = data[1:3]
        self.item_type = iKingUtils.hex2int(data[3:4])

    def print_debug(self, type_='000B', addInfo='get'):
        self.desc(type_, addInfo)

    def desc(self, type_='000B', addInfo='get'):
        s = "%s     \titem %.6s: %s%s %s load->%d " % (type_, addInfo, '*' if self.equip else ' ', self.name, ItemType.type(self.item_type), self.current_load)
        return iKingUtils.dump_bytearray(self.item_id, s, ret_full=True)

    def update(self, data):
        pass


class iKingSkill(iKingBaseMod):
    def parse(self, data):
        # user skill
        # type_000B(10): 77 65 61 70 6F 6E 5F 63 6C 61 73 73 00 00 07
        (self.name, tn) = iKingUtils.export_string(data)
        self.level = data[tn]
        self.unknown = data[-1:]

    def print_debug(self, type_, addInfo=''):
        pass

    def update(self, data):
        pass


class iKingSpell(iKingBaseMod):
    def parse(self, data):
        # user spell
        # type_000B(10): 77 65 61 70 6F 6E 5F 63 6C 61 73 73 00 00 07
        (self.name, tn) = iKingUtils.export_string(data)
        self.level = data[tn]
        self.unknown = data[-1:]

    def print_debug(self, type_, addInfo=''):
        pass

    def update(self, data):
        pass


class iKingDescription(iKingBaseMod):
    def parse(self, data):
        # user spell
        # type_000B(10): 77 65 61 70 6F 6E 5F 63 6C 61 73 73 00 00 07
        (self.first, tn) = iKingUtils.export_string(data)
        self.unknown = data[tn:(tn + 4)]
        (self.second, tn) = iKingUtils.export_string(data, tn + 4)

    def print_debug(self, type_, addInfo=''):
        pass

    def update(self, data):
        pass
