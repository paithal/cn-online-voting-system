import sys
import sqlite3
import ssl
import socket
import threading
import struct
import ctypes
import hashlib

# Status codes
OP_SUCCESS = 0
OP_FAILURE = 1

# Reason codes
REASON_SUCCESS = 0
REASON_NOT_LOGGED_IN = 1
REASON_ALREADY_LOGGED_IN = 2
REASON_INCORRECT_PWD = 3
REASON_DUPLICATE_USER_ID = 4
REASON_USER_ID_NOT_FOUND = 5
REASON_DUP_POLL_DATA = 6
REASON_DATABASE_ERROR = 7
REASON_UNKNOWN = 99

# Message types
CREATE_USER = 1
CHANGE_USER = 2

LOGIN_USER = 3
LOGOUT_USER = 4

CREATE_POLL = 5
POLL_ADD_CHOICES = 6
POLL_REMOVE_CHOICES = 7
POLL_SET_STATUS = 8

USER_POLL_MAKE_SELECTION = 9
USER_POLL_GET_RESULTS = 10

# msg type strings
msgtype2stringMap = {
   CREATE_USER: "Create User Operation",
   CHANGE_USER: "Change User Operation",
   LOGIN_USER: "Login User Operation",
   LOGOUT_USER: "Logout User Operation",
   CREATE_POLL: "Create Poll Operation",
   POLL_ADD_CHOICES: "Add Poll Choices Operation",
   POLL_REMOVE_CHOICES: "Remove Poll Choices Operation",
   POLL_SET_STATUS: "Set Poll Status Operation",
   USER_POLL_MAKE_SELECTION: "Make Poll Section Operation",
   USER_POLL_GET_RESULTS: "Get Poll Results Operation",
}

def GetMsgTypeString(msgType):
   if msgType in msgtype2stringMap:
      return msgtype2stringMap[msgType]
   else:
      return 'Unknown'

# Reason strings
reason2stringMap = {
   REASON_SUCCESS: "Success.",
   REASON_NOT_LOGGED_IN: "User has not logged-in. Operation requires the user to be logged-in in the current session.",
   REASON_ALREADY_LOGGED_IN: "User already logged-in. Only one login is allowed per user at a time.",
   REASON_INCORRECT_PWD: "Incorrect password. Check the spelling.",
   REASON_DUPLICATE_USER_ID: "User ID already exist. Choose a different one",
   REASON_USER_ID_NOT_FOUND: "Unrecognized User ID. Check the User ID spelling",
   REASON_DUP_POLL_DATA: "Either pollID already exists or pollID + choiceID combination already exists",
   REASON_DATABASE_ERROR: "Internal database error",
   REASON_UNKNOWN: "Unknown reason",
}

def GetReasonString(reason):
   if reason in reason2stringMap:
      return reason2stringMap[reason]
   else:
      return 'Unknown'

# Message data

# Create user request
USER_ID_SIZE = 20
USER_NAME_SIZE = 30
USER_EMAIL_SIZE = 30
USER_PWD_SIZE = 30

class PollMsgHdr(ctypes.Structure):
    _fields_ = [('msgType', ctypes.c_uint16),
                ('flags', ctypes.c_uint16)]
    _pack_ = 1

class PollCreateUserData(ctypes.Structure):
    _fields_ = [('userID', ctypes.c_char * USER_ID_SIZE),
                ('userName', ctypes.c_char * USER_NAME_SIZE),
                ('userEmail', ctypes.c_char * USER_EMAIL_SIZE),
                ('userPwd', ctypes.c_char * USER_PWD_SIZE)]
    _pack_ = 1

class PollCreateUserDataReq(ctypes.Structure):
    _fields_ = [('hdr', PollMsgHdr),
                ('data', PollCreateUserData)]
    _pack_ = 1

def sendCreateUserReqMsg(sock, userID, userName, userEmail, userPwd):
   createUserDataReq = PollCreateUserDataReq()
   createUserDataReq.hdr.msgType = socket.htons(CREATE_USER)
   createUserDataReq.hdr.flags = socket.htons(1)
   createUserDataReq.data.userID = userID.encode()
   createUserDataReq.data.userName = userName.encode()
   createUserDataReq.data.userEmail = userEmail.encode()
   createUserDataReq.data.userPwd = userPwd.encode()
   return sock.send(createUserDataReq)

