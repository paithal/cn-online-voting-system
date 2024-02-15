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

r = sendLoginUserReqMsg(sock, "p123", "pass_p123_word")
print(r)

msgType, flags, status, reason = recvResponseMessage(sock)
print(GetMsgTypeString(msgType), flags, status, reason, GetReasonString(reason))

r = sendLoginUserReqMsg(sock, "p123", "pass_p123123_word")
print(r)

msgType, flags, status, reason = recvResponseMessage(sock)
print(GetMsgTypeString(msgType), flags, status, reason, GetReasonString(reason))

r = sendLoginUserReqMsg(sock, "p123", "pass_p123_word")
print(r)

msgType, flags, status, reason = recvResponseMessage(sock)
print(GetMsgTypeString(msgType), flags, status, reason, GetReasonString(reason))

# create server socket
sock1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock1.connect(POLLSERVER_HOST_PORT)

r = sendLoginUserReqMsg(sock1, "p123", "pass_p123_word")
print(r)

msgType, flags, status, reason = recvResponseMessage(sock1)
print(GetMsgTypeString(msgType), flags, status, reason, GetReasonString(reason))

sock1.close()

r = sendLogoutUserReqMsg(sock)
print(r)

msgType, flags, status, reason = recvResponseMessage(sock)
print(GetMsgTypeString(msgType), flags, status, reason, GetReasonString(reason))
sock.close()
