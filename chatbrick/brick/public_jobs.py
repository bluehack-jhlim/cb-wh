import logging

import blueforge.apis.telegram as tg
import requests
import datetime
from blueforge.apis.facebook import Message, ImageAttachment, QuickReply, QuickReplyTextItem

from chatbrick.util import get_items_from_xml

logger = logging.getLogger(__name__)

BRICK_DEFAULT_IMAGE = 'https://www.chatbrick.io/api/static/brick/img_brick_07_001.png'


class PublicJobs(object):
    def __init__(self, fb, brick_db):
        self.brick_db = brick_db
        self.fb = fb

    async def facebook(self, command):
        if command == 'get_started':
            send_message = [
                Message(
                    attachment=ImageAttachment(
                        url=BRICK_DEFAULT_IMAGE
                    )
                ),
                Message(
                    text='인사혁신처에서 제공하는 "공공취업정보검색 서비스"에요.'
                )
            ]
            await self.fb.send_messages(send_message)
            await self.brick_db.save()
        elif command == 'final':
            input_data = await self.brick_db.get()
            keyword = input_data['store'][0]['value']
            to = datetime.datetime.today()
            today = '%d-%02d-%02d' % (to.year, to.month, to.day)
            res = requests.get(
                url='http://openapi.mpm.go.kr/openapi/service/RetrievePblinsttEmpmnInfoService/getList?serviceKey=%s&pageNo=1&startPage=1&numOfRows=20&pageSize=20&Pblanc_ty=e01&Begin_de=%s&Sort_order=1&Kwrd=%s' % (
                    input_data['data']['api_key'], today, keyword))

            items = get_items_from_xml(res)

            if len(items) == 0:
                send_message = [
                    Message(
                        text='조회된 결과가 없습니다.',
                        quick_replies=QuickReply(
                            quick_reply_items=[
                                QuickReplyTextItem(
                                    title='다른 키워드검색',
                                    payload='brick|public_jobs|get_started'
                                )
                            ]
                        )
                    )
                ]
            else:
                sending_message = []
                for item in items:
                    sending_message.append('*{title}*\n{deptName}\n{regdate} ~ {enddate}'.format(**item))
                send_message = [
                    Message(
                        text='조회된 결과에요'
                    ),
                    Message(
                        text='\n\n'.join(sending_message),
                        quick_replies=QuickReply(
                            quick_reply_items=[
                                QuickReplyTextItem(
                                    title='다른 키워드검색',
                                    payload='brick|public_jobs|get_started'
                                )
                            ]
                        )
                    )
                ]

            await self.brick_db.delete()
            await self.fb.send_messages(send_message)
        return None

    async def telegram(self, command):
        if command == 'get_started':
            send_message = [
                tg.SendPhoto(
                    photo=BRICK_DEFAULT_IMAGE
                ),
                tg.SendMessage(
                    text='인사혁신처에서 제공하는 "공공취업정보검색 서비스"에요.'
                )

            ]
            await self.fb.send_messages(send_message)
            await self.brick_db.save()
        elif command == 'final':
            input_data = await self.brick_db.get()
            keyword = input_data['store'][0]['value']
            to = datetime.datetime.today()
            today = '%d-%02d-%02d' % (to.year, to.month, to.day)
            res = requests.get(
                url='http://openapi.mpm.go.kr/openapi/service/RetrievePblinsttEmpmnInfoService/getList?serviceKey=%s&pageNo=1&startPage=1&numOfRows=20&pageSize=20&Pblanc_ty=e01&Begin_de=%s&Sort_order=1&Kwrd=%s' % (
                    input_data['data']['api_key'], today, keyword))

            items = get_items_from_xml(res)

            if len(items) == 0:
                send_message = [
                    tg.SendMessage(
                        text='조회된 결과가 없습니다.',
                        reply_markup=tg.MarkUpContainer(
                            inline_keyboard=[
                                [
                                    tg.CallbackButton(
                                        text='다른 키워드검색',
                                        callback_data='BRICK|public_jobs|get_started'
                                    )
                                ]
                            ]
                        )
                    )
                ]
            else:
                sending_message = []
                for item in items:
                    sending_message.append('*{title}*\n{deptName}\n{regdate} ~ {enddate}'.format(**item))

                send_message = [
                    tg.SendMessage(
                        text='조회된 결과에요.'
                    ),
                    tg.SendMessage(
                        text='\n\n'.join(sending_message),
                        parse_mode='Markdown',
                        reply_markup=tg.MarkUpContainer(
                            inline_keyboard=[
                                [
                                    tg.CallbackButton(
                                        text='다른 키워드검색',
                                        callback_data='BRICK|public_jobs|get_started'
                                    )
                                ]
                            ]
                        )
                    )
                ]

            await self.brick_db.delete()
            await self.fb.send_messages(send_message)
        return None