def recvCreateUserData(sock):
   msgBuf = sock.recv(ctypes.sizeof(PollCreateUserData))
   if  not msgBuf:
      return (None, None, None, None)
   createUserData = PollCreateUserData.from_buffer(bytearray(msgBuf))
   userID = createUserData.userID.decode().rstrip('\x00')
   userName = createUserData.userName.decode().rstrip('\x00')
   userEmail = createUserData.userEmail.decode().rstrip('\x00')
   userPwd = hashlib.sha256(createUserData.userPwd).hexdigest()

   return (userID, userName, userEmail, userPwd)

# Message response
class PollResponseMessage(ctypes.Structure):
    _fields_ = [('hdr', PollMsgHdr),
                ('status', ctypes.c_uint8),
                ('reason', ctypes.c_uint32)]
    _pack_ = 1

def sendResponseMessage(sock, msgType, status, reason):
   msgResp = PollResponseMessage()
   msgResp.hdr.msgType = socket.htons(msgType)
   msgResp.hdr.flags = socket.htons(2)
   msgResp.status = socket.htons(status)
   msgResp.reason = socket.htons(reason)
   return sock.send(msgResp)

def recvResponseMessage(sock):
   msgBuf = sock.recv(ctypes.sizeof(PollResponseMessage))
   if  not msgBuf:
      return (None, None, None, None)
   msgResp = PollResponseMessage.from_buffer(bytearray(msgBuf))
   return (socket.ntohs(msgResp.hdr.msgType), socket.ntohs(msgResp.hdr.flags), socket.ntohs(msgResp.status), socket.ntohs(msgResp.reason))

# Poll change user
class PollChangeUserData(ctypes.Structure):
    _fields_ = [('userName', ctypes.c_char * USER_NAME_SIZE),
                ('userEmail', ctypes.c_char * USER_EMAIL_SIZE),
                ('userPwd', ctypes.c_char * USER_PWD_SIZE)]
    _pack_ = 1

class PollChangeUserDataReq(ctypes.Structure):
    _fields_ = [('hdr', PollMsgHdr),
                ('data', PollChangeUserData)]
    _pack_ = 1

def sendChangeUserReqMsg(sock, userID, userName, userEmail, userPwd):
   changeUserDataReq = PollChangeUserDataReq()
   changeUserDataReq.hdr.msgType = socket.htons(CHANGE_USER)
   changeUserDataReq.hdr.flags = socket.htons(1)
   changeUserDataReq.data.userName = userName.encode()
   changeUserDataReq.data.userEmail = userEmail.encode()
   changeUserDataReq.data.userPwd = userPwd.encode()
   return sock.send(changeUserDataReq)

def recvChangeUserData(sock):
   msgBuf = sock.recv(ctypes.sizeof(PollChangeUserData))
   if  not msgBuf:
      return (None, None, None)
   changeUserData = PollChangeUserData.from_buffer(bytearray(msgBuf))
   userName = changeUserData.userName.decode().rstrip('\x00')
   userEmail = changeUserData.userEmail.decode().rstrip('\x00')
   userPwd = hashlib.sha256(changeUserData.userPwd).hexdigest()

   return (userName, userEmail, userPwd)

# Poll login user
class PollLoginUserData(ctypes.Structure):
    _fields_ = [('userID', ctypes.c_char * USER_ID_SIZE),
                ('userPwd', ctypes.c_char * USER_PWD_SIZE)]
    _pack_ = 1

class PollLoginUserDataReq(ctypes.Structure):
    _fields_ = [('hdr', PollMsgHdr),
                ('data', PollLoginUserData)]
    _pack_ = 1

def sendLoginUserReqMsg(sock, userID, userPwd):
   loginUserDataReq = PollLoginUserDataReq()
   loginUserDataReq.hdr.msgType = socket.htons(LOGIN_USER)
   loginUserDataReq.hdr.flags = socket.htons(1)
   loginUserDataReq.data.userID = userID.encode()
   loginUserDataReq.data.userPwd = userPwd.encode()
   return sock.send(loginUserDataReq)

def recvLoginUserData(sock):
   msgBuf = sock.recv(ctypes.sizeof(PollLoginUserData))
   if  not msgBuf:
      return (None, None)
   loginUserData = PollLoginUserData.from_buffer(bytearray(msgBuf))
   userID = loginUserData.userID.decode().rstrip('\x00')
   userPwd = hashlib.sha256(loginUserData.userPwd).hexdigest()

   return (userID, userPwd)

