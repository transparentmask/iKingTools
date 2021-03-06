#!/usr/bin/env python
# -*- encoding: utf-8 -*-
from iking_utils import iKingUtils
from iking_data import *
from iking_map import *
from iking_magic import *
from iking_emotions import *
from collections import deque
from abc import ABCMeta, abstractmethod
import logging
import time
import traceback


class SendType:
    Version = [0x90, 0x05]
    Account = [0x90, 0x00]
    Server = [0x90, 0x06]
    Player = [0x90, 0x02]
    LOGIN_UNKNOWN1 = [0x90, 0x04]
    CreatePlayer = [0x90, 0x03]
    Command = [0x80, 0x03]
    Give = [0x80, 0x04]
    Go = [0x80, 0x05]
    Get = [0x80, 0x06]
    Kill = [0x80, 0x07]
    UseItem = [0x80, 0x08]
    Click = [0x80, 0x09]
    Run = [0x80, 0x0B]
    UNKNOWN1 = [0x80, 0x0C]
    Door = [0x80, 0x0D]
    UNKNOWN2 = [0x80, 0x0E]
    MenuOption = [0x80, 0x0F]
    IntitalFeedback = [0x80, 0x11]
    # 可能有上马, 铺地, 造房子, 拆房子


class ActionStep:
    Empty = 0x00
    CheckVersion = 0x01
    LoginAccount = 0x02
    LoginServer = 0x03
    LoginPlayer = 0x04
    SendCommand = 0x05
    SendClick = 0x06
    SendGo = 0x07
    SendRun = 0x08
    SendKill = 0x09
    SendGet = 0x0A
    SendLook = 0x0B
    SendMenuOption = 0x0C
    SendInitialFeedback = 0x0D
    MobAppear = 0x20
    MobMove = 0x21
    PlayerMove = 0x22
    ItemAppear = 0x30
    ItemDisappear = 0x31
    PlayerItemAppear = 0x40
    PlayerItemDisappear = 0x41
    UpdateStatus = 0xA0
    EnvironmentChange = 0xE0
    ShowDescription = 0xFE
    ShowInfo = 0xFF


class iKingPackageCaller(object):
    __metaclass__ = ABCMeta

    # def __init__(self, data=None):
    #     self.data = data
    #     self.parse()

    # @abstractmethod
    # def parse(self):
    #     pass

    # @abstractmethod
    # def print_debug(self, type_, addInfo=''):
    #     pass

    # @abstractmethod
    # def update(self):
    #     pass

    @abstractmethod
    def beforePackProcess(caller, pack):
        pass

    @abstractmethod
    def doPackProcess(caller, pack, dictionary):
        pass

    @abstractmethod
    def afterPackProcess(caller, pack):
        pass


