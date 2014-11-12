import sqlite3, os
from TransactionManager.transaction import Transaction
from TransactionManager.coinbase import CoinBase
#from BlockManager.block import Block

class DB:
  
  db_file = 'db.db'
  
  def __init__(self):
    """ Initializes the database access object
        If the database doesn't exist, it is created, otherwise we just connect.
    """
    db_is_new = not os.path.exists(DB.db_file)
    self.conn = sqlite3.connect(DB.db_file)
    
    # if there is no database file, create the db schema
    if db_is_new:
      print('Creating schema')
      sql = '''create table if not exists OBJECTS(
      ID CHAR(64) PRIMARY KEY,
      PAYLOAD BLOB,
      OWNER CHAR(64) NULL,
      TYPE CHAR(5),
      TIMESTAMP DATETIME DEFAULT CURRENT_TIMESTAMP
      );'''
      self.conn.execute(sql)
      
  def getTransactionByHash(self, hash):
    """ Retrieves a transaction by hash
    
    Param:
      hash: (SHA256 hash) hash of the transaction to be retrieved
      
    Return: (Transaction) the transaction object or None if not found
    """
    trans = self.conn.execute('SELECT * FROM OBJECTS WHERE ID = ?', [hash])
    if not trans:
      return trans
    return Transaction().unpack(trans)
    
  def getAllTransactions(self):
    """ Retrieves every transaction stored in the database
    
    Return: (list) Transaction objects
    """
    trans = self.conn.execute('SELECT * FROM OBJECTS WHERE TYPE = ?', ['TRANS'])
    raw_list = trans.fetchall()
    result = []
    for item in raw_list:
      t = Transaction()
      t.unpack(item[1])
      result.append(t)
    return result
    
  def insertUnspentOutput(self, out):
    """ Inserts an unspent output into the database
    
    Param:
      out: (Transaction.Output) the output to be inserted
    """
    id = out.hash_key()
    self.conn.execute('insert into OBJECTS (ID, PAYLOAD, TYPE, OWNER) values (?, ?, ?, ?)', [out.hash_output(), out.pack(bytearray()), 'UNSPT', id])
    self.conn.commit()
    
  def insertTransaction(self, trans):
    """ Inserts a transaction into the database
    
    Param:
      trans: (Transaction) the transaction to be inserted
    """
    t = trans.build_struct()
    
    ### NOT SURE IF THIS SHOULD GO HERE
    #o = trans.get_outputs()
    #for output in o:
    #  self.insertUnspentOutput(output)
    self.conn.execute('insert into OBJECTS (ID, PAYLOAD, TYPE) values (?, ?, ?)', [trans.get_hash(), t, 'TRANS'])
    self.conn.commit()
    
  def getUnspentOutputs(self):
    """ Retrieves a list of all unspent outputs
    
    Return: (list) Transaction.Output objects
    """
    unspents = self.conn.execute('SELECT * FROM OBJECTS WHERE TYPE = ?', ['UNSPT'])
    raw_list = unspents.fetchall()
    result = []
    for item in raw_list:
      trans = Transaction.Output.unpack(item[1])
      result.append(trans)
    return result
    
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
    block = self.conn.execute('SELECT * FROM OBJECTS WHERE TYPE = ? ORDER BY TIMESTAMP LIMIT 1', ['BLOCK'])
    raw_list = block.fetchall()
    return raw_list[0]
    
if __name__ == '__main__':
  from keystore import KeyStore
  db = DB()
  c = CoinBase()
  t = Transaction()
  t.add_input(Transaction.Input(100, b'', 0))
  t.add_output(Transaction.Output(20, KeyStore.getPublicKey()))
  db.insertTransaction(t)
  #t = Transaction()
  #c = CoinBase()
  #t.add_input(Transaction.Input(17, 0))
  #t.add_output(Transaction.Output(7, KeyStore.getPublicKey()))
  #db.insertTransaction(t)
  print(db.getAllTransactions())
  print(db.getUnspentOutputs())