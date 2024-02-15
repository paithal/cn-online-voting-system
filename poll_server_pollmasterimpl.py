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
class CreatePollImpl:
   def __init__(self, cl_sock, cl_cntxt, conn):
      self.sock = cl_sock
      self.cntxt = cl_cntxt
      self.conn = conn
      self.userID = self.cntxt['userID']
      self.op = CREATE_POLL

   def invoke(self):
      print("ENTER CreatePollImpl", self.cntxt)
      pollID, pollName, openDateTime, closeDateTime, pollChoices = recvCreatePollData(self.sock)
      print(pollID, pollName, openDateTime, closeDateTime, pollChoices)

      if not poll_database_ops.AmILoggedIn(self.userID, self.cntxt):
         res = OP_FAILURE
         reason = REASON_NOT_LOGGED_IN
      else:
         ### LOCK POLL TABLE
         res, reason = poll_database_ops.AddPoll(self.conn, self.userID, pollID, pollName, openDateTime, closeDateTime, pollChoices)
         ### UNLOCK POLL TABLE

      r = sendResponseMessage(self.sock, self.op, res, reason)
      print(r)
      print("EXIT CreatePollImpl", self.cntxt)
      return 0

class AddPollChoicesImpl:
   def __init__(self, cl_sock, cl_cntxt, conn):
      self.sock = cl_sock
      self.cntxt = cl_cntxt
      self.conn = conn
      self.op = POLL_ADD_CHOICES
      self.userID = self.cntxt['userID']

   def invoke(self):
      print("ENTER AddPollChoicesImpl", self.cntxt)
      pollID, pollChoices = recvAddPollChoicesData(self.sock)
      if not poll_database_ops.AmILoggedIn(self.userID, self.cntxt):
         res = OP_FAILURE
         reason = REASON_NOT_LOGGED_IN
      else:
         ### LOCK POLL TABLE
         res, reason = poll_database_ops.AddPollChoices(self.conn, pollID, self.userID, pollChoices)
         ### UNLOCK POLL TABLE

      r = sendResponseMessage(self.sock, self.op, res, reason)
      print(r)
      print("EXIT AddPollChoicesImpl", self.cntxt)
      return 0

class RemovePollChoicesImpl:
   def __init__(self, cl_sock, cl_cntxt, conn):
      self.sock = cl_sock
      self.cntxt = cl_cntxt
      self.conn = conn
      self.op = POLL_REMOVE_CHOICES
      self.userID = self.cntxt['userID']

   def invoke(self):
      print("ENTER RemovePollChoicesImpl", self.cntxt)
      pollID, pollChoices = recvRemovePollChoicesData(self.sock)
      if not poll_database_ops.AmILoggedIn(self.userID, self.cntxt):
         res = OP_FAILURE
         reason = REASON_NOT_LOGGED_IN
      else:
         ### LOCK POLL TABLE
         res, reason = poll_database_ops.RemovePollChoices(self.conn, pollID, self.userID, pollChoices)
         ### UNLOCK POLL TABLE

      r = sendResponseMessage(self.sock, self.op, res, reason)
      print(r)
      print("EXIT RemovePollChoicesImpl", self.cntxt)
      return 0

class SetPollStatusImpl:
   def __init__(self, cl_sock, cl_cntxt, conn):
      self.sock = cl_sock
      self.cntxt = cl_cntxt
      self.conn = conn
      self.op = POLL_SET_STATUS
      self.userID = self.cntxt['userID']

   def invoke(self):
      print("ENTER SetPollStatusImpl", self.cntxt)
      pollID, pollStatus = recvSetPollStatusData(self.sock)
      if not poll_database_ops.AmILoggedIn(self.userID, self.cntxt):
         res = OP_FAILURE
         reason = REASON_NOT_LOGGED_IN
      else:
         ### LOCK POLL TABLE
         res, reason = poll_database_ops.SetPollStatus(self.conn, pollID, self.userID, pollStatus)
         ### UNLOCK POLL TABLE

      r = sendResponseMessage(self.sock, self.op, res, reason)
      print(r)
      print("EXIT SetPollStatusImpl", self.cntxt)
      return 0

class InvalidMsgReqImpl:
   def __init__(self, cl_sock, cl_cntxt, conn):
      self.sock = cl_sock
      self.cntxt = cl_cntxt
      self.conn = conn

   def invoke(self):
      print("InvalidMsgReqImpl")
      return 0
