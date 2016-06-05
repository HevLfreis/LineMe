#!/usr/bin/env python
# coding: utf-8
# created by hevlhayt@foxmail.com 
# Date: 2016/5/25 
# Time: 10:44
#
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import os
import random
import smtplib
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

# if __name__ == '__main__':
#     # create_avatar(9, 'Name Potter')
#     text = '<b>Some <i>HTML</i> text</b> and an image.<br><img src="cid:image1"><br>good!'
#     send_email('1017844578@qq.com', 'Test', text)
