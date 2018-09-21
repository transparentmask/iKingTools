#!/usr/bin/env python
# -*- encoding: utf-8 -*-
from iking_utils import iKingUtils


class Magic(object):
    NAME = {
        0x03: "反魔法力场(anti_magic)",
        0x04: "弧光指(arc_fire)",
        0x05: "祝福(bless)",
        0x08: "魔法镀膜(coating)",
        0x09: "治疗术(cure)",
        0x0A: "疗毒术(cure_poison)",
        0x11: "侦测隐形(detect_invi)",
        0x15: "喷火龙(dragon_breath)",
        0x16: "火龙变幻(dragon)",
        0x17: "恐惧术(fear)",
        0x18: "火球术(fireball)",
        0x19: "萤光术(firefly)",
        0x1A: "急救术(first_aid)",
        0x1B: "飞拳术(fist)",
        0x1D: "核融合术(flare)",
        0x1E: "飘浮(float)",
        0x1F: "冻结术(freeze)",
        0x20: "重力倍增(gravity)",
        0x23: "恢复术(heal)",
        0x28: "神圣精神(holy_spirit)",
        0x2A: "圣水术(holy_water)",
        0x2C: "冰刃风暴(ice_lance)",
        0x2D: "隐身术(invisible)",
        0x2F: "召雷术(lightning)",
        0x31: "闪电球(lightning_sphere)",
        0x33: "巫师之火(magefire)",
        0x34: "魔法弹(magic_missle)",
        0x35: "亚伯拉之盾(magic_shield)",
        0x36: "造绳术(make_rope)",
        0x3A: "巨魔之力(ogre_power)",
        0x3B: "毒击(poison)",
        0x3F: "强力恢复(restore)",
        0x41: "暗之盾(shadow_shield)",
        0x44: "吸魂术(soul_steal)",
        0x45: "幽灵之触(spectre_touch)",
        0x47: "心灵之鎚(spirit_hammer)",
        0x48: "化石术(stone)",
        0x49: "硬皮术(stone_skin)",
        0x4A: "冰雪风暴(storm)",
        0x4B: "强壮(strong)",
        0x4C: "电击术(stun)",
        0x4D: "召唤元素(summon_element)",
        0x50: "造狼术(wolf)",
    }

    @staticmethod
    def name(type_):
        if type_ in Magic.NAME:
            return Magic.NAME[type_]
        else:
            return "0x%.2X" % type_

    def __init__(self, data=None):
        if data is not None:
            self.parse(data)

    def parse(self, data):
        self.name = data[:0x10].strip("\x00").decode('big5').encode('utf-8')
        self.name_eng = data[0x10:0x28].strip("\x00")
        self.num_1_hex = bytearray(data[0x28:0x2A])
        self.num_1 = iKingUtils.hex2int(self.num_1_hex, bigEndian=False)
        self.sub_index = iKingUtils.hex2int(bytearray(data[0x2A:0x2C]), bigEndian=False)
        self.file_index = iKingUtils.hex2int(bytearray(data[0x2C:0x2E]), bigEndian=False)
        self.num_2 = iKingUtils.hex2int(bytearray(data[0x2E:0x30]), bigEndian=False)

    def desc(self):
        # num_1_hex = " ".join(map(lambda b: "0x%.2X" % b, self.num_1_hex))
        # return "%02d - %02d (%d) (%s) %s(%s)" % (self.file_index, self.sub_index, self.num_2, num_1_hex, self.name, self.name_eng)
        return "%02d - %02d (%d) %s(%s)" % (self.file_index, self.sub_index, self.num_1, self.name, self.name_eng)


if __name__ == '__main__':
    magics = []
    with open("iKing/SplTable.dat", "rb") as file:
        count = iKingUtils.hex2int(bytearray(file.read(2)), bigEndian=False)
        for i in range(count):
            spl_data = file.read(0x30)
            magic = Magic(spl_data)
            magics.append(magic)

    # magics.sort(key=lambda m: m.file_index * 0x100 + m.sub_index)

    for index, magic in enumerate(magics):
        # print "0x%.2X: %s" % (index + 1, magic.desc())
        print "%s" % (magic.desc())


