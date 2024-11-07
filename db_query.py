import pprint
import sqlite3

conn = sqlite3.connect('poll_database.sqldb')
cur = conn.execute('select * from user_table')
print('user_table : ')
pprint.pprint(cur.fetchall())

cur = conn.execute('select * from poll_master_table')
print('poll_master_table : ')
pprint.pprint(cur.fetchall())

cur = conn.execute('select * from poll_choices_table')
print('poll_choices_table : ')
pprint.pprint(cur.fetchall())

cur = conn.execute('select * from user_poll_selection_table')
print('user_poll_selection_table : ')
pprint.pprint(cur.fetchall())