class iKingPackage:
    def __init__(self, caller=None):
        self.caller = caller

        self.mobs_list = []
        self.items_list = []
        self.player_items_list = []
        self.player = None
        self.player_id = ""
        self.cur_map = MapInfo()
        self.packs = deque()

        self.processing = True
        self.process_thread = threading.Thread(target=self.process_loop, name="PrecessThread")
        self.process_thread.setDaemon(True)
        self.process_thread.start()

    def do_7001(self, type_, pack):
        self.do_default(type_, pack)
        data = pack['data']
        if data[1] == 0x02:
            logging.getLogger("iking_proxy").info("**** 密码错误")
        elif data[1] == 0x03:
            logging.getLogger("iking_proxy").info("**** 世界准备中")
        elif data[1] == 0x64:
            new_ip = "%d.%d.%d.%d" % (data[2], data[3], data[4], data[5])
            new_port = iKingUtils.hex2int(data[-2:])
            logging.getLogger("iking_proxy").info("**** new ip:port = %s:%d" % (new_ip, new_port))
        else:
            logging.getLogger("iking_proxy").info("**** 剩余点数: %d" % (iKingUtils.hex2int(data[2:6])))
            logging.getLogger("iking_proxy").info("**** 可创建人物: %d" % (data[-1]))

        # kk_type_7001(0x10): 0x00 0x01 0x70 0x01 0x00 0x00 0x00 0x08 0x00 0x02 0x00 0x00 0x00 0x00 0x00 0x00 密码错误
        # kk_type_7001(0x10): 0x00 0x01 0x70 0x01 0x00 0x00 0x00 0x08 0x00 0x03 0x00 0x00 0x00 0x00 0x00 0x00 世界准备中
        # kk_type_7001(0x10): 0x00 0x01 0x70 0x01 0x00 0x00 0x00 0x08 0x00 0x00 0x00 0x00 0x00 0x00 0xFF 0x00
        # kk_type_7001(0x10): 0x00 0x01 0x70 0x01 0x00 0x00 0x00 0x08 0x00 0x00 0x00 0x00 0x00 0x58 0xFF 0x00 紫晶88
        # kk_type_7001(0x10): 0x00 0x01 0x70 0x01 0x00 0x00 0x00 0x08 0x00 0x00 0x00 0x00 0x00 0x00 0xFF 0x01 可创建人物1
        # kk_type_7001(0x10): 0x00 0x01 0x70 0x01 0x00 0x00 0x00 0x08 0x00 0x64 0x70 0x79 0x6D 0xA0 0x10 0xE1 变更ip: 112.121.109.160

    def do_7002(self, type_, pack):
        self.do_default(type_, pack)
        players = pack['data'].decode('utf-8').split(',')
        players = map(lambda p: p.strip('\x00').strip(), players)
        logging.getLogger("iking_proxy").info(iKingUtils.dump_string(type_, ",".join(players), ret=True))
        self.player = iKingPlayer()
        self.player.id = self.player_id = players[0]

    def do_7003(self, type_, pack):
        self.do_default(type_, pack, highlight=True)

        data = pack['data']
        if data[1] == 0x00:
            pass
            # print "**** Force close connection!"
        if data[1] == 0x06:
            logging.getLogger("iking_proxy").info("**** 没有可用人物(创建失败)")

    # def do_7006(self, type_, pack):
    #     pass

    def do_7009(self, type_, pack):
        self.do_default(type_, pack)
        server_infos = pack['data'].decode('utf-8').split('\t')
        logging.getLogger("iking_proxy").info(iKingUtils.dump_string(type_, ",".join(server_infos), ret=True))

    def do_0001(self, type_, pack):
        data = pack['data']
        logging.getLogger("iking_proxy").info(iKingUtils.dump_string(type_, str(data).decode('utf-8'), ret=True))

    def do_0003(self, type_, pack):
        # player move 0x00 0x01 0x00 0x03 0x00 0x00 0x00 0x55 0x07 0x00 0x00 0x00 0x14 0x00 0x00 0x0E 0x14 0x00 0x00 0x0E 0x10 0x00 0x00 0x0E 0x5C 0x00 0x00 0x0E 0x54 0x00 0x00 0x0E 0x34 0x00 0x00 0x0E 0x20 0x00 0x00 0x0E 0x2C 0x00 0x00 0x0E 0x34 0x00 0x00 0x8E 0x00 0x00 0x00 0x8E 0x4C 0x00 0x00 0x8E 0x54 0x00 0x00 0x0E 0x1C 0x00 0x00 0x0E 0x30 0x00 0x00 0x0E 0x34 0x00 0x00 0x81 0x20 0x00 0x00 0x7B 0x5C 0x00 0x00 0x22 0x20 0x00 0x00 0x26 0x5C 0x00 0x00 0x02 0x04 0x00 0x00 0x02 0x04
        # self.do_default(type_, pack, highlight=True)
        data = pack['data']

        # ts = int(time.time() * 1000)
        # cache = 'maps/data/%d_0003.dat' % (ts)
        # i = 1
        # while os.path.exists(cache):
        #     cache = 'maps/data/%d_0003_%.2d.dat' % (ts, i)
        #     i += 1
        # with open(cache, "wb") as file:
        #     file.write(data)
        #     file.close()

        self.cur_map.moveon_map(data)
        self.cur_map.save_map()
        self.player.move(self.cur_map.map_pos[0], self.cur_map.map_pos[1])
        outdoor = self.cur_map.is_out_door()
        logging.getLogger("iking_proxy").info('%s move to %s %s %s' % (self.player.fullname(), self.player.pos(), self.player.pos(True), outdoor[1]))

    def do_0004(self, type_, pack):
        data = pack['data']
        pos = Pos(pos_data=data[0:4])
        direction = data[4]
        for mob in self.mobs_list:
            if mob.check_pos(pos=pos):
                pos.move(direction)
                mob.move(pos.x, pos.y)
                logging.getLogger("iking_proxy").info('%s move to %s %s' % (mob.fullname(), mob.pos(), mob.pos(True)))
                break

    def do_0005(self, type_, pack):
        data = pack['data']
        mob = iKingMob(data)
        if str(mob.id) == str(self.player_id):
            self.player.parse(data)
            mob = self.player
        else:
            self.mobs_list.append(mob)
        logging.getLogger("iking_proxy").info(mob.desc())

    def do_0006(self, type_, pack):
        # map 0x00 0x01 0x00 0x06 0x00 0x00 0x03 0x8C 0x00 0x53 0x00 0x99 0x6E 0x65 0x77 0x62 0x69 0x65 0x33 0x20 0x76 0x61 0x63 0x68 0x65 0x6C 0x6C 0x00 0x00 0x64 0x00 0xC8 0x00 0x00 0x00 0xDC 0x00 0x00 0x87 0x3C 0x00 0x00 0x0D 0x28 0x00 0x00 0x0D 0x31 0x00 0x00 0x0D 0x0D 0x00 0x00 0x0D 0x51 0x00 0x00 0x86 0x50 0x00 0x00 0x0E 0x5C 0x00 0x00 0x0E 0x1C 0x00 0x00 0x0E 0x50 0x00 0x00 0x0E 0x5C 0x00 0x00 0x0E 0x2C 0x00 0x00 0x0D 0x04 0x00 0x00 0x0D 0x08 0x00 0x00 0x0D 0x1D 0x00 0xC3 0x0D 0x20 0x00 0xC4 0x0D 0x35 0x00 0x00 0x86 0x30 0x00 0x00 0x0E 0x54 0x00 0x00 0x0E 0x58 0x00 0x00 0x0E 0x5C 0x00 0x00 0x0E 0x3C 0x00 0x00 0x0E 0x34 0x00 0x00 0x0D 0x44 0x00 0x00 0x0D 0x08 0x00 0x00 0x0D 0x41 0x00 0x00 0x0D 0x01 0x00 0x00 0x0D 0x05 0x00 0x00 0x86 0x10 0x00 0x00 0x0E 0x34 0x00 0x00 0x0E 0x58 0x00 0x00 0x0E 0x5C 0x00 0x00 0x0E 0x38 0x00 0x00 0x0E 0x5C 0x00 0x00 0x0D 0x40 0x00 0x00 0x0D 0x30 0x00 0x00 0x0D 0x08 0x00 0x00 0x0D 0x0C 0x00 0x00 0x0D 0x20 0x00 0x00 0x86 0x10 0x00 0x00 0x0E 0x20 0x00 0x00 0x0E 0x08 0x00 0x00 0x0E 0x34 0x00 0x00 0x0E 0x18 0x00 0x00 0x0E 0x1C 0x00 0x00 0x86 0x18 0x00 0x00 0x86 0x18 0x00 0x00 0x86 0x18 0x00 0x00 0x86 0x18 0x00 0x00 0x86 0x38 0x00 0x00 0x86 0x5C 0x00 0x00 0x0E 0x2C 0x00 0x00 0x0E 0x54 0x00 0x00 0x8E 0x00 0x00 0x00 0x8E 0x04 0x00 0x00 0x8E 0x48 0x00 0x00 0x0E 0x54 0x00 0x00 0x0E 0x14 0x00 0x00 0x0E 0x00 0x00 0x00 0x0E 0x24 0x00 0x00 0x0E 0x34 0x00 0x00 0x0E 0x00 0x00 0x00 0x0E 0x34 0x00 0x00 0x8E 0x00 0x00 0x00 0x8F 0x1C 0x00 0x00 0x11 0x45 0x00 0x00 0x8E 0x51 0x00 0x00 0x0E 0x3C 0x00 0x00 0x0E 0x10 0x00 0x00 0x0E 0x20 0x00 0x00 0x0E 0x40 0x00 0x00 0x0E 0x34 0x00 0x00 0x0E 0x40 0x00 0x00 0x8E 0x00 0x00 0x00 0x8F 0x1C 0x00 0x00 0x11 0x01 0x00 0x00 0x11 0x05 0x00 0x00 0x8E 0x31 0x00 0x00 0x0E 0x24 0x00 0x00 0x0E 0x00 0x00 0x00 0x0E 0x44 0x00 0x00 0x0E 0x48 0x00 0x00 0x0E 0x0C 0x00 0x00 0x0E 0x0C 0x00 0x00 0x8E 0x4C 0x00 0x00 0x11 0x4D 0x00 0x00 0x11 0x2D 0x00 0x00 0x11 0x49 0x00 0x00 0x8E 0x31 0x00 0x00 0x0E 0x24 0x00 0x00 0x0E 0x18 0x00 0x00 0x0E 0x18 0x00 0x00 0x0E 0x18 0x00 0x00 0x0E 0x58 0x00 0x00 0x0E 0x34 0x00 0x00 0x8E 0x54 0x00 0x00 0x8E 0x19 0x00 0x00 0x8E 0x59 0x00 0x00 0x8E 0x19 0x00 0x00 0x8E 0x3D 0x00 0x00 0x87 0x18 0x00 0x00 0x87 0x18 0x00 0x00 0x87 0x18 0x00 0x00 0x86 0x08 0x00 0x00 0x0E 0x54 0x00 0x00 0x0E 0x18 0x00 0x00 0x0E 0x1C 0x00 0x00 0x0E 0x0C 0x00 0x00 0x0E 0x50 0x00 0x00 0x81 0x40 0x00 0x00 0x7B 0x18 0x00 0x00 0x0D 0x1C 0x00 0x00 0x0D 0x54 0x00 0x00 0x0D 0x18 0x00 0x00 0x86 0x10 0x00 0x00 0x0E 0x58 0x00 0x00 0x0E 0x1C 0x00 0x00 0x0E 0x30 0x00 0x00 0x0E 0x14 0x00 0x00 0x81 0x40 0x00 0x00 0x7B 0x5C 0x00 0x00 0x22 0x40 0x00 0x00 0x0D 0x10 0x16 0x49 0x0D 0x29 0x00 0x00 0x0D 0x48 0x00 0x00 0x86 0x50 0x00 0x00 0x0E 0x58 0x00 0x00 0x0E 0x3C 0x00 0x00 0x0E 0x34 0x00 0x00 0x81 0x00 0x00 0x00 0x7B 0x1C 0x00 0x00 0x22 0x20 0x00 0x00 0x26 0x5C 0x00 0x00 0x0D 0x1C 0x00 0x00 0x0D 0x30 0x00 0x00 0x87 0x20 0x00 0x00 0x86 0x1C 0x00 0x00 0x0E 0x5C 0x00 0x00 0x0E 0x5C 0x00 0x00 0x81 0x20 0x00 0x00 0x7B 0x5C 0x00 0x00 0x22 0x00 0x00 0x00 0x26 0x3C 0x00 0x00 0x02 0x34 0x00 0x00 0x86 0x18 0x00 0x00 0x86 0x58 0x00 0x00 0x86 0x1C 0x00 0x00 0x0E 0x24 0x00 0x00 0x0E 0x34 0x00 0x00 0x81 0x20 0x00 0x00 0x7B 0x5C 0x00 0x00 0x22 0x00 0x00 0x00 0x26 0x1C 0x00 0x00 0x02 0x54 0x00 0x00 0x02 0x40 0x00 0x00 0x0E 0x54 0x00 0x00 0x0E 0x50 0x00 0x00 0x0E 0x4C 0x00 0x00 0x0E 0x34 0x00 0x00 0x81 0x40 0x00 0x00 0x7B 0x5C 0x00 0x00 0x22 0x20 0x00 0x00 0x26 0x3C 0x00 0x00 0x02 0x08 0x00 0x00 0x02 0x08 0x00 0x00 0x02 0x40 0x00 0x00 0x7B 0x38 0x00 0x00 0x7B 0x38 0x00 0x00 0x7B 0x38 0x00 0x00 0x7B 0x18 0x00 0x00 0x7B 0x3C 0x00 0x00 0x22 0x00 0x00 0x00 0x26 0x5C 0x00 0x00 0x02 0x48 0x00 0x00 0x02 0x08 0x00 0x00 0x02 0x30 0x00 0x00 0x02 0x20 0x00 0x00 0x06 0x00 0x00 0x00 0x06 0x24 0x00 0x00 0x22 0x00 0x00 0x00 0x22 0x44 0x00 0x00 0x22 0x44 0x00 0x00 0x26 0x5C 0x00 0x00 0x02 0x04 0x00 0x00 0x02 0x28 0x00 0x00 0x02 0x10 0x00 0x00 0x02 0x5C 0x00 0x00 0x02 0x2C 0x00 0x00 0x22 0x44 0x00 0x00 0x22 0x24 0x00 0x00 0x26 0x3C 0x00 0x00 0x02 0x20 0x00 0x00 0x02 0x44 0x00 0x00 0x02 0x48 0x00 0x00 0x02 0x04 0x00 0x00 0x02 0x08 0x00 0x00 0x02 0x1C 0x00 0x00 0x02 0x54 0x00 0x00 0x02 0x00 0x00 0x00 0x24 0x24 0x00 0x00 0x24 0x08 0x00 0x00 0x02 0x14 0x00 0x00 0x02 0x4C 0x00 0x00 0x02 0x54 0x00 0x00 0x02 0x10 0x00 0x00 0x02 0x48 0x00 0x00 0x02 0x30 0x00 0x00 0x02 0x1C 0x00 0x00 0x02 0x1C 0x00 0x00 0x02 0x4C 0x00 0x00 0x03 0x30 0x00 0x00 0x24 0x10 0x00 0x00 0x02 0x38 0x00 0x00 0x02 0x54 0x00 0x00 0x02 0x18 0x00 0x00 0x02 0x1C 0x00 0x00 0x02 0x38 0x00 0x00 0x02 0x3C 0x00 0x00 0x02 0x10 0x00 0x00 0x02 0x38 0x00 0x00 0x02 0x34
        # self.do_default(type_, pack, highlight=True)
        data = pack['data']

        # ts = int(time.time() * 1000)
        # cache = 'maps/data/%d_0006.dat' % (ts)
        # i = 1
        # while os.path.exists(cache):
        #     cache = 'maps/data/%d_0006_%.2d.dat' % (ts, i)
        #     i += 1
        # with open(cache, "wb") as file:
        #     file.write(data)
        #     file.close()

        self.cur_map.init_map(data)
        self.cur_map.save_map()

    def do_0007(self, type_, pack):
        # kk_type_0007(0x0C): 0x00 0x01 0x00 0x07 0x00 0x00 0x00 0x04 0x00 0x56 0x00 0x8B
        data = pack['data']
        pos = Pos(pos_data=data[0:4])
        # key = "%d_%d" % (x, y)
        for mob in self.mobs_list:
            if mob.check_pos(pos=pos):
                self.mobs_list.remove(mob)
                logging.getLogger("iking_proxy").info("mob %s @ %s %s disappear" % (mob.fullname(), mob.pos(), mob.pos(True)))
                break

    def do_0008(self, type_, pack):
        self.do_default(type_, pack)
        data = pack['data']
        item = iKingGroundItem(data)
        self.items_list.append(item)
        if item.item_type == 0x3C:
            self.cur_map.add_clickable_item(item)
        logging.getLogger("iking_proxy").info(item.desc())

    def do_0009(self, type_, pack):
        data = pack['data']
        pos = Pos(pos_data=data[0:4])
        for item in self.items_list:
            if item.check_pos(pos=pos):
                logging.getLogger("iking_proxy").info(item.desc(type_='0009', addInfo='disappear'))
                self.items_list.remove(item)
                break

    def do_000A(self, type_, pack):
        self.do_default(type_, pack)
        data = pack['data']
        self.player.parse_0A(data)
        logging.getLogger("iking_proxy").info(self.player.get_sc())

    def do_000B(self, type_, pack):
        data = pack['data']
        item = iKingPlayerItem(data)
        self.player_items_list.insert(0, item)
        logging.getLogger("iking_proxy").info(item.desc())

    def do_000C(self, type_, pack):
        data = pack['data']
        item_index = iKingUtils.hex2int(data[0:2])
        if item_index < len(self.player_items_list):
            item = self.player_items_list[item_index]
            logging.getLogger("iking_proxy").info(item.desc(type_='000C', addInfo='disappear'))
            del self.player_items_list[item_index]

    def do_000E(self, type_, pack):
        (name, tn) = iKingUtils.export_string(pack['data'])
        value = iKingUtils.hex2int(pack['data'][tn:])
        logging.getLogger("iking_proxy").info(iKingUtils.dump_string(type_, "%s: %d" % (name, value), ret=True))

    def do_000F(self, type_, pack):
        (name, tn) = iKingUtils.export_string(pack['data'])
        value = iKingUtils.hex2int(pack['data'][tn:])
        logging.getLogger("iking_proxy").info(iKingUtils.dump_string(type_, "%s: %d" % (name, value), ret=True))

    def do_0010(self, type_, pack):
        data = pack['data']
        index = iKingUtils.hex2int(data[0:2])
        if index < len(self.player_items_list):
            item = self.player_items_list[index]
            item.change_status(data[2:])
            logging.getLogger("iking_proxy").info(item.desc('0010', 'change'))
        else:
            self.do_default(type_, pack, highlight=True, special="Wrong")

    def do_0011(self, type_, pack):
        desc = iKingDescription(pack['data'])
        logging.getLogger("iking_proxy").info(iKingUtils.dump_string(type_, "%s(%s): %s" % (desc.first, iKingUtils.dump_bytearray(desc.unknown, ret=True), desc.second), ret=True))

    def do_0012(self, type_, pack):
        data = pack['data']
        subtype = data[0]
        if subtype > 0 and subtype <= 0x0C:
            channel = ""
            content = str(data[1:])
            if subtype == 0x01:
                channel = "交谈"
            elif subtype == 0x02:
                channel = "闲聊"
            elif subtype == 0x03:
                channel = "谣言"
            elif subtype == 0x04:
                channel = "拍卖"
            elif subtype == 0x05:
                channel = "组队"
            elif subtype == 0x06:
                channel = "国家"
            elif subtype == 0x07:
                channel = "组织"
            elif subtype == 0x08:
                channel = "系统"
            elif subtype == 0x6D:
                channel = "职业"
            elif subtype == 0x6E:
                channel = "英雄"
            elif subtype == 0x6F:
                channel = "自由"
            elif subtype == 0x70:
                channel = "广告"
            logging.getLogger("iking_proxy").info('%s-%s(%.2X)\t%s' % (pack['type'], channel, subtype, content))
        elif subtype == 0x0B:
            # Click Target
            # 0x00 0x01 0x00 0x12 0x00 0x00 0x00 0x2C 0x0B 0xE9 0xAB 0x94 0xE8 0xB3 0xAA 0x09 0x32 0x34 0x38 0x38 0x33 0x32 0x0A 0xE6 0xAF 0x85 0xE5 0x8A 0x9B 0x09 0x31 0x34 0x34 0x30 0x30 0x30 0x0A 0xE9 0x81 0x8B 0xE6 0xB0 0xA3 0x09 0x31 0x34 0x34 0x30 0x30 0x30 0x0A 0x00
            content = str(data[1:])
            logging.getLogger("iking_proxy").info('%s-0x%.2X\tClick Target\n%s' % (pack['type'], subtype, content))
        elif subtype == 0x0C:
            # Target update
            # 0x00 0x01 0x00 0x12 0x00 0x00 0x00 0x17 0x0C 0xE9 0xAB 0x94 0xE8 0xB3 0xAA 0x0A 0xE9 0xAB 0x94 0xE8 0xB3 0xAA 0x09 0x32 0x39 0x38 0x35 0x39 0x38 0x0A 0x00
            content = str(data[1:])
            logging.getLogger("iking_proxy").info('%s-0x%.2X\tUpdate Target\n%s' % (pack['type'], subtype, content))
        elif subtype == 0x15 or subtype == 0x16 or subtype == 0x18 or subtype == 0x19 or subtype == 0x1B:
            # 0x15: 输入框/银行;
            # 0x16: 传送师/车夫/小贩/定位/get/r7存装备;
            # 0x18: set/会馆/finger/store;
            # 0x19: 单纯按钮;
            # 0x18: Finger
            # 0x1B: 时空门/auc/月神路标/地道入口/enter entrance/魔影任务中
            # 0x00 0x01 0x00 0x12 0x00 0x00 0x01 0xDD 0x18 0x30 0x0A 0xE9 0xA2 0xA8 0xE4 0xB8 0xAD 0xE5 0x82 0xB3 0xE4 0xBE 0x86 0xE4 0xBA 0x86 0xE7 0xAB 0x8A 0xE7 0xAB 0x8A 0xE7 0xA7 0x81 0xE8 0xAA 0x9E 0xEF 0xBC 0x8C 0xE4 0xBD 0xA0 0xE8 0x81 0xBD 0xE5 0x88 0xB0 0xE4 0xBA 0x86 0x2E 0x2E 0x2E 0x0A 0x0A 0xE4 0xBB 0x96 0xE6 0x9C 0x89 0xE6 0x96 0xB0 0xE7 0x9A 0x84 0xE4 0xBF 0xA1 0xE3 0x80 0x82 0x0A 0x0A 0x0A 0xE5 0x82 0xAD 0xE5 0x85 0xB5 0x3A 0x20 0xE5 0x8E 0x9F 0xE5 0xA7 0x8B 0xE5 0x9C 0x8B 0xE8 0x97 0x89 0x20 0xE9 0xBE 0x8D 0xE7 0x9C 0xA0 0xE5 0x9F 0x8E 0x28 0x7A 0x7A 0x7A 0x29 0x0A 0xE4 0xB8 0x8A 0xE7 0xB7 0x9A 0xE6 0x99 0x82 0xE6 0x95 0xB8 0x3A 0x20 0x31 0x35 0x20 0xE5 0xA4 0xA9 0x20 0x32 0x20 0xE5 0xB0 0x8F 0xE6 0x99 0x82 0x20 0x31 0x35 0x20 0xE5 0x88 0x86 0x20 0x32 0x38 0x20 0xE7 0xA7 0x92 0xE3 0x80 0x82 0x0A 0xE7 0x9B 0xAE 0xE5 0x89 0x8D 0xE8 0x81 0xB7 0xE6 0xA5 0xAD 0x3A 0x20 0xE5 0xA4 0xA7 0xE6 0xB3 0x95 0xE5 0xB8 0xAB 0x20 0x20 0x20 0x20 0x20 0x20 0x20 0x20 0x20 0x20 0x20 0x20 0x20 0x20 0x20 0x20 0x20 0x20 0x20 0x20 0x20 0xE7 0x9B 0xAE 0xE5 0x89 0x8D 0xE7 0xAD 0x89 0xE7 0xB4 0x9A 0x3A 0x20 0x3F 0x3F 0x0A 0xE6 0x89 0x80 0xE5 0xB1 0xAC 0xE7 0xB5 0x84 0xE7 0xB9 0x94 0x3A 0x20 0xE3 0x80 0x8E 0xE6 0x88 0x98 0xE2 0x98 0x85 0xE8 0xB4 0xA9 0xE3 0x80 0x8F 0x28 0x61 0x6B 0x69 0x6C 0x6C 0x29 0x20 0x20 0x20 0x20 0x20 0x20 0x20 0x20 0xE7 0xB5 0x84 0xE7 0xB9 0x94 0xE8 0x81 0xB7 0xE9 0x8A 0x9C 0x3A 0x20 0xE7 0x84 0xA1 0x0A 0xE6 0x89 0x80 0xE5 0xB1 0xAC 0xE5 0x9C 0x8B 0xE5 0xAE 0xB6 0x3A 0x20 0xE9 0x87 0x91 0xE9 0xA3 0x8E 0xE7 0xBB 0x86 0xE9 0x9B 0xA8 0xE6 0xA5 0xBC 0x28 0x70 0x6B 0x62 0x75 0x67 0x29 0x20 0x20 0x20 0x20 0x20 0x20 0x20 0x20 0xE8 0x81 0xB7 0x20 0x20 0x20 0x20 0xE9 0x8A 0x9C 0x3A 0x20 0xE8 0x8B 0xB1 0xE9 0x9B 0x84 0x0A 0xE6 0x80 0xA7 0x20 0x20 0x20 0x20 0xE5 0x88 0xA5 0x3A 0x20 0xE5 0xA5 0xB3 0xE6 0x80 0xA7 0x20 0x20 0x20 0x20 0x20 0x20 0x20 0x20 0x20 0x20 0x20 0x20 0x20 0x20 0x20 0x20 0x20 0x20 0x20 0x20 0x20 0x20 0x20 0x20 0xE9 0x85 0x8D 0x20 0x20 0x20 0x20 0xE5 0x81 0xB6 0x3A 0x20 0xE7 0x84 0xA1 0x0A 0xE8 0x8B 0xB1 0xE6 0x96 0x87 0xE4 0xBB 0xA3 0xE8 0x99 0x9F 0xEF 0xB9 0x95 0x6C 0x6F 0x76 0x65 0x70 0x6B 0x62 0x75 0x67 0x20 0x20 0x20 0x20 0x20 0x20 0x20 0x20 0x20 0x20 0x20 0x20 0x20 0x20 0x20 0x20 0x20 0x20 0x20 0x20 0x20 0xE5 0xA7 0x93 0x20 0x20 0x20 0x20 0xE5 0x90 0x8D 0xEF 0xB9 0x95 0x5E 0x5B 0x33 0x37 0x6D 0xE2 0x98 0x85 0xE7 0x99 0xBD 0xE6 0x84 0x81 0xE9 0xA3 0x9E 0xE2 0x98 0x85 0x00
            # 0x19: Dialog
            buttons = []
            if data[1] == 0x5C and data[2] == 0x6E:
                button_count = 0
            else:
                button_count = int(chr(data[1]))
            logging.getLogger("iking_proxy").info("button_count: " + str(button_count))
            tn = 3
            if button_count > 0:
                for i in range(button_count):
                    button = {}
                    (button['name'], tn) = iKingUtils.export_string(data, tn, terminator='\x0A')
                    (button['action'], tn) = iKingUtils.export_string(data, tn, terminator='\x0A')
                    buttons.append(button)
                buttons_str = "    ".join(map(lambda button: "%s(%s)" % (button['name'], button['action']), buttons))
            else:
                if subtype == 0x19:
                    tn = 4
                buttons_str = 'No Buttons'
            content = data[tn:]
            logging.getLogger("iking_proxy").info('%s-0x%.2X\tDialog:    %s\n%s' % (pack['type'], subtype, buttons_str, content))
        else:
            logging.getLogger("iking_proxy").info('%s-0x%.2X\t%s' % (pack['type'], pack['data'][0], str(pack['data'][1:]).decode('utf-8')))

    def do_0013(self, type_, pack):
        data = pack['data']
        (name, tn) = iKingUtils.export_string(data)
        logging.getLogger("iking_proxy").info(iKingUtils.dump_string(type_, "skill %s: %d(0x%.2X)" % (name, data[-1], data[-1]), ret=True))

    def do_0014(self, type_, pack):
        # '0014': iKingPackage.do_0014, action
        # 0x00 0x01 0x00 0x14 0x00 0x00 0x00 0x09 0x00 0x55(x) 0x00 0x8E(y) 0x00 0x00 0x00 0x07(action) 0xFF(direction)
        data = pack['data']
        pos = Pos(pos_data=data[0:4])
        data1 = data[4]
        data2 = data[5]
        data3 = iKingUtils.hex2int(bytearray(data[6:8]))
        data4 = data[7]
        data5 = data[8]

        if data3 == 0x0BB8:  # and data5 == 0x1B: 0x0A 0x0F
            logging.getLogger("iking_proxy").info(iKingUtils.dump_string(type_, "?? Login Finish ??", ret=True))
            return

        char = None
        if self.player.check_pos(pos=pos):
            char = "%s %s" % (self.player.fullname(), self.player.pos(True))
        else:
            for mob in self.mobs_list:
                if mob.check_pos(pos=pos):
                    char = "%s %s" % (mob.fullname(), mob.pos(True))
        if char is None:
            char = "[%d, %d]" % (pos.x, pos.y)

        if data1 == 0x01:
            action = "起身(恢复常态)"
            logging.getLogger("iking_proxy").info(iKingUtils.dump_bytearray(data[4:], "%s     \t%s %s (%s)" % (type_, char, action, iKingUtils.direction_desc(data5)), ret_full=True))
        elif data1 == 0x04:
            if data4 == 0x0A:
                action = "1: 0x04 被击中"
            else:
                action = "1: 0x04 未知 0x%.2X" % data4
            logging.getLogger("iking_proxy").info(iKingUtils.dump_bytearray(data[4:], "%s     \t%s %s (%s)" % (type_, char, action, iKingUtils.direction_desc(data5)), ret_full=True))
        elif data1 == 0x08:
            if data4 == 0x0A:
                action = "1: 0x08 被魔法击中"
            else:
                action = "1: 0x08 未知 0x%.2X" % data4
            logging.getLogger("iking_proxy").info(iKingUtils.dump_bytearray(data[4:], "%s     \t%s %s (%s)" % (type_, char, action, iKingUtils.direction_desc(data5)), ret_full=True))
        elif data3 < 0x0100:
            # action
            if data4 == 0x00:
                action = "起身(恢复常态)"
            elif data4 == 0x01:
                action = "攻击"
            elif data4 == 0x02:
                action = "丢东西"
            elif data4 == 0x03:
                action = "捡东西"
            elif data4 == 0x04:
                action = "给东西"
            elif data4 == 0x06:
                action = "装备武器"
            elif data4 == 0x07:
                action = "放下武器"
            elif data4 == 0x08:
                action = "穿装备"
            elif data4 == 0x09:
                action = "脱装备"
            elif data4 == 0x0F:
                action = "死亡"
            elif data4 == 0x12:
                action = "低头(冥想?)"
            elif data4 == 0x13 or data4 == 0x14 or data4 == 0x15 or data4 == 0x16:
                if data2 == 0x00:
                    action = "施法 0x%.2X" % data4
                else:
                    action = "施法(持续%d) 0x%.2X" % (data2, data4)
            else:
                action = "未知动作 0x%.2X" % data4
            logging.getLogger("iking_proxy").info(iKingUtils.dump_bytearray(data[4:], "%s     \t%s %s (%s)" % (type_, char, action, iKingUtils.direction_desc(data5)), ret_full=True))
        elif Emotion.isEmotion(data3):
            logging.getLogger("iking_proxy").info(iKingUtils.dump_bytearray(data[4:], "%s     \t%s emotion? %s (0x%.2X) (%s)" % (type_, char, Emotion.emotion(data3), data2, iKingUtils.direction_desc(data5)), ret_full=True))
        elif data3 == 0x07:
            logging.getLogger("iking_proxy").info(iKingUtils.dump_bytearray(data[4:], "%s     \t%s unknown action (appear?) (%s)" % (type_, char, iKingUtils.direction_desc(data5)), ret_full=True))

    def do_0015(self, type_, pack):
        # kk_type_0015(0x10): 0x00 0x01 0x00 0x15 0x00 0x00 0x00 0x08 0x00 0x22 0x00 0x2A 0x10 0x01 0x30 0x04
        data = pack['data']
        pos = Pos(pos_data=data[0:4])
        equip = data[4] == 0x10
        item_id = data[5:7]
        item_type = iKingUtils.hex2int(data[7:8])
        if self.player.check_pos(pos=pos):
            s = "%s     \t%s %s change eq: %s%s " % (type_, self.player.fullname(), self.player.pos(True), '*' if equip else ' ', ItemType.type(item_type))
            logging.getLogger("iking_proxy").info(iKingUtils.dump_bytearray(item_id, s, ret_full=True))
            return

        for mob in self.mobs_list:
            if mob.check_pos(pos=pos):
                s = "%s     \t%s %s change eq: %s%s " % (type_, mob.fullname(), mob.pos(True), '*' if equip else ' ', ItemType.type(item_type))
                logging.getLogger("iking_proxy").info(iKingUtils.dump_bytearray(item_id, s, ret_full=True))
                return

        s = "%s     \t[%d, %d] change eq: %s%s " % (type_, pos.x, pos.y, '*' if equip else ' ', ItemType.type(item_type))
        logging.getLogger("iking_proxy").info(iKingUtils.dump_bytearray(item_id, s, ret_full=True))

    def do_0018(self, type_, pack):
        data = pack['data']
        (name, tn) = iKingUtils.export_string(data)
        logging.getLogger("iking_proxy").info(iKingUtils.dump_string(type_, "spell %s: %d(0x%.2X)" % (name, data[-1], data[-1]), ret=True))

    def do_0019(self, type_, pack):
        # kk_type_0019(0x1C): 0x00 0x01 0x00 0x19 0x00 0x00 0x00 0x14
        # 0x00 0x00 0x00 0x04 0x00 0x3F 0x00 0x6D 0x00 0x00 0x14 0x20 0x00 0x44 0x00 0x6F 0x00 0x00 0x14 0x22
        # self.do_default(type_, pack, highlight=True)
        data = pack['data']

        # ts = int(time.time() * 1000)
        # cache = 'maps/data/%d_0019.dat' % (ts)
        # i = 1
        # while os.path.exists(cache):
        #     cache = 'maps/data/%d_0019_%.2d.dat' % (ts, i)
        #     i += 1
        # with open(cache, "wb") as file:
        #     file.write(data)
        #     file.close()

        self.cur_map.parse_addon_item(data)
        self.cur_map.save_map()

    # def do_001B(self, type_, pack):
    #     # kk_type_001B(0x14): 0x00 0x01 0x00 0x1B 0x00 0x00 0x00 0x0C 0x10 0x00 0x00 0x20 0x00 0x5C 0x00 0x86 0x00 0x00 0x00 0x01
    #     # kk_type_001B(0x14): 0x00 0x01 0x00 0x1B 0x00 0x00 0x00 0x0C 0x00 0x00 0x00 0x0F 0x00 0x58 0x00 0x82 0x00 0x00 0x00 0x01
    #     # kk_type_001B(0x14): 0x00 0x01 0x00 0x1B 0x00 0x00 0x00 0x0C 0x00 0x07 0x00 0x06 0x00 0x58 0x00 0x82 0x00 0x00 0xFF 0x01
    #     # kk_type_001B(0x14): 0x00 0x01 0x00 0x1B 0x00 0x00 0x00 0x0C 0x00 0x00 0x00 0x1E 0x00 0x58 0x00 0x82 0x00 0x00 0x01 0x01
    #     # kk_type_001B(0x14): 0x00 0x01 0x00 0x1B 0x00 0x00 0x00 0x0C 0x00 0x03 0x00 0x0E 0x00 0x58 0x00 0x82 0x00 0x00 0x02 0x01
    #     # kk_type_001B(0x14): 0x00 0x01 0x00 0x1B 0x00 0x00 0x00 0x0C 0x00 0x00 0x00 0x60 0x00 0x58 0x00 0x81 0x00 0x00 0x02 0x00
    #     # kk_type_001B(0x14): 0x00 0x01 0x00 0x1B 0x00 0x00 0x00 0x0C 0x00 0x06 0x00 0x0E 0x00 0x03 0x00 0x2A 0x00 0x00 0x03 0x01
    #     # kk_type_001B(0x14): 0x00 0x01 0x00 0x1B 0x00 0x00 0x00 0x0C 0x00 0x05 0x00 0x0E 0x00 0x07 0x00 0x32 0x00 0x00 0x06 0x01
    #     # kk_type_001B(0x14): 0x00 0x01 0x00 0x1B 0x00 0x00 0x00 0x0C 0x00 0x00 0x00 0x06 0x00 0x15 0x00 0x9D 0x00 0x00 0x0A 0x01
    #     #kk_type_001B(0x14): 0x00 0x01 0x00 0x1B 0x00 0x00 0x00 0x0C 0x00 0x00 0x00 0x2A 0x00 0x59 0x00 0x67 0x00 0x00 0x00 0x01

    #     data = pack['data']
    #     show_effect = data[0] == 0x00
    #     index1 = data[1]
    #     index2 = iKingUtils.hex2int(bytearray(data[2:4]))
    #     pos = Pos(pos_data=data[4:8])
    #     if self.player.check_pos(pos=pos):
    #         self.player.buff_change(data[-2:])
    #         logging.getLogger("iking_proxy").info(iKingUtils.dump_string(type_, "%s %s buff change: %s %s(0x%.2X)" % (self.player.fullname(), self.player.pos(True), "+" if data[-2] == 0x00 else "-", Buff.name(data[-1]), data[-1]), ret=True))
    #         return

    #     for mob in self.mobs_list:
    #         if mob.check_pos(pos=pos):
    #             mob.buff_change(data[-2:])
    #             logging.getLogger("iking_proxy").info(iKingUtils.dump_string(type_, "%s %s buff change: %s %s(0x%.2X)" % (mob.fullname(), mob.pos(True), "+" if data[-2] == 0x00 else "-", Buff.name(data[-1]), data[-1]), ret=True))
    #             return

    #     logging.getLogger("iking_proxy").info(iKingUtils.dump_string(type_, "[%d, %d] buff change: %s %s(0x%.2X)" % (pos.x, pos.y, "+" if data[-2] == 0x00 else "-", Buff.name(data[-1]), data[-1]), ret=True))

    def do_001C(self, type_, pack):
        # kk_type_001C(0x0E): 0x00 0x01 0x00 0x1C 0x00 0x00 0x00 0x06 0x00 0x2D 0x00 0xC7 0x80 0x20
        data = pack['data']
        pos = Pos(pos_data=data[0:4])
        if self.player.check_pos(pos=pos):
            self.player.buff_change(data[-2:])
            logging.getLogger("iking_proxy").info(iKingUtils.dump_string(type_, "%s %s buff change: %s %s(0x%.2X)" % (self.player.fullname(), self.player.pos(True), "+" if data[-2] == 0x00 else "-", Buff.name(data[-1]), data[-1]), ret=True))
            return

        for mob in self.mobs_list:
            if mob.check_pos(pos=pos):
                mob.buff_change(data[-2:])
                logging.getLogger("iking_proxy").info(iKingUtils.dump_string(type_, "%s %s buff change: %s %s(0x%.2X)" % (mob.fullname(), mob.pos(True), "+" if data[-2] == 0x00 else "-", Buff.name(data[-1]), data[-1]), ret=True))
                return

        logging.getLogger("iking_proxy").info(iKingUtils.dump_string(type_, "[%d, %d] buff change: %s %s(0x%.2X)" % (pos.x, pos.y, "+" if data[-2] == 0x00 else "-", Buff.name(data[-1]), data[-1]), ret=True))

    def do_001E(self, type_, pack):
        self.do_default(type_, pack)

    def do_001F(self, type_, pack):
        # iKingUtils.dump_string(type_, "%s: %d" % (name, value))
        logging.getLogger("iking_proxy").info(iKingUtils.dump_bytearray(pack['data'], 'type_%s(music)' % type_, ret_full=True))

    def do_0020(self, type_, pack):
        # '0020': iKingPackage.do_0020, # 0x00 0x01 0x00 0x20 0x00 0x00 0x00 0x06 0x00 0x5A 0x00 0x94 0x00 0x4B
        data = pack['data']
        pos = Pos(pos_data=data[0:4])
        magic = iKingUtils.hex2int(data[4:6])
        if self.player.check_pos(pos=pos):
            logging.getLogger("iking_proxy").info(iKingUtils.dump_string(type_, "%s %s use magic: %s(0x%.2X)" % (self.player.fullname(), self.player.pos(True), Magic.name(magic), magic), ret=True))
            return

        for mob in self.mobs_list:
            if mob.check_pos(pos=pos):
                logging.getLogger("iking_proxy").info(iKingUtils.dump_string(type_, "%s %s use magic: %s(0x%.2X)" % (mob.fullname(), mob.pos(True), Magic.name(magic), magic), ret=True))
                return

        logging.getLogger("iking_proxy").info(iKingUtils.dump_string(type_, "[%d, %d] use magic: %s(0x%.2X)" % (pos.x, pos.y, Magic.name(magic), magic), ret=True))

    def do_0023(self, type_, pack):
        logging.getLogger("iking_proxy").info(iKingUtils.dump_bytearray(pack['data'], 'type_%s(load finish)' % type_, ret_full=True))

    def do_0024(self, type_, pack):
        self.do_default(type_, pack)
        # data = pack['data']
        # if self.player is not None and data[0] == 0x03:
        #     self.player.move(iKingUtils.hex2int(data[1:3]), iKingUtils.hex2int(data[3:5]))
        #     print '%s move to %s %s' % (self.player.fullname(), self.player.pos(), self.player.pos(True))

        # iKingUtils.dump_bytearray(data, 'type_%s' % pack['type'])

    def do_0025(self, type_, pack):
        # Poem
        self.do_default(type_, pack)

    def do_default(self, type_, pack, highlight=False, special=None):
        if highlight:
            logging.getLogger("iking_proxy").info(iKingUtils.dump_bytearray(pack['full'], '**%s** kk_type_%s' % (special if special is not None else "-|-", type_), ret_full=True))
        else:
            logging.getLogger("iking_proxy").info(iKingUtils.dump_bytearray(pack['full'], 'kk_type_%s' % type_, ret_full=True))

    # 一件智力衣服腐蚀, 服务器要给客户端这些包(当然可能一次发送, 但其实是多个包)
    # 000F 智力(int) 下降
    # 000F 最大mp(max_sp) 下降
    # 000F 防御(armor_class) 下降
    # 000F 额防(defense_bonus) 下降
    # 0014 脱衣服的动作
    # 0015 衣服消失的贴图变化
    # 0010 装备栏的装备状态变化
    # 000F 智力(int) 上升
    # 000F 最大mp(max_sp) 上升
    # 000F 防御(armor_class) 上升
    # 000F 额防(defense_bonus) 上升
    # 0014 穿衣服的动作
    # 0015 穿上衣服的贴图变化
    # 0010 装备栏的装备状态变化
    # 0012 (sys: 08)一个被腐蚀的描述信息
    # 000A 一个面板信息的更新

    def process_pack(self, type_, pack):
        # 装备栏状态变化 kk_type_0010(0x0E): 0x00 0x01 0x00 0x10 0x00 0x00 0x00 0x06 0x00 0x0F 0x10 0x01 0x05 0x03

        # '0014': iKingPackage.do_0014, # action 0x00 0x01 0x00 0x14 0x00 0x00 0x00 0x09 0x00 0x55(x) 0x00 0x8E(y) 0x00 0x00 0x00 0x07(action) 0xFF(direction)
        # *'0015': iKingPackage.do_0015, # 0x00 0x01 0x00 0x15 0x00 0x00 0x00 0x08 0x00 0x55(x) 0x00 0x8E(x) 0x00 0x00 0x00 0x16
        # '0017': iKingPackage.do_0017, # 0x00 0x01 0x00 0x17 0x00 0x00 0x00 0x04 0x00 0x5E(x) 0x00 0x9D(y)
        # '001B': iKingPackage.do_001B, # 0x00 0x01 0x00 0x1B 0x00 0x00 0x00 0x0C 0x00 0x04 0x00 0x59 0x00 0x56 0x00 0x8E 0x00 0x00 0xFF 0x01
        # '001C': iKingPackage.do_001C, # 0x00 0x01 0x00 0x1C 0x00 0x00 0x00 0x06 0x00 0x56 0x00 0x8E 0x00 0x20
        # *'0020': iKingPackage.do_0020, # 0x00 0x01 0x00 0x20 0x00 0x00 0x00 0x06 0x00 0x5A 0x00 0x94 0x00 0x4B
        # '0024': iKingPackage.do_0024, # 0x00 0x01 0x00 0x24 0x00 0x00 0x00 0x11 0x02 0x00 0x5E 0x00 0x9B 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00
        method_name = "do_%s" % type_
        if hasattr(self, method_name):
            try:
                getattr(self, method_name)(type_, pack)
            except Exception:
                err_desc = traceback.format_exc()
                print err_desc

                ts = int(time.time() * 1000)
                cache = os.path.join('error_logs', '%d_%s.dat' % (ts, type_))
                i = 1
                while os.path.exists(cache):
                    cache = os.path.join('error_logs', '%d_%s_%.2d.dat' % (ts, type_, i))
                    i += 1
                with open(cache, "wb") as file:
                    file.write(err_desc)
                    file.write("\n\n")
                    file.write(iKingUtils.dump_bytearray(pack['full'], ret_full=True))
                    file.close()

                self.do_default(type_, pack)
                # raise e
        else:
            self.do_default(type_, pack)

    @staticmethod
    def extract_pack(data):
        packs = []
        offset = 0
        while offset < len(data):
            # if data[offset + 4] != 0 || data[offset + 5] != 0:
            #     throw False
            # if hex2int(data[offset + 6:offset + 8]) > 0x4000:
            #     throw False
            if len(data) - offset < 8:
                break
            pack = {}
            pack['v0'] = "%.2X%.2X" % (data[offset + 0], data[offset + 1])
            pack['type'] = "%.2X%.2X" % (data[offset + 2], data[offset + 3])
            pack['length'] = iKingUtils.hex2int(data[offset + 6:offset + 8])
            pack['full'] = data[offset:offset + 8 + pack['length']]
            pack['data'] = data[offset + 8:offset + 8 + pack['length']]
            if len(pack['data']) == pack['length']:
                pack['data'] = iKingUtils.fix_string_color(pack['data'])
                packs.append(pack)
                offset = offset + 8 + pack['length']
            else:
                break
        return (packs, offset)

    def process_data_packs(self, data_packs, caller=None):
        self.packs.extend(data_packs)

    def process_loop(self):
        while self.processing:
            if len(self.packs) > 0:
                pack = self.packs.popleft()
                if self.caller is not None:
                    self.caller.beforePackProcess(pack)
                    self.caller.doPackProcess(pack, None)
                    self.caller.afterPackProcess(pack)
                else:
                    t = pack['type']
                    self.process_pack(t, pack)
            else:
                time.sleep(0.1)

    def stop(self):
        self.processing = False
        # self.process_thread.stop()
        self.process_thread.join()
