import sys
import sqlite3
import ssl
import socket
import threading
import poll_server_userimpl
import poll_server_pollmasterimpl
import poll_database_ops
from poll_message_api import *

POLLSERVER_HOST_PORT = ('127.0.0.1', 10000)
POLLSERVER_NUM_WAIT_REQS = 25

# message to function callback map
msgType2CBMap = {
   CREATE_USER: poll_server_userimpl.CreateUserImpl,
   CHANGE_USER: poll_server_userimpl.ChangeUserImpl,
   LOGIN_USER: poll_server_userimpl.LoginUserImpl,
   LOGOUT_USER: poll_server_userimpl.LogoutUserImpl,
   CREATE_POLL: poll_server_pollmasterimpl.CreatePollImpl,
   POLL_ADD_CHOICES: poll_server_pollmasterimpl.AddPollChoicesImpl,
   POLL_REMOVE_CHOICES: poll_server_pollmasterimpl.RemovePollChoicesImpl,
   POLL_SET_STATUS: poll_server_pollmasterimpl.SetPollStatusImpl,
}

def ThreadMain(cl_sock):
   print(cl_sock)
   cntxt = poll_database_ops.GetThreadContext(cl_sock)
   conn = cntxt['conn']
   print(cntxt)
   while True:
      msgBuf = cl_sock.recv(ctypes.sizeof(PollMsgHdr))
      if not msgBuf:
         break
      msgHdr = PollMsgHdr.from_buffer(bytearray(msgBuf))
      msgType = socket.ntohs(msgHdr.msgType)
      msgFlags = socket.ntohs(msgHdr.flags)
      print(msgType, msgFlags)
      if msgType in msgType2CBMap:
         if msgType2CBMap[msgType](cl_sock, cntxt, conn).invoke():
            break
      else:
         InvalidMsgReqImpl(cl_sock, cntxt, conn).invoke()
         break
   poll_database_ops.RemoveThreadContext(cl_sock)
   cl_sock.close()

# start a new thread for serviving the client socket
def start_new_thread(cl_sock, cl_address, conn):
   ct = threading.Thread(target=ThreadMain, args=(cl_sock,))
   if ct:
      poll_database_ops.AddThreadContext(cl_sock, cl_address, conn)
      ct.start()

# connect to database
conn = poll_database_ops.ConnectDatabase()
if not conn:
   sys.exit(1)

# create tables if needed
cur = poll_database_ops.CreateTables(conn)
if not cur:
   sys.exit(1)

# create server socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.bind(POLLSERVER_HOST_PORT)
sock.listen(POLLSERVER_NUM_WAIT_REQS)

while True:
   # wait for connection from client
   (cl_sock, cl_address) = sock.accept()
   start_new_thread(cl_sock, cl_address, conn)

sock.close()