class Buff(object):
    NAME = {
        0x01: "天使之音",
        0x02: "侦测隐形",
        0x03: "神光",
        0x04: "中毒",
        0x05: "????05",
        0x06: "????06",
        0x07: "神圣之力",
        0x08: "纯洁之盾",
        0x09: "禁言",
        0x0A: "巨大",
        0x0B: "神圣精神",
        0x0C: "圣光",
        0x0D: "????0D",  # 狂暴攻击?
        0x0E: "荧光术",
        0x0F: "隐形",
        0x10: "暗之盾",
        0x11: "祝福",
        0x12: "漂浮",
        0x13: "亚伯拉盾",
        0x14: "????14",
        0x15: "盲目",
        0x16: "迅捷",
        0x17: "自然医疗?",
        0x18: "加速度",
        0x19: "镇定",
        0x1A: "朦胧",
        0x1B: "巨魔之力",
        0x1C: "石肤",
        0x1D: "骑马",  # 冲锋?
        0x1E: "英雄气魄",
        0x1F: "????1F",
        0x20: "强壮",
        0x21: "????21",
        0x22: "????22",
        0x23: "????23",
        0x24: "虚弱",
        0x25: "巫师之火",
        0x26: "火把??",
    }

    @staticmethod
    def name(type_):
        if type_ in Buff.NAME:
            return Buff.NAME[type_]
        else:
            return "0x%.2X" % type_


