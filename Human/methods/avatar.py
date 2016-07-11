#!/usr/bin/env python
# coding: utf-8
# created by hevlhayt@foxmail.com 
# Date: 2016/7/11
# Time: 13:32
import base64
import os
import random

import cStringIO
from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw

from Human.methods.sessionid import get_session_id

from Human.methods.utils import logger_join
from LineMe.constants import STATIC_FOLDER
from LineMe.settings import logger


def create_avatar(request, userid, username='Unknown'):
    save_path = os.path.join(STATIC_FOLDER, 'images/user_avatars/')
    word = ''.join(map(lambda x: x[0].upper(), username.split(' ')))
    beautifulRGB = ((245, 67, 101),
                    (252, 157, 154),
                    (249, 205, 173),
                    (131, 175, 155),
                    (6, 128, 67),
                    (38, 157, 128),
                    (137, 157, 192))
    # font = ImageFont.truetype('simhei.ttf', 125)
    font = ImageFont.truetype('/usr/share/fonts/truetype/simhei.ttf', 125)
    img = Image.new('RGB', (200, 200), random.choice(beautifulRGB))
    draw = ImageDraw.Draw(img)
    if len(word) >= 2:
        draw.text((40, 38), word[:2], (255, 255, 255), font=font)
    if len(word) == 1:
        draw.text((69, 38), word, (255, 255, 255), font=font)
    try:
        img.save(save_path + str(userid) + '.png')
    except IOError, e:
        logger.error(logger_join('Avatar', get_session_id(request), e=e))
        return -1

    logger.info(logger_join('Avatar', get_session_id(request)))
    return 0


def handle_avatar(request):
    userid = request.user.id
    try:

        image_string = cStringIO.StringIO(base64.b64decode(request.POST['imgBase64'].partition('base64,')[2]))
        image = Image.open(image_string)

        path = os.path.join(STATIC_FOLDER, 'images/user_avatars/')
        image.resize((200, 200)).save(path+str(userid)+".png", image.format, quality=100)
        # print image.format, image.size, image.mode
    except Exception, e:
        logger.error(logger_join('Avatar', get_session_id(request), e=e))
        return -1
    logger.info(logger_join('Avatar', get_session_id(request)))
    return 0