# Author: @freyley.leyva
import os, sqlite3
DB_PATH=os.path.join(os.path.dirname(__file__),"..","mixteca_bank.db")
def init_db():
    c=sqlite3.connect(DB_PATH); cur=c.cursor(); cur.execute('CREATE TABLE IF NOT EXISTS accounts (user_id TEXT PRIMARY KEY, full_name TEXT NOT NULL, account_number TEXT NOT NULL, balance REAL NOT NULL, status TEXT NOT NULL)'); cur.execute('DELETE FROM accounts'); cur.executemany('INSERT INTO accounts VALUES (?,?,?,?,?)',[("CLI-001","Alex Rivera","012180001111222233",45200.50,"ACTIVA"),("CLI-002","Sam Torres","012180009876543210",1250.00,"RESTRINGIDA")]); c.commit(); c.close()
def get_account_by_user(user_id):
    c=sqlite3.connect(DB_PATH); r=c.execute('SELECT user_id,full_name,account_number,balance,status FROM accounts WHERE user_id=?',(user_id,)).fetchone(); c.close()
    return dict(zip(["user_id","full_name","account_number","balance","status"],r)) if r else None