"""
0012-系统(08) 妳高舉雙手 : 戰神啊 ! 加您的神力於您的戰士吧。
kk_type_0014(0x11): 0x00 0x01 0x00 0x14 0x00 0x00 0x00 0x09 0x00 0x2D 0x00 0xC7 0x00 0x00 0x00 0x13 0xFF
0020        噗噗(vachell) [0x2D,0xC7] use magic: 0x4B
kk_type_001B(0x14): 0x00 0x01 0x00 0x1B 0x00 0x00 0x00 0x0C 0x00 0x00 0x00 0x1F 0x00 0x2D 0x00 0xC7 0x00 0x00 0x00 0x01
0012-系统(08) 妳渾身肌肉變得更發達 ...
kk_type_001B(0x14): 0x00 0x01 0x00 0x1B 0x00 0x00 0x00 0x0C 0x00 0x04 0x00 0x59 0x00 0x2D 0x00 0xC7 0x00 0x00 0xFF 0x01
kk_type_001C(0x0E): 0x00 0x01 0x00 0x1C 0x00 0x00 0x00 0x06 0x00 0x2D 0x00 0xC7 0x00 0x20

kk_type_001B(0x14): 0x00 0x01 0x00 0x1B 0x00 0x00 0x00 0x0C 0x10 0x04 0x00 0x59 0x00 0x2D 0x00 0xC7 0x00 0x00 0x00 0x01
kk_type_001C(0x0E): 0x00 0x01 0x00 0x1C 0x00 0x00 0x00 0x06 0x00 0x2D 0x00 0xC7 0x80 0x20


kk_type_0014(0x11): 0x00 0x01 0x00 0x14 0x00 0x00 0x00 0x09 0x00 0x2D 0x00 0xC7 0x00 0x00 0x00 0x15 0xFF
0020        噗噗(vachell) [0x2D,0xC7] use magic: 0x05
0012-系统(08) 一道藍色的光芒緩緩從地面升起, 環繞在妳身上, 發出閃閃的螢光 ...
kk_type_001B(0x14): 0x00 0x01 0x00 0x1B 0x00 0x00 0x00 0x0C 0x00 0x00 0x00 0x0F 0x00 0x2D 0x00 0xC7 0x00 0x00 0x00 0x01
kk_type_001B(0x14): 0x00 0x01 0x00 0x1B 0x00 0x00 0x00 0x0C 0x00 0x07 0x00 0x06 0x00 0x2D 0x00 0xC7 0x00 0x00 0xFF 0x01
kk_type_001C(0x0E): 0x00 0x01 0x00 0x1C 0x00 0x00 0x00 0x06 0x00 0x2D 0x00 0xC7 0x00 0x11

kk_type_001B(0x14): 0x00 0x01 0x00 0x1B 0x00 0x00 0x00 0x0C 0x10 0x07 0x00 0x06 0x00 0x5A 0x00 0xBE 0x00 0x00 0x00 0x01
kk_type_001C(0x0E): 0x00 0x01 0x00 0x1C 0x00 0x00 0x00 0x06 0x00 0x5A 0x00 0xBE 0x80 0x11

0012-系统(08) 妳喃喃唸道 : 摩里多納 ～～ 賀魯 ...
kk_type_0014(0x11): 0x00 0x01 0x00 0x14 0x00 0x00 0x00 0x09 0x00 0x2D 0x00 0xC7 0x00 0x00 0x00 0x15 0xFF
0020        噗噗(vachell) [0x2D,0xC7] use magic: 0x1E
0012-系统(08) 妳緩緩從地面升起 ...
kk_type_001B(0x14): 0x00 0x01 0x00 0x1B 0x00 0x00 0x00 0x0C 0x00 0x00 0x00 0x0C 0x00 0x2D 0x00 0xC7 0x00 0x00 0xFF 0x01
kk_type_001C(0x0E): 0x00 0x01 0x00 0x1C 0x00 0x00 0x00 0x06 0x00 0x2D 0x00 0xC7 0x00 0x12

0012-系统(08) 妳又緩緩降回地面。
kk_type_001B(0x14): 0x00 0x01 0x00 0x1B 0x00 0x00 0x00 0x0C 0x10 0x00 0x00 0x0C 0x00 0x5A 0x00 0xBE 0x00 0x00 0x00 0x01
kk_type_001C(0x0E): 0x00 0x01 0x00 0x1C 0x00 0x00 0x00 0x06 0x00 0x5A 0x00 0xBE 0x80 0x12


kk_type_0014(0x11): 0x00 0x01 0x00 0x14 0x00 0x00 0x00 0x09 0x00 0x5A 0x00 0xBE 0x00 0x00 0x00 0x13 0x07
kk_type_001B(0x14): 0x00 0x01 0x00 0x1B 0x00 0x00 0x00 0x0C 0x00 0x03 0x00 0x0E 0x00 0x5A 0x00 0xBE 0x00 0x00 0x02 0x01
0020        噗噗(vachell) [0x5A,0xBE] use magic: 0x1B
0012-系统(08) 妳低頭喃喃唸道 : 戰神啊 ... 借您神武之拳打擊敵人吧 !
kk_type_001A(0x14): 0x00 0x01 0x00 0x1A 0x00 0x00 0x00 0x0C 0x00 0x00 0x80 0x05 0x00 0x5A 0x00 0xBE 0x00 0x57 0x00 0xC0
0012-系统(08) 天空突然伸出一隻大手, 一拳向白兔轟過去 ...

kk_type_0014(0x11): 0x00 0x01 0x00 0x14 0x00 0x00 0x00 0x09 0x00 0x5A 0x00 0xBE 0x00 0x00 0x00 0x13 0x07
kk_type_001B(0x14): 0x00 0x01 0x00 0x1B 0x00 0x00 0x00 0x0C 0x00 0x03 0x00 0x0E 0x00 0x5A 0x00 0xBE 0x00 0x00 0x02 0x01
0020        噗噗(vachell) [0x5A,0xBE] use magic: 0x1B
0012-系统(08) 妳低頭喃喃唸道 : 戰神啊 ... 借您神武之拳打擊敵人吧 !
kk_type_001A(0x14): 0x00 0x01 0x00 0x1A 0x00 0x00 0x00 0x0C 0x00 0x00 0x80 0x05 0x00 0x5A 0x00 0xBE 0x00 0x59 0x00 0xBE
0012-系统(08) 天空突然伸出一隻大手, 一拳向白兔轟過去 ...

"""

