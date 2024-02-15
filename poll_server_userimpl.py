import sys
import sqlite3
import ssl
import socket
import threading
import struct
import ctypes
from poll_message_api import *
import poll_database_ops

# Server side message handling implementations
class CreateUserImpl:
   def __init__(self, cl_sock, cl_cntxt, conn):
      self.sock = cl_sock
      self.cntxt = cl_cntxt
      self.conn = conn

   def invoke(self):
      print("ENTER CreateUserImpl", self.cntxt)
      userID, userName, userEmail, userPwd = recvCreateUserData(self.sock)
      print(userID, userName, userEmail, userPwd)

      ### LOCK USER TABLE
      res, reason = poll_database_ops.AddUser(self.conn, userID, userName, userEmail, userPwd)
      ### UNLOCK USER TABLE

      r = sendResponseMessage(self.sock, CREATE_USER, res, reason)
      print(r)
      print("EXIT CreateUserImpl", self.cntxt)
      return 0

class ChangeUserImpl:
   def __init__(self, cl_sock, cl_cntxt, conn):
      self.sock = cl_sock
      self.cntxt = cl_cntxt
      self.conn = conn
      self.op = CHANGE_USER
      self.userID = self.cntxt['userID']

   def invoke(self):
      print("ENTER ChangeUserImpl", self.cntxt)
      userName, userEmail, userPwd = recvChangeUserData(self.sock)
      if not poll_database_ops.AmILoggedIn(self.userID, self.cntxt):
         res = OP_FAILURE
         reason = REASON_NOT_LOGGED_IN
      else:
         userID = self.cntxt['userID']
         print(userID, userName, userEmail, userPwd)

         ### LOCK USER TABLE
         res, reason = poll_database_ops.ChangeUser(self.conn, userID, userName, userEmail, userPwd)
         ### UNLOCK USER TABLE

      r = sendResponseMessage(self.sock, self.op, res, reason)
      print(r)
      print("EXIT ChangeUserImpl", self.cntxt)
      return 0

class LoginUserImpl:
   def __init__(self, cl_sock, cl_cntxt, conn):
      self.sock = cl_sock
      self.cntxt = cl_cntxt
      self.conn = conn
      self.op = LOGIN_USER

   def invoke(self):
      print("ENTER LoginUserImpl", self.cntxt)
      userID, userPwd = recvLoginUserData(self.sock)
      print(userID, userPwd)
      ### LOCK USER TABLE
      if poll_database_ops.IsUserLoggedIn(userID):
         res = OP_FAILURE
         reason = REASON_ALREADY_LOGGED_IN
      else:
         res, reason = poll_database_ops.ValidateUser(self.conn, userID, userPwd)
         if res == OP_SUCCESS:
            res, reason = poll_database_ops.SetUserLoggedIn(userID, self.cntxt)
      ### UNLOCK USER TABLE

      r = sendResponseMessage(self.sock, self.op, res, reason)
      print(r)
      print("EXIT LoginUserImpl", self.cntxt)
      return 0

class LogoutUserImpl:
   def __init__(self, cl_sock, cl_cntxt, conn):
      self.sock = cl_sock
      self.cntxt = cl_cntxt
      self.conn = conn
      self.op = LOGOUT_USER
      self.userID = self.cntxt['userID']

   def invoke(self):
      print("ENTER LogoutUserImpl", self.cntxt)
      if not poll_database_ops.AmILoggedIn(self.userID, self.cntxt):
         r = sendResponseMessage(self.sock, self.op, OP_FAILURE, REASON_NOT_LOGGED_IN)
         print(r)
         return

      ### LOCK USER TABLE
      poll_database_ops.SetUserLoggedOut(self.cntxt)
      ### UNLOCK USER TABLE

      r = sendResponseMessage(self.sock, self.op, OP_SUCCESS, REASON_SUCCESS)
      print(r)
      print("EXIT LogoutUserImpl", self.cntxt)
      return 0

class InvalidMsgReqImpl:
   def __init__(self, cl_sock, cl_cntxt, conn):
      self.sock = cl_sock
      self.cntxt = cl_cntxt
      self.conn = conn

   def invoke(self):
      print("InvalidMsgReqImpl")
      return 0
