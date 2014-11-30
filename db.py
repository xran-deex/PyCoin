import sqlite3, os
from TransactionManager.transaction import Transaction
from TransactionManager.coinbase import CoinBase
#from BlockManager.block import Block
import logging
from globals import LOG_LEVEL

log = logging.getLogger(__name__)
log.setLevel(LOG_LEVEL)

class DB:
  
  db_file = 'db.db'
  db = None
  
  def getDB():
    if not DB.db:
      DB.db = DB(DB.__name__)
    return DB.db
  
  def __init__(self, caller):
    """ Initializes the database access object
        If the database doesn't exist, it is created, otherwise we just connect.
    """
    if caller != 'DB':
      raise Exception('DB is a singleton. Get instance by calling DB.getDB()')
    db_is_new = not os.path.exists(DB.db_file)
    self.conn = sqlite3.connect(DB.db_file)
    
    # if there is no database file, create the db schema
    if db_is_new:
      log.info('Creating schema')
      sql = '''create table if not exists TRANSACTIONS(
      ID TEXT PRIMARY KEY,
      TRANS BLOB,
      TIMESTAMP DATETIME DEFAULT CURRENT_TIMESTAMP
      );
      create table if not exists INPUT_OUTPUTS(
      ID TEXT,
      TRANS BLOB,
      VALUE INTEGER,
      PUBLIC_KEY TEXT,
      SIGNATURE TEXT,
      CONFIRMED INTEGER,
      N INTEGER,
      PACKED BLOB,
      TIMESTAMP DATETIME DEFAULT CURRENT_TIMESTAMP,
      PRIMARY KEY (TRANS, N)
      );
      create table if not exists BLOCKS(
      ID TEXT PRIMARY KEY,
      BLOCK BLOB,
      TIMESTAMP DATETIME DEFAULT CURRENT_TIMESTAMP
      );
      '''
      self.conn.executescript(sql)
    self.subscribers = []
      
  def getTransactionByHash(self, hash):
    """ Retrieves a transaction by hash
    
    Param:
      hash: (SHA256 hash) hash of the transaction to be retrieved
      
    Return: (Transaction) the transaction object or None if not found
    """
    trans = self.conn.execute('SELECT * FROM TRANSACTIONS WHERE ID = ?', [hash])
    if not trans:
      return trans
    return Transaction().unpack(trans[1])
    
  def getAllTransactions(self):
    """ Retrieves every transaction stored in the database
    
    Return: (list) Transaction objects
    """
    trans = self.conn.execute('SELECT * FROM TRANSACTIONS')
    raw_list = trans.fetchall()
    result = []
    for item in raw_list:
      t = Transaction()
      t.unpack(item[1])
      result.append(t)
    return result
    
  def insertUnspentOutput(self, out, trans):
    """ Inserts an unspent output into the database
    
    Param:
      out: (Transaction.Output) the output to be inserted
    """
    self.conn.execute('insert into INPUT_OUTPUTS (ID, VALUE, PUBLIC_KEY, TRANS, N, CONFIRMED, PACKED) values (?, ?, ?, ?, ?, ?, ?)', [out.hash_output(), out.value, out.pubKey.exportKey(), out.transaction, out.n, 0, out.pack(bytearray())])
      
    self.conn.commit()
    self.notify_subscribers()
    
  def insertTransaction(self, trans):
    """ Inserts a transaction into the database
    
    Param:
      trans: (Transaction) the transaction to be inserted
    """
    for o in trans.output:
      self.insertUnspentOutput(o, trans)
    t = trans.pack()

    self.conn.execute('insert into TRANSACTIONS (ID, TRANS) values (?, ?)', [trans.hash_transaction(), t])
    self.conn.commit()
    
  def removeUnspentOutput(self, out):
    if not out:
      return
    log.info('removing...%d, %s', out.value, out.hash_output())
    self.conn.execute('delete from INPUT_OUTPUTS WHERE ID = ?', [out.hash_output()])
    self.conn.commit()
    self.notify_subscribers()
    
  def getUnspentOutputs(self, pubKey=None):
    """ Retrieves a list of all unspent outputs
    
    Return: (list) Transaction.Output objects
    """
    unspents = None
    if pubKey:
      unspents = self.conn.execute('SELECT TRANS, PACKED FROM INPUT_OUTPUTS WHERE CONFIRMED = ? AND PUBLIC_KEY = ?', [0, pubKey.exportKey()])
    else:
      unspents = self.conn.execute('SELECT TRANS, PACKED FROM INPUT_OUTPUTS WHERE CONFIRMED = ? AND PUBLIC_KEY IS NOT NULL', [0])
    raw_list = unspents.fetchall()
    result = []
    for item in raw_list:
      trans = Transaction.Output.unpack(item[1])
      trans.transaction = item[0]
      result.append(trans)
    return result
    
  def confirmOutput(self, out):
    self.conn.execute('delete from INPUT_OUTPUTS where ID = ?', [out.hash_output()])
    self.conn.commit()
    
  def getAllBlocks(self):
    blocks = self.conn.execute('SELECT * FROM BLOCKS')
    raw_list = blocks.fetchall()
    result = []
    for item in raw_list:
      b = Block()
      b.unpack(item[1])
      result.append(b)
    return result
    
  def getLatestBlock(self):
    block = self.conn.execute('SELECT * FROM BLOCKS ORDER BY TIMESTAMP LIMIT 1')
    raw_list = block.fetchall()
    return raw_list[0]
    
  def insertBlock(self, block):
    self.conn.execute('insert into BLOCKS (ID, BLOCK) values (?, ?)', [block.hash_block(hex=True), block.pack()])
    self.conn.commit()
    
  def subscribe(self, callback):
    self.subscribers.append(callback)
    
  def notify_subscribers(self):
    for callback in self.subscribers:
      callback()
    
if __name__ == '__main__':
  from keystore import KeyStore
  from Crypto.PublicKey import RSA
  import time
  otherKey = RSA.generate(2048)
  db = DB()
  c = CoinBase()
  t = Transaction()
  #t.add_input(Transaction.Input(15, b'', 0))
  t.add_output(Transaction.Output(7, otherKey.publickey()))
  t.finish_transaction()
  #t = Transaction()
  #c = CoinBase()
  #t.add_input(Transaction.Input(17, b'', 0))
  #t.add_output(Transaction.Output(9, otherKey.publickey()))
  #t.finish_transaction()
  #print(db.getAllTransactions())
  #myOuts = db.getUnspentOutputs(KeyStore.getPublicKey())
  #print(myOuts)
  #print(db.getUnspentOutputs(otherKey.publickey()))
  time.sleep(10)