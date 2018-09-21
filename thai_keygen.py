#!/usr/bin/env python
# -*- encoding: utf-8 -*-
import random
import math
import datetime
import argparse


def gen_random(min=0x00, max=0xFF):
    rand = random.random()
    rand = rand * (max - min) + min
    rand = math.ceil(rand) - 1
    return int(rand)


def random_char():
    chars = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
    # chars = '0123456789abcdef'
    return chars[gen_random(0, len(chars))]


def charToHex(char):
    return int(char.encode('hex'), 16)


def main():
    parse = argparse.ArgumentParser()
    parse.add_argument('-i', '--id', dest='id', help='player id, not account', type=str)
    args = parse.parse_args()
    if args.id is None:
        parse.print_help()
        exit(0)

    id_len = len(args.id)
    key = ['0'] * 0x20
    key[:6] = datetime.datetime.now().strftime('%y%m%d')
    key[6] = random_char()
    # print ''.join(key)

    tmp_65 = (charToHex(key[6]) + id_len) & 0x0F
    tmp_74 = 7
    for i in range(0, id_len):
        if tmp_74 >= 0x1E:
            print "id to long!"
            exit(0)

        k = charToHex(args.id[i])
        if i == 0:
            k = k - tmp_65 - 3
        else:
            if i & 0x80000001 == 0:
                k = k - tmp_65 - 2
            else:
                k = k - tmp_65
        k &= 0xFF
        if k < 0x61:
            k -= 6
        key[tmp_74] = hex(k)[2:].zfill(2).decode('hex')
        key[tmp_74 + 1] = random_char()
        tmp_74 += 2
    # print ''.join(key)

    for i in range(tmp_74, 0x1E):
        key[i] = random_char()
    # print ''.join(key)

    s = 0
    for c in key[:-2]:
        s += charToHex(c)
    s &= 0xFF
    # print hex(s)
    key[-2:] = hex(s)[2:].zfill(2)
    print ''.join(key)


if __name__ == '__main__':
    main()
