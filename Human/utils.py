#!/usr/bin/env python
# coding: utf-8
# created by hevlhayt@foxmail.com 
# Date: 2016/5/25 
# Time: 10:44
#
import os
import random
from PIL import ImageFont
from PIL import Image
from PIL import ImageDraw
from Human.constants import STATIC_FOLDER


def create_avatar(userid, username='Unknown'):
    save_path = os.path.join(STATIC_FOLDER, 'images/user_avatars/')
    word = ''.join(map(lambda x: x[0].upper(), username.split(' ')))
    beautifulRGB = ((245, 67, 101),
                    (252, 157, 154),
                    (249, 205, 173),
                    (131, 175, 155),
                    (6, 128, 67),
                    (38, 157, 128),
                    (137, 157, 192))
    # font = ImageFont.truetype('simhei.ttf', 250)
    font = ImageFont.truetype('/usr/share/fonts/truetype/simhei.ttf', 250)
    img = Image.new('RGB', (400, 400), random.choice(beautifulRGB))
    draw = ImageDraw.Draw(img)
    if len(word) >= 2:
        draw.text((84, 75), word[:2], (255, 255, 255), font=font)
    if len(word) == 1:
        draw.text((137, 75), word, (255, 255, 255), font=font)
    try:
        img.save(save_path + str(userid) + '.png')
    except IOError, e:
        print 'Avatar create: ', e
        return -1
    return 0

# if __name__ == '__main__':
#     create_avatar(9, 'Name Potter')

