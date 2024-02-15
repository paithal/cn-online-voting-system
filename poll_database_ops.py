import sys
import sqlite3
from poll_message_api import *

POLLSERVER_DB = "poll_database.sqldb"

cl_contexts = []

def GetThreadContext(cl_sock):
   # CONTEXT LOCK
   cntxt = [c for c in cl_contexts if c['socket'] == cl_sock]
   # CONTEXT UNLOCK
   if cntxt:
      return cntxt[0]
   else:
      return None

def RemoveThreadContext(cl_sock):
   # CONTEXT LOCK
   cntxt = [i for i in cl_contexts if i['socket'] == cl_sock]
   cl_contexts.remove(cntxt[0])
   # CONTEXT UNLOCK

def AddThreadContext(cl_sock, cl_address, conn):
   # CONTEXT LOCK
   cl_contexts.append({'socket': cl_sock, 'address': cl_address, 'conn': conn, 'userID': None, 'logged_in': False})
   # CONTEXT UNLOCK

def ConnectDatabase():
   return sqlite3.connect(POLLSERVER_DB, check_same_thread=False)

def CreateTable(cur, tableName, fields):
   sqlCmd = f"CREATE TABLE {tableName} ({fields})"
   try:
      cur.execute(sqlCmd)
   except sqlite3.OperationalError as opErr:
      print(opErr)

def CreateTables(conn):
   cur = conn.cursor()
   CreateTable(cur, "user_table", "userID, userName, userEmail, password, primary key (userID)")
   CreateTable(cur, "poll_master_table", "pollID, description, status, ownerID, startDate, endDate, primary key (pollID)")
   CreateTable(cur, "poll_choices_table", "pollID, choiceID, choiceDescription, primary key (pollID, choiceID)")
   CreateTable(cur, "user_poll_selection_table", "pollID, userID, choiceID, primary key(pollID, userID)")

   return cur

def AddUser(conn, userID, userName, userEmail, userPwd):
   print(userID, userName, userEmail, userPwd)
   print(len(userID), len(userName), len(userEmail), len(userPwd))

   ### Add duplicate userID, valid userID checks
   if IsUserIDAlreadyExists(conn, userID):
      return (OP_FAILURE, REASON_DUPLICATE_USER_ID)

   res = conn.execute("INSERT INTO user_table VALUES(?, ?, ?, ?)", (userID, userName, userEmail, userPwd))
   print(res)
   res = conn.execute("commit")
   print(res)
   return (OP_SUCCESS, REASON_SUCCESS)

def ChangeUser(conn, userID, userName, userEmail, userPwd):
   print(userID, userName, userEmail, userPwd)
   print(len(userID), len(userName), len(userEmail), len(userPwd))

   ### Add valid user ID check

   res = conn.execute("UPDATE user_table SET userName=?, userEmail=?, password=? WHERE userID=?", (userName, userEmail, userPwd, userID))
   print(res)
   res = conn.execute("commit")
   print(res)
   return (OP_SUCCESS, REASON_SUCCESS)

def IsUserIDAlreadyExists(conn, userID):
   cur = conn.execute("SELECT userID from user_table WHERE userID=?", (userID,))
   data = cur.fetchall()
   if data:
      return True
   return False

def ValidateUser(conn, userID, userPwd):
   cur = conn.execute("SELECT password from user_table WHERE userID=?", (userID,))
   data = cur.fetchall()
   print(userID, userPwd, data)
   if not data:
      res = OP_FAILURE
      reason = REASON_USER_ID_NOT_FOUND
   elif data[0][0] != userPwd:
      res = OP_FAILURE
      reason = REASON_INCORRECT_PWD
   else:
      res = OP_SUCCESS
      reason = REASON_SUCCESS

   return (res, reason)

def AmILoggedIn(userID, cntxt):
   return cntxt['userID'] == userID and cntxt['logged_in']

def IsUserLoggedIn(userID):
   # CONTEXT LOCK
   found = [c for c in cl_contexts if c['userID'] == userID and c['logged_in']]
   # CONTEXT UNLOCK
   if found:
      return True
   return False

def SetUserLoggedIn(userID, cntxt):
   # CONTEXT LOCK 
   if IsUserLoggedIn(userID):
      ret = (OP_FAILURE, REASON_ALREADY_LOGGED_IN)
   else:
      cntxt['userID'] = userID
      cntxt['logged_in'] = True
      ret = (OP_SUCCESS, REASON_SUCCESS)
   # CONTEXT UNLOCK
   return ret

def SetUserLoggedOut(cntxt):
   # CONTEXT LOCK
   cntxt['userID'] = None
   cntxt['logged_in'] = False
   # CONTEXT UNLOCK

def AddPoll(conn, userID, pollID, pollName, openDateTime, closeDateTime, pollChoices):
   print(conn, userID, pollID, pollName, openDateTime, closeDateTime, pollChoices)
   
   try:
      cur = conn.cursor()
      cur.execute("INSERT INTO poll_master_table VALUES(?, ?, ?, ?, ?, ?)", pollID, pollName, 'C', userID, openDateTime, closeDateTime)
      cur.executemany("INSERT INTO poll_choices_table VALUES(?, ?, ?)", pollChoices)
      conn.commit()
      res, reason = OP_SUCCESS, REASON_SUCCESS
   except sqlite3.IntegrityError as opErr:
      if opErr.sqlite_errorcode == sqlite3.SQLITE_CONSTRAINT_PRIMARYKEY:
         res, reason = OP_FAILURE, REASON_DUP_POLL_DATA
      else:
         res, reason = OP_FAILURE, REASON_DATABASE_ERROR
      conn.rollback()
   
   return res

def AddPollChoices(conn, userID, pollID, pollChoices):
   print(conn, userID, pollID, pollChoices)
   return (OP_FAILURE, REASON_UNKNOWN)

def RemovePollChoices(conn, userID, pollID, pollChoices):
   print(conn, userID, pollID, pollChoices)
   return (OP_FAILURE, REASON_UNKNOWN)

def SetPollStatus(conn, userID, pollID, pollStatus):
   print(conn, userID, pollID, pollStatus)
   return (OP_FAILURE, REASON_UNKNOWN)