"""
    0x01: "召唤天使(angel)",
    0x02: "天使之音(angel_voice)",
    0x03: "反魔法力场(anti_magic)",
    0x04: "弧光指(arc_fire)",
    0x05: "祝福(bless)",
    0x06: "盲目(blind)",
    0x07: "镇定术(calm)",
    0x08: "魔法镀膜(coating)",
    0x09: "治疗术(cure)",
    0x0A: "疗毒术(cure_poison)",
    0x0B: "匕首雨(dagger_fall)",
    0x0C: "狂舞之剑(dancing_sword)",
    0x0D: "死亡之指(death_touch)",
    0x0E: "延时炸弹(delay_bomb)",
    0x0F: "破魔(demon_bane)",
    0x10: "恶魔之击(demon_strike)",
    0x11: "侦测隐形(detect_invi)",
-    0x12: "解除力场(dispel)",
    0x13: "天使尘(divine_dust)",
-    0x14: "神之干预(divine_power)",
    0x15: "双倍医疗(double_heal)",
    0x16: "火龙变幻(dragon)",
    0x17: "喷火龙(dragon_breath)",
    0x18: "巨大术(enlarge)",
    0x19: "恐惧术(fear)",
    0x1A: "火球术(fireball)",
    0x1B: "萤光术(firefly)",
    0x1C: "急救术(first_aid)",
    0x1D: "飞拳术(fist)",
    0x1E: "火焰剑(flame_sword)",
    0x1F: "核融合术(flare)",
    0x20: "飘浮(float)",
    0x21: "冻结术(freeze)",
    0x22: "重力倍增(gravity)",
    0x23: "迅捷术(haste)",
    0x24: "朦胧术(hazy)",
    0x25: "恢复术(heal)",
    0x26: "英雄气魄(heroism)",
    0x27: "神圣爆破(holy_blast)",
    0x28: "神光术(holy_light)",
    0x29: "神圣之力(holy_power)",
    0x2A: "神圣精神(holy_spirit)",
    0x2B: "神圣之击(holy_strike)",
    0x2C: "圣水术(holy_water)",
    0x2D: "圣言术(holy_word)",
    0x2E: "冰刃风暴(ice_lance)",
-    0x2F: "鑑定术(identify)",
    0x30: "隐身术(invisible)",
    0x31: "召雷术(lightning)",
    0x32: "爆雷(lightning_bolt)",
    0x33: "闪电球(lightning_sphere)",
    0x34: "闪电剑(lightning_sword)",
-    0x35: "定位术(location)",
    0x36: "魔法漩涡(maelstrom)",
    0x37: "巫师之火(magefire)",
    0x38: "魔法弹(magic_missle)",
    0x39: "亚伯拉之盾(magic_shield)",
    0x3A: "造绳术(make_rope)",
    0x3B: "心灵爆破(mind_blast)",
    0x3C: "月光术(moon_light)",
    0x3D: "自然医疗(natural_heal)",
    0x3E: "巨魔之力(ogre_power)",
    0x3F: "毒击(poison)",
    0x40: "纯洁之刃(pure_blade)",
    0x41: "纯洁之盾(pure_shield)",
-    0x42: "复活术(regeneration)",
    0x43: "强力恢复(restore)",
    0x44: "圣光术(sanctuary)",
    0x45: "暗之盾(shadow_shield)",
    0x46: "电能冲击(shock_wave)",
    0x47: "沉静术(silence)",
-    0x48: "天剑(sky_sword)",
    0x49: "吸魂术(soul_steal)",
    0x4A: "幽灵之触(spectre_touch)",
    0x4B: "加速度(speedup)",
    0x4C: "心灵之鎚(spirit_hammer)",
    0x4D: "化石术(stone)",
    0x4E: "硬皮术(stone_skin)",
    0x4F: "冰雪风暴(storm)",
    0x50: "强壮(strong)",
    0x51: "电击术(stun)",
    0x52: "召唤元素(summon_element)",
    0x53: "真空斩(vacuum_blade)",
    0x54: "风之龙(wind_dragon)",
    0x55: "造狼术(wolf)",
    0x56: "圣光弹(holyball)",
    0x57: "神之怒雷(god_lightning)",
    0x58: "雷光护盾(lightning_shield)",
    0x59: "光灵术(light_element)",
    0x5A: "梦之法术(zzzz)",
    0x5B: "化剑诀(swordize)",
    0x5C: "御剑诀(swordplay)",
    0x5D: "万剑诀(swords)",
    0x5E: "回生诀(revive_sword)",
    0x5F: "心剑(mind_sword)",
    0x60: "潜能激化(potential)",
    0x61: "回时术(retime)",
    0x62: "时空裂缝(time_break)",
    0x63: "岁月无情(ages)",
    0x64: "末日禁咒(nuke)",
    0x65: "奇蹟之光(miracle_light)",
    0x66: "清心咒(clear_word)",
    0x67: "金刚咒(protect_word)",
    0x68: "雷咒(lightning_word)",
    0x69: "守护神音(voice)",
    0x6A: "定身咒(hold)",
    0x6B: "狮子吼(command)",
    0x6C: "真言咒(words)",
    0x6D: "嗜血(bloodlust)",
    0x6E: "失忆术(forgetter)",
    0x6F: "无尽黑暗(darken)",
    0x70: "飞剑术(fly_swords)",
    0x71: "剑灵罩(sword_shield)",
    0x72: "大地之刃(earth_sword)",
    0x73: "流星雨(meteor_shower)",
    0x74: "活尸术(animate)",
    0x75: "枯竭术(drain)",
    0x76: "黑暗之门(dark_gate)",
    0x77: "死亡诅咒(death_curse)",
    0x78: "吸魂真言(vampires)",
    0x79: "黑暗深渊(dark_abyss)",
    0x7A: "神言术(divine_word)",
    0x7B: "神威术(god_power)",
    0x7C: "天谴术(divine_blame)",
    0x7D: "神助术(divine_aid)",
    0x7E: "天杀术(divine_nuke)",
    0x7F: "真言术(my_word)",
    0x80: "谴责术(my_blame)",
    0x81: "协助术(my_aid)",
    0x82: "天使泪(angel_tear)",
    0x83: "深层恢复(deep_recover)",
    0x84: "心灵风暴(mind_storm)",
    0x85: "深度恐惧(deep_terror)",
    0x86: "时空风暴(time_storm)",
    0x87: "神圣之路(holy_path)",
    0x88: "完全医疗(full_heal)",
    0x89: "强力圣言(power_word)",
    0x8A: "强力咒(mighty_word)",
    0x8B: "隐身护罩(dark_cloak)",
    0x8C: "炽炎之刃(arc_dagger)",
    0x8D: "狂刃斩(slashs)",
    0x8E: "能量冲击(energy_shock)",
    0x8F: "能量风暴(energy_storm)",
    0x90: "威力术(my_power)",
    0x91: "即死术(my_nuke)",
    0x92: "圣雷之刃(lightning_blade)",
    0x93: "暗夜幽魂(dark_soul)",
    0x94: "焰之柱(flame_column)",
    0x95: "邪恶反噬(reflect)",
    0x96: "万魔咒(evils)",
    0x97: "灵击术(soul_arc)",
    0x98: "灵鞭术(soul_whip)",
    0x99: "威力带(power_circle)",
    0x9A: "纯洁之光(pure_light)",
    0x9B: "闪烁之光(flash)",
    0x9C: "光之守护者(guardian)",
    0x9D: "终极圣光(ultra_light)",
    0x9E: "邪恶之力(evil_power)",
    0x9F: "黯影术(shadows)",
    0xA0: "黯黑闪电(dark_lightning)",
    0xA1: "恶魔咒(demons)",
    0xA2: "领域(domain)",
    0xA3: "地狱火(hellfire)",
    0xA4: "巨魔术(ogre)",
    0xA5: "黑暗阴影(dark_shadow)",
    0xA6: "邪恶之刃(evil_blade)",
    0xA7: "死亡之吻(death_kiss)",
    0xA8: "死亡末日(doom)",
    0xA9: "再生术(relive)",
    0xAA: "暗之火(black_flame)",
    0xAB: "冰之触(chill_touch)",
    0xAC: "黯黑诅咒(dark_curse)",
    0xAD: "妖火(devil_fire)",
    0xAE: "逆流术(backdraft)",
    0xAF: "淨化仪式(purify)",
    0xB0: "冥想(meditate)",
    0xB1: "法器使用(invoke)",
    0xB2: "法术充电(recharge)",
    0xB3: "狂暴攻击(berserk)",
    0xB4: "狂暴之吼(powerup)",
    0xB5: "骑马下马(mount)",
    0xB6: "骑马冲锋(charge)",
    0xB7: "背刺(backstab)",
    0xB8: "时空跳跃(time_bllink)",
    0xB9: "劝服(convert)",
    0xBA: "禁食(fast)",
    0xBB: "食尸(feast)",
    0xBC: "躲藏(hide)",
    0xBD: "心灵控制(mind_control)",
    0xBE: "镜像分身(mirror_image)",
    0xBF: "剑气(swordkee)",
    0xC0: "附身(possess)",
    0xC1: "残像攻击(shadow)",
    0xC2: "吸魂(soul_steal)",
    0xC3: "偷窃(steal)",
    0xC4: "召唤(summon)",
    0xC5: "传送(locate)",
    0xC6: "毒物学(toxicology)",
    0xC7: "祈愿(wish)",
    0xC8: "守夜之歌(night_watch)",
    0xC9: "雾曲(fog_song)",
    0xCA: "黄昏之星(hesper)",
    0xCB: "醉梦曲(wind_dance)",
    0xCC: "刀剑光影(eager_shadow)",
    0xCD: "最后的祈祷(last_pray)",
    0xCE: "凯尔序曲(carr_vorspiel)",
    0xCF: "天地之木(celestial_tree)",
    0xD0: "闇夜幽歌(deeply_night)",
    0xD1: "邱比特之箭(jupitor_arrow)",
    0xD2: "爱的礼讚(love_song)",
    0xD3: "冬日雪晴(winter_sunshine)",
    0xD4: "靡靡之音(decadent_voice)",
    0xD5: "魂飞魄散(stray_soul)",
    0xD6: "飞翔之歌(fly_song)",
    0xD7: "魔音(magic_voice)",
    0xD8: "血之光晕(blood_ray)",
    0xD9: "勇士之魂(heroic_soul)",
    0xDA: "大地之歌(earth_song)",
    0xDB: "洗尘雨(falling_rain)",
    0xDC: "炙热焰(hot_flame)",
    0xDD: "冰雪暴(ice_barber)",
    0xDE: "远程冲锋(lcharge)",
    0xDF: "喂食马豆(feed)",
    0xE0: "龙状态查询(dragon_score)",
    0xE1: "龙恢复体力(dragon_heal)",
    0xE2: "龙回家休息(dragon_home)",
    0xE3: "命令龙飞行(dragon_fly)",
    0xE4: "龙情绪表达(dragon_emote)",
    0xE5: "喂食蜥蝪乾(fill)",
    0xE6: "命令座骑飞行(fly)",
    0xE7: "装备修复(repair)",
    0xE8: "强化拳术(efist)",
    0xE9: "诱导器(dragon_derive)",
    0xEA: "魔法攻击(dragon_launch)",
"""