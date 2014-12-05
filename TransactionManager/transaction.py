from Crypto.Hash import SHA256
from Crypto.Signature import PKCS1_v1_5
from Crypto.PublicKey import RSA
from Crypto.Random import random
import struct, time

import logging
from globals import LOG_LEVEL

log = logging.getLogger(__name__)
log.setLevel(LOG_LEVEL)

from keystore import *
from P2P.client_manager import *

class Transaction:
  ''' Base "regular" transaction '''
  nVersion = 1
  
  def __init__(self, owner=None, callback=None):
    """ Initializes a Transaction object
    
    Param: owner -> The 'owner' of this transaction. (Initiator)
           callback -> a callback function to get called when the transaction is verified
    """
    log.debug('Creating a regular transaction')
    self.input = []
    self.output = []
    self.hash = None
    if not owner:
      self.owner = KeyStore.getPrivateKey()
    else:
      self.owner = owner
    self.callback = callback
    
  def add_input(self, inp):
    """ since inputs are really just outputs, this will be slowly converted to just accepting an input value
    and it finds previous output values from past transactions."""
    target_val = inp.value
    
    # find all previous unspent outputs....
    from db import DB
    db = DB()
    outputs = db.getUnspentOutputs(self.owner.publickey())
    
    # find enough outputs to total the requested input...
    val = 0
    for o in outputs:
      val += o.value
      inp = Transaction.Input(o.value, o.transaction, o.n, owner=self.owner, output=o)
      self.input.append(inp)
      if val > target_val:
        break
    # compute change and create a new output to ourselves.
    diff = val - target_val

    if diff < 0:
      raise Exception('Output exceeds input!')
    # 'manually' add the change as an output back to ourselves
    o = Transaction.Output(diff, self.owner.publickey())
    self.output.append(o)
    o.n = len(self.output)

    return self
    
  def add_output(self, output):
    """ Adds an output to this transaction
    
    Args:
      output: an Transaction.Output object that will be added to this transaction
      
    Returns:
      Self, for use as a factory type builder.
    """
    #log.info('creating output... %d, paying to %s', output.value, output.pubKey.exportKey())
    self.output.append(output)
    output.n = len(self.output)
    
    # find (and add) the necessary inputs
    self.add_input(output)
    
    return self
    
  def get_outputs(self):
    return self.output
    
  def broadcast(self):
    """ Broadcast this transaction to peers
    
    Broadcast this transaction in packed binary format to the peer network
    """
    try:
      port = random.randint(40000, 60000)
      p2pclient = P2PClientManager.getClient(port)
      p2pclient.broadcast_transaction(self)
    except Exception as e:
      log.warning(e)
    
  def hash_transaction(self):
    """ Hashes the transaction in raw format """
    if self.hash:
      return self.hash.digest()
    self.hash = SHA256.new()
    self.hash.update(self.pack())
    return self.hash.digest()
    
  # def pay_diff_to_self(self):
  #   totalIn = sum([x.value for x in self.input])
  #   totalOut = sum([x.value for x in self.output])
  #   print(totalIn, totalOut, totalIn-totalOut)
  #   self.add_output(Transaction.Output(totalIn-totalOut, self.owner.publickey()))
    
  def finish_transaction(self):

    self.sign_inputs()
    self.add_hash_to_outputs()
    self.store_transaction()
    self.broadcast()
    self.verify()
    
  def add_hash_to_outputs(self):
    for o in self.output:
      o.transaction = self.hash_transaction()
    
  def sign_inputs(self):
    for i in self.input:
      i.apply_signature(i.prev)
    
  def store_transaction(self):
    from db import DB
    db = DB()
    db.insertTransaction(self)
    
  def pack(self, withSig=False):
    
    buffer = bytearray()
    buffer.extend(self.hash_transaction())
    buffer.extend(struct.pack('B', len(self.input)))
    self.pack_inputs(buffer, withSig)
    buffer.extend(struct.pack('B', len(self.output)))
    self.pack_outputs(buffer)
    return buffer
    
  def pack_inputs(self, buf, withSig):
    for inp in self.input:
      inp.pack(buf, withSig=withSig)
    return buf
    
  def pack_outputs(self, buf):
    for o in self.output:
      o.pack(buf)
    return buf
    
  def unpack(self, buf):
    """ unpacks a Transaction from a buffer of bytes
    
    """
    self.hash = SHA256.new(buf[:32])
    offset = 32
    num_in = struct.unpack_from('B', buf, offset)[0]
    offset += 1
    self.input = []
    coinbase = False
    if self.hash == bytes(struct.pack('I', 0) * 8):
      coinbase = True
    for i in range(num_in):
      inp = Transaction.Input.unpack(buf, offset, coinbase=coinbase)
      self.input.append(inp)
      offset += Transaction.Input.PACKED_SIZE
      if coinbase:
        offset += 4
      
    num_out = struct.unpack_from('B', buf, offset)[0]
    offset += 1
    
    self.output = []
    for i in range(num_out):
      out = Transaction.Output.unpack(buf, offset)
      self.output.append(out)
      offset += Transaction.Output.PACKED_SIZE
    
    
  def __repr__(self):
    return 'Transaction:' +\
    '\nvin#: ' + str(len(self.input)) +\
    '\nvin[]: ' + str(self.input) +\
    '\nvout#: ' + str(len(self.output)) +\
    '\nvout[]: ' + str(self.output)
    
  def verify(self):
    # find all previous unspent outputs....
    from db import DB
    db = DB()
    log.info('Verifying transaction...')
    if self.input[0].prev == bytes(struct.pack('I', 0) * 8):
      log.info('Coinbase transaction verified.')
      return True
    outputs = db.getUnspentOutputs()
    for o in outputs:
      for i in self.input:
        if i.prev == o.transaction and i.n == o.n:
          if not self.check_sig(i.signature, o.pubKey, o.transaction):
            log.warning('Transaction invalid!')
            return False
          log.debug('removing output...')
          db.removeUnspentOutput(o) # output was verified, remove it
    if self.callback:
      self.callback()
    return True
    
  def check_sig(self, signature, pubKey, trans):
    message = SHA256.new(trans)
    verifier = PKCS1_v1_5.new(pubKey)
    verified = verifier.verify(message, signature)
    return verified
    
  # inner class representing inputs/outputs to a transaction
  class Input:
    """ defines an input object in a transaction
    
    Attributes:
      value: the bitcoin value of this input in a transaction
      signature: the digital signature of the entity spending bitcoins
      n: the nth input in a transaction
    """
    
    PACKED_SIZE = 290
    
    @staticmethod
    def unpack(buf, offset, coinbase=False):
      value = struct.unpack_from('B', buf, offset)[0]
      offset += 1
      prev = buf[offset:offset+32]
      offset += 32
      n = struct.unpack_from('B', buf, offset)[0]
      offset += 1
      signature = buf[offset:offset+256]
      i = Transaction.Input(value, prev, n)
      i.signature = signature
      i.n = n
      if coinbase:
        i.coinbase = struct.unpack_from('I', buf, offset)[0]
      return i
    
    def __init__(self, value, prev, n, owner=None, output=None):
      # sanity checks
      if len(prev) != 32:
        raise Exception('Previous transaction hash invalid length!')
      self.value = value
      self.prev = prev
      self.n = n
      self.signature = None
      if not owner:
        self.owner = KeyStore.getPrivateKey()
      else:
        self.owner = owner
      self.output=output
      
    def __repr__(self):
      return 'Input:' +\
      '\nvalue: ' + str(self.value) +\
      '\nprev trans: ' + str(self.prev) +\
      '\nn: ' + str(self.n) +\
      '\nsignature: ' + str(self.signature)
      
    def apply_signature(self, trans_hash):
      """ Signs a hash of the transaction
      
      Param: trans_hash - the hash of the current transaction
      """
      # sign the input
      message = SHA256.new(trans_hash)
      signer = PKCS1_v1_5.new(self.owner)
      self.signature = signer.sign(message)
      
    def pack(self, buf, withSig=False):
      buf.extend(struct.pack('B', self.value))
      buf.extend(self.prev)
      buf.extend(struct.pack('B', self.n))
      if withSig:
        buf.extend(self.signature)
      if hasattr(self, 'coinbase'):
        buf.extend(struct.pack('I', self.coinbase)) #4
      return buf
      
  class Output:
    """ defines an output object in a transaction
    
    Attributes:
      value: the bitcoin value of this output to be transfer to another user
      pubKey: the public key of the recipient of the bitcoins
      n: the nth output in a transaction
    """
    
    #_n = 0   # the output count
    PACKED_SIZE = 455
    
    def __init__(self, value, pubKey):
      self.value = value
      self.pubKey = pubKey
      # this will prevent accidentally storing the private key of a client
      if pubKey.has_private():
        raise Exception('Private key')
      self.timestamp = int(time.time())  # not sure if this is needed, but this will make each hash unique
      self.transaction = None
      self.n = -1
      
    def __repr__(self):
      return 'Output:' +\
      '\nvalue: ' + str(self.value) +\
      '\npublic key: ' + str(self.pubKey.exportKey()) +\
      '\ntrans: ' + str(self.transaction) +\
      '\nn: ' + str(self.n)
        
    def hash_key(self, hex=True):
      hash = SHA256.new()
      hash.update(self.pubKey.exportKey())
      if hex:
        return hash.hexdigest()
      else:
        return hash.digest()
        
    def hash_output(self, hex=True):
      bytes = self.pack(bytearray())
      hash = SHA256.new()
      hash.update(bytes)
      if hex:
        return hash.hexdigest()
      else:
        return hash.digest()
        
    def pack(self, buf):
      buf.extend(struct.pack('I', self.value))
      #buf.extend(struct.pack('I', self.timestamp))
      buf.extend(struct.pack('B', self.n))
      buf.extend(self.pubKey.exportKey())
      return buf
      
    @staticmethod
    def unpack(buf, offset=0):
      #transaction = buf[offset:offset+32]
      #offset += 32
      value = struct.unpack_from('I', buf, offset)[0]
      offset += 4
      #offset += 4 # ignore timestamp
      n = struct.unpack_from('B', buf, offset)[0]
      offset += 1
      key = buf[offset:offset+450]
      pubKey = RSA.importKey(key)
      o = Transaction.Output(value, pubKey)
      o.n = n
      #i.transaction = transaction
      return o
      
if __name__ == '__main__':
  import sys, time
  from keystore import KeyStore
  from Crypto.PublicKey import RSA
  from Crypto import Random
  r = Random.new().read
  otherKey = RSA.generate(2048, r)
  myKey = RSA.generate(2048, r)
  from TransactionManager.coinbase import CoinBase
  c = CoinBase(owner=myKey)
  c.finish_transaction()
  #print('Verified: ', c.verify())
  t = Transaction(owner=myKey)

  t.add_output(Transaction.Output(20, myKey.publickey()))
  #t.input[0].owner = otherKey
  t.finish_transaction()
  #print('Verified: ', t.verify())
  #time.sleep(10)
  
  # t = Transaction(owner=myKey)

  # t.add_output(Transaction.Output(12, otherKey.publickey()))
  # t.finish_transaction()
  # print('Verified: ', t.verify())
  # c = CoinBase()
  # t = Transaction()
  # t.add_output(Transaction.Output(20, otherKey.publickey()))
  # for i in t.input:
  #     i.apply_signature(t.hash_transaction())
  # b = t.pack(withSig=True)
  # #print(b)
  # t.unpack(b)
  # print(t)