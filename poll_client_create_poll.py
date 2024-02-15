import sys
import sqlite3
import ssl
import socket
import struct
from poll_message_api import *

POLLSERVER_HOST_PORT = ('127.0.0.1', 10000)

# create server socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect(POLLSERVER_HOST_PORT)

r = sendLoginUserReqMsg(sock, "p123", "pass_p123123_word")
print(r)

msgType, flags, status, reason = recvResponseMessage(sock)
print(GetMsgTypeString(msgType), flags, status, reason, GetReasonString(reason))

r = sendCreatePollReqMsg(sock, "poll1", "POLL 1", "", "", [('A', "Choice A")])
print(r)

msgType, flags, status, reason = recvResponseMessage(sock)
print(GetMsgTypeString(msgType), flags, status, reason, GetReasonString(reason))

sock.close()
