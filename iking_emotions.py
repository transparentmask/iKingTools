#!/usr/bin/env python
# -*- encoding: utf-8 -*-
from iking_utils import iKingUtils


class Emotion(object):
    EMOTION_MIN = 0x03E9
    EMOTION_MAX = 0x0469
    EMOTION = {
        0x03E9: "飛吻, kiss",
        0x03EA: "打飽嗝, burp",
        0x03EB: "那也安捏, ack",
        0x03EC: "屈膝禮, curtsey",
        0x03ED: "揮拳咆哮, growl",
        0x03EE: "絞手, twiddle",
        0x03EF: "揮揮手, wave",
        0x03F0: "高興地唱, sing",
        0x03F1: "裝死, die",
        0x03F3: "嗶嗶, beep",
        0x03F4: "挑眉, arc",
        0x03F5: "邪惡的笑, grin",
        0x03F6: "抬抬眉毛, raise",
        0x03F7: "眨眼, blink",
        0x03F8: "耐心地等, wait",
        0x03F9: "熱情的笑, beam",
        0x03FA: "皺眉, frown",
        0x03FB: "扮鬼臉, grimace",
        0x03FC: "拋媚眼, leer",
        0x03FD: "嘟嘴, pout",
        0x03FE: "深深注視, stare",
        0x03FF: "呻吟, groan",
        0x0400: "咳嗽, cough",
        0x0401: "聳聳肩, shrug",
        0x0402: "抱怨, mutter",
        0x0403: "怨東怨西, grumble",
        0x0404: "lag, lag",
        0x0405: "啊！, ah",
        0x0407: "打招呼, hi",
        0x0408: "昏倒了, faint",
        0x0409: "跌了一跤, flop",
        0x040B: "跳起來, jump",
        0x040C: "跟神一樣, buddha",
        0x040D: "渾身顫抖, cower",
        0x040E: "衷心感謝, thank",
        0x040F: "溫柔擁抱, cuddle",
        0x0410: "踢屁屁, kick",
        0x0411: "輕拍, pat",
        0x0412: "一巴掌, slap",
        0x0413: "甜蜜情話, whisper",
        0x0414: "咯咯咯！, cackle",
        0x0415: "吃吃地笑, giggle",
        0x0416: "混身顫抖, tremble",
        0x0417: "害怕, cringe",
        0x0418: "大搖大擺, strut",
        0x0419: "挨近, snuggle",
        0x041B: "擁吻, lkiss",
        0x041C: "緊抱, hug",
        0x041D: "狠狠地咬, bite",
        0x041E: "安慰, comfort",
        0x041F: "抓住, tackle",
        0x0420: "輕拍肩膀, tap",
        0x0421: "抓抓龍, rub",
        0x0422: "輕輕的推, nudge",
        0x0423: "打屁股, spank",
        0x0424: "鞠躬, bow",
        0x0425: "卑躬屈膝, grovel",
        0x0426: "走來走去, pace",
        0x0427: "完全同意, agree",
        0x0428: "點頭, nod",
        0x0429: "使使眼色, wink",
        0x042A: "亂吠, bark",
        0x042B: "吐一口痰, spit",
        0x042C: "愉快微笑, smile",
        0x042D: "呵呵傻笑, smirk",
        0x042E: "低聲輕笑, chuckle",
        0x042F: "羞得臉紅, blush",
        0x0430: "流口水, slobber",
        0x0431: "搖搖頭, shake",
        0x0433: "東聞西聞, sniff",
        0x0434: "大聲尖叫, scream",
        0x0435: "吹著口哨, whistle",
        0x0436: "哼！, snort",
        0x0438: "歎了口氣, sigh",
        0x0439: "轉過頭去, avert",
        0x043A: "敲頭, bang",
        0x043B: "開始思考, hmm",
        0x043C: "打鼾聲, snore",
        0x043D: "低頭沉思, ponder",
        0x043E: "盯著看, peer",
        0x043F: "發呆, idle",
        0x0440: "聆聽, listen",
        0x0441: "嗚咽, moan",
        0x0442: "哭哭啼啼, sob",
        0x0443: "擦擦汗水, sweat",
        0x0444: "號啕大哭, cry",
        0x0445: "搔搔頭, scratch",
        0x0446: "疑惑, ?",
        0x0447: "揉揉眼睛, roll",
        0x0448: "打哈欠, yawn",
        0x0449: "伸懶腰, stretch",
        0x044B: "真心喝彩, cheer",
        0x044C: "歡迎到來, greet",
        0x044D: "挑戰, pk",
        0x044E: "喘不過氣, gasp",
        0x044F: "熱情探戈, tango",
        0x0450: "跳華爾滋, dance",
        0x0451: "轉圈子, spin",
        0x0452: "開始嘔吐, puke",
        0x0453: "吐得滿地, barf",
        0x0454: "笑倒在地, laugh",
        0x0455: "蹦來蹦去, bounce",
        0x0456: "高興, ya",
        0x0457: "搖擺, waggle",
        0x0458: "舔人, lick",
        0x0459: "怒視著, glare",
        0x045A: "放屁, fart",
        0x045B: "指著, point",
        0x045C: "戳, poke",
        0x045D: "呵癢, tickle",
        0x045E: "摀住嘴巴, gag",
        0x045F: "喵喵地叫, cat",
        0x0460: "嘖嘖稱奇, tsk",
        0x0461: "有人在嗎, ak",
        0x0462: "鼓掌, clap",
        0x0463: "鴨子叫, duck",
        0x0464: "拍拍灰塵, flip",
        0x0465: "揮揮鞭子, flog",
        0x0466: "學豬叫, grunt",
        0x0467: "學狼嚎, howl",
        0x0468: "對空鳴槍, pong",
        0x0469: "繞著打轉, zip",
    }

    @staticmethod
    def isEmotion(type_):
        return type_ >= Emotion.EMOTION_MIN and type_ <= Emotion.EMOTION_MAX

    @staticmethod
    def emotion(type_):
        if type_ in Emotion.EMOTION:
            return Emotion.EMOTION[type_]
        else:
            return "0x%.2X" % type_

    def __init__(self, data=None, iking=None, iking_tables=None):
        if data is not None:
            self.parse(data, iking, iking_tables)

    def parse(self, data, iking, iking_tables):
        ba = bytearray(data)
        self.action1_hex = ba[0:2]
        self.action1 = iKingUtils.hex2int(self.action1_hex, bigEndian=False)
        self.action2_hex = ba[2:4]
        self.action2 = iKingUtils.hex2int(self.action2_hex, bigEndian=False)
        self.file_index = ba[4]
        self.sub_index = ba[5]
        self.name = str(data[6:]).strip("\x00").decode('big5').encode('utf-8')
        for i in range(0x1000 / 8):
            if iking_tables[i * 8 + 0x04] == self.action1_hex[0] and iking_tables[i * 8 + 0x05] == self.action1_hex[1]:
                str_offset = iKingUtils.hex2int(iking_tables[i * 8:i * 8 + 4], bigEndian=False)
                str_offset -= 0x401800
                iking.seek(str_offset)
                self.name_en, _ = iKingUtils.export_string(iking.read(0x10), 0)
                self.name_en = self.name_en.strip(" ")

    def desc(self):
        action1_hex = " ".join(map(lambda b: "0x%.2X" % b, self.action1_hex))
        action2_hex = " ".join(map(lambda b: "0x%.2X" % b, self.action2_hex))
        return "%.2d - %.2d: %s(%s) %d(%s) %d(%s)" % (self.file_index, self.sub_index, self.name, self.name_en, self.action1, action1_hex, self.action2, action2_hex)


if __name__ == '__main__':
    emotions = []
    iking = open("iKing/iKingXP.exe", "rb")
    iking.seek(0x1C55F0)
    tables = bytearray(iking.read(0x1000))
    # 0x401800

    with open("iKing/EmoteBtn.dat", "rb") as file:
        count = iKingUtils.hex2int(bytearray(file.read(2)), bigEndian=False)
        for i in range(count):
            emotion_data = file.read(0x26)
            emotion = Emotion(emotion_data, iking, tables)
            emotions.append(emotion)

    iking.close()

    # magics.sort(key=lambda m: m.file_index * 0x100 + m.sub_index)

    for index, emotion in enumerate(emotions):
        # print "0x%.2X: \"%s\"," % (index, emotion.name)
        print "0x%.2X: %s" % (index, emotion.desc())
