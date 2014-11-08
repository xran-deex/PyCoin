import sqlite3, os
from TransactionManager.transaction import Transaction
#from BlockManager.block import Block

class DB:
  
  db_file = 'db.db'
  
  def __init__(self):
    
    db_is_new = not os.path.exists(DB.db_file)
    self.conn = sqlite3.connect(DB.db_file)
    
    if db_is_new:
      print('Creating schema')
      sql = '''create table if not exists OBJECTS(
      ID CHAR(64) PRIMARY KEY,
      PAYLOAD BLOB,
      TYPE CHAR(5),
      TIMESTAMP DATETIME DEFAULT CURRENT_TIMESTAMP
      );'''
      self.conn.execute(sql)
    else:
      print('Schema exists')
      
  def getTransactionByHash(self, hash):
    trans = self.conn.execute('SELECT * FROM OBJECTS WHERE ID = ?', [hash])
    return Transaction().unpack(trans)
    
  def getAllTransactions(self):
    trans = self.conn.execute('SELECT * FROM OBJECTS WHERE TYPE = ?', ['TRANS'])
    raw_list = trans.fetchall()
    result = []
    for item in raw_list:
      t = Transaction()
      t.unpack(item[1])
      result.append(t)
    return result
    
  def insertTransaction(self, trans):
    t = trans.build_struct()
    self.conn.execute('insert into OBJECTS (ID, PAYLOAD, TYPE) values (?, ?, ?)', [trans.get_hash(), t, 'TRANS'])
    self.conn.commit()
    
  def getAllBlocks(self):
    blocks = self.conn.execute('SELECT * FROM OBJECTS WHERE TYPE = ?', ['BLOCK'])
    raw_list = blocks.fetchall()
    result = []
    for item in raw_list:
      b = Block()
      b.unpack(item[1])
      result.append(b)
    return result
    
  def getLatestBlock(self):
    block = self.conn.execute('SELECT * FROM OBJECTS WHERE TYPE = ? ORDER BY TIMESTAMP LIMIT 1', ['TRANS'])
    raw_list = block.fetchall()
    return raw_list[0]
    
if __name__ == '__main__':
  from keystore import KeyStore
  db = DB()
  t = Transaction()
  t.add_input(Transaction.Input(100, b''))
  t.add_output(Transaction.Output(20, KeyStore.getPublicKey()))
  db.insertTransaction(t)
  t = Transaction()
  t.add_input(Transaction.Input(17, b''))
  t.add_output(Transaction.Output(7, KeyStore.getPublicKey()))
  db.insertTransaction(t)
  print(db.getAllTransactions())