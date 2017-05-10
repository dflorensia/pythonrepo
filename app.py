# -*- coding: utf-8 -*-

#  Licensed under the Apache License, Version 2.0 (the "License"); you may
#  not use this file except in compliance with the License. You may obtain
#  a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#  WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#  License for the specific language governing permissions and limitations
#  under the License.

import os
import sys
import wsgiref.simple_server
from argparse import ArgumentParser

from builtins import bytes
from linebot import (LineBotApi, WebhookParser)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage
)
from linebot.utils import PY3

# get channel_secret and channel_access_token from your environment variable
channel_secret = os.getenv('LINE_CHANNEL_SECRET', 'e28f3b71efa37e176811715c749b74ac')
channel_access_token = os.getenv('LINE_CHANNEL_ACCESS_TOKEN','T5jiQgxmfY2VRiUC7DzhYwjwLQr5gD2FKddYkXYYmduIF6zxKfSk8rtOp7dzsZv4JKLoPSSzNzGN820Xi2nOcrqe5JPOqFw6ctWUtwnYWxRc5kBmyOXfeICPZJE50K2iGh8OYguGQa+4DvOFzYEtcQdB04t89/1O/w1cDnyilFU=')
if channel_secret is None:
    print('Specify LINE_CHANNEL_SECRET as environment variable.')
    sys.exit(1)
if channel_access_token is None:
    print('Specify LINE_CHANNEL_ACCESS_TOKEN as environment variable.')
    sys.exit(1)

line_bot_api = LineBotApi(channel_access_token)
parser = WebhookParser(channel_secret)
print('Florensia Unggul')

def application(environ, start_response):
    # check request path
    print(environ)
    print(environ['PATH_INFO'])
    print(environ['REQUEST_METHOD'])
    if environ['PATH_INFO'] != '/callback':
        start_response('404 Not Found', [])
        print('start_response 404:' + '404 Not Found');
        return create_body('Not Found')

    # check request method
    if environ['REQUEST_METHOD'] != 'POST':
        start_response('405 Method Not Allowed', [])
        print('start_response 405:' + '405 Method Not Allowed');
        return create_body('Method Not Allowed')

    # get X-Line-Signature header value
    signature = environ['HTTP_X_LINE_SIGNATURE']
    print('signature:' + signature)

    # get request body as text
    wsgi_input = environ['wsgi.input']
    content_length = int(environ['CONTENT_LENGTH'])
    body = wsgi_input.read(content_length).decode('utf-8')
    #print('wsgi_input:'+ wsgi_input);
    #print('content_length' + content_length);
    print('body' + body);
    # parse webhook body
    try:
        events = parser.parse(body, signature)
        #print('events' + events);
    except InvalidSignatureError:
        start_response('400 Bad Request', [])
        print('start_response 400:' + '400 Bad Request');
        return create_body('Bad Request')

    # if event is MessageEvent and message is TextMessage, then echo text
    for event in events:
        if not isinstance(event, MessageEvent):
            print('event MessageEvent' + MessageEvent)
            continue
        if not isinstance(event.message, TextMessage):
            print('event TextMessage' + TextMessage)
            continue

        print('event.reply_token:'+event.reply_token)
        print('event.message.text:'+event.message.text)
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=event.message.text)
        )

    start_response('200 OK', [])
    return create_body('OK')


def create_body(text):
    if PY3:
        print('PY3' + text)
        return [bytes(text, 'utf-8')]
    else:
        print('else' + text)
        return text


if __name__ == '__main__':
    arg_parser = ArgumentParser(
        usage='Usage: python ' + __file__ + ' [--port <port>] [--help]'
    )
    arg_parser.add_argument('-p', '--port', default=8000, help='port')
    options = arg_parser.parse_args()
    print('start server')
    httpd = wsgiref.simple_server.make_server('', options.port, application)
    httpd.serve_forever()