# Poll logout user
class PollLogoutUserData(ctypes.Structure):
    _fields_ = [('userID', ctypes.c_char * USER_ID_SIZE),
                ('userPwd', ctypes.c_char * USER_PWD_SIZE)]
    _pack_ = 1

class PollLogoutUserDataReq(ctypes.Structure):
    _fields_ = [('hdr', PollMsgHdr)]
    _pack_ = 1

def sendLogoutUserReqMsg(sock):
   logoutUserDataReq = PollLogoutUserDataReq()
   logoutUserDataReq.hdr.msgType = socket.htons(LOGOUT_USER)
   logoutUserDataReq.hdr.flags = socket.htons(1)
   return sock.send(logoutUserDataReq)

# Create poll

class PollChoiceData(ctypes.Structure):
    _fields_ = [('choiceID', ctypes.c_char * USER_ID_SIZE),
                ('choiceName', ctypes.c_char * USER_PWD_SIZE)]
    _pack_ = 1

class CreatePollData(ctypes.Structure):
    _fields_ = [('pollID', ctypes.c_char * USER_ID_SIZE),
                ('pollName', ctypes.c_char * USER_PWD_SIZE),
                ('openDateTime', ctypes.c_char * USER_PWD_SIZE),
                ('closeDateTime', ctypes.c_char * USER_PWD_SIZE),
                ('pollStatus', ctypes.c_char),
                ('numChoices', ctypes.c_uint16)]
    _pack_ = 1

class CreatePollDataReq(ctypes.Structure):
    _fields_ = [('hdr', PollMsgHdr),
                ('data', CreatePollData)]
    _pack_ = 1

def sendCreatePollReqMsg(sock, pollID, pollName, openDateTime, closeDateTime, pollChoices):
   createPollDataReq = CreatePollDataReq()
   createPollDataReq.hdr.msgType = socket.htons(CREATE_POLL)
   createPollDataReq.hdr.flags = socket.htons(1)
   createPollDataReq.data.pollID = pollID.encode()
   createPollDataReq.data.pollName = pollName.encode()
   createPollDataReq.data.openDateTime = openDateTime.encode()
   createPollDataReq.data.closeDateTime = closeDateTime.encode()
   createPollDataReq.data.numChoices = socket.htons(len(pollChoices))

   numChoices = len(pollChoices)
   pollChoiceData = (PollChoiceData * numChoices)()
   for i in range(0, numChoices):
      pollChoiceData[i].choiceID = pollChoices[i][0].encode()
      pollChoiceData[i].choiceName = pollChoices[i][1].encode()
      
   print(createPollDataReq, ctypes.sizeof(createPollDataReq))
   print(pollChoiceData, ctypes.sizeof(pollChoiceData))

   numBytes = sock.send(createPollDataReq)
   if numBytes == ctypes.sizeof(createPollDataReq):
      return numBytes + sock.send(pollChoiceData)
   else:
      return 0

def recvCreatePollData(sock):
   msgBuf = sock.recv(ctypes.sizeof(CreatePollData))
   if  not msgBuf:
      return (None, None, None, None, None)
   createPollData = CreatePollData.from_buffer(bytearray(msgBuf))
   pollID = createPollData.pollID.decode().rstrip('\x00')
   pollName = createPollData.pollName.decode().rstrip('\x00')
   openDateTime = createPollData.openDateTime.decode().rstrip('\x00')
   closeDateTime = createPollData.closeDateTime.decode().rstrip('\x00')
   pollStatus = createPollData.pollStatus.decode().rstrip('\x00')
   numChoices = socket.ntohs(createPollData.numChoices)

   msgBuf = sock.recv(ctypes.sizeof(PollChoiceData) * numChoices)
   if  not msgBuf:
      return (None, None, None, None, None)

   pollChoiceData = (PollChoiceData * numChoices).from_buffer(bytearray(msgBuf))
   pollChoices = []
   for i in range(0, numChoices):
      choiceID = pollChoiceData[i].choiceID.decode().rstrip('\x00')
      choiceName = pollChoiceData[i].choiceName.decode().rstrip('\x00')
      pollChoices.append((choiceID, choiceName))

   return (pollID, pollName, openDateTime, closeDateTime, pollChoices)
