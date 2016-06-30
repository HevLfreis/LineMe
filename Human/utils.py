#!/usr/bin/env python
# coding: utf-8
# created by hevlhayt@foxmail.com 
# Date: 2016/5/25 
# Time: 10:44
#
import re
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import os
import random
import smtplib
from PIL import ImageFont
from PIL import Image
from PIL import ImageDraw
from django.contrib.auth.models import User

from Human.constants import STATIC_FOLDER, CITIES_TABLE
from Human.models import Group


def user_existed(name):
    if User.objects.filter(username=name).exists():
        return True
    return False


def validate_email(email):
    if User.objects.filter(email=email).exists():
        return False
    if len(email) > 7:
        if re.match("^.+\\@(\\[?)[a-zA-Z0-9\\-\\.]+\\.([a-zA-Z]{2,3}|[0-9]{1,3})(\\]?)$", email) is not None:
            return True
    return False


def validate_passwd(password, password2):
    if len(password) < 6 or password != password2:
        return False
    return True


def check_groupid(groupid):
    if groupid is None:
        return -2
    elif Group.objects.filter(id=groupid).exists():
        return groupid
    else:
        return 0


def group_name_existed(name):
    if Group.objects.filter(group_name=name).exists():
        return True
    return False


def check_profile(first_name, last_name, birth, sex, country, city, institution):
    if re.match("^[A-Za-z]+$", first_name) and re.match("^[A-Za-z]+$", last_name):
        if sex == 0 or sex == 1:
            if re.match("^(?:(?!0000)[0-9]{4}/(?:(?:0[1-9]|1[0-2])/(?:0[1-9]|1[0-9]|2[0-8])|"
                        "(?:0[13-9]|1[0-2])/(?:29|30)|(?:0[13578]|1[02])-31)|(?:[0-9]{2}(?:0[48]|"
                        "[2468][048]|[13579][26])|(?:0[48]|[2468][048]|[13579][26])00)/02/29)$", birth):
                if re.match("^[A-Za-z\s]+$", institution):
                    if country in CITIES_TABLE and city in CITIES_TABLE[country]:
                        return True
    return False


#######################################################################


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
        print 'Avatar create: ', e
        return -1
    return 0


def send_email(receiver, subject, text):
    sender = 'hevlhayt@foxmail.com'
    subject = subject
    smtpserver = 'smtp.qq.com'
    username = 'hevlhayt'
    password = 'cypxypypmmvxbcii'

    msgRoot = MIMEMultipart('related')
    msgRoot['From'] = sender
    msgRoot['To'] = receiver
    msgRoot['Subject'] = subject

    msgText = MIMEText(text, 'html', 'utf-8')
    msgRoot.attach(msgText)

    # fp = open('h:\\python\\1.jpg', 'rb')
    # msgImage = MIMEImage(fp.read())
    # fp.close()

    # msgImage.add_header('Content-ID', '<image1>')
    # msgRoot.attach(msgImage)

    smtp = smtplib.SMTP()
    smtp.connect(smtpserver)
    smtp.starttls()
    smtp.login(username, password)
    smtp.sendmail(sender, receiver, msgRoot.as_string())
    smtp.quit()


def logger_join(*args, **kwargs):
    if not args:
        return ''
    else:
        str_arg = ' '.join([str(arg) for arg in args])
        if not kwargs:
            return str_arg
        else:
            return str_arg + ' ' + ' '.join([k.upper()+':'+str(v) for k, v in kwargs.items()])


# if __name__ == '__main__':
    # create_avatar(9, 'Name Potter')
    # text = '<b>Some <i>HTML</i> text</b> and an image.<br><img src="cid:image1"><br>good!'
    # send_email('1017844578@qq.com', 'Test', text)

    # print logger_join('a', 'b', c='d', e='f')
