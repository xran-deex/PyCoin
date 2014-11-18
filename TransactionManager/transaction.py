from Crypto.Hash import SHA256
from Crypto.Signature import PKCS1_v1_5
from Crypto.PublicKey import RSA
from Crypto.Random import random
import struct, time

from keystore import *
from P2P.client_manager import *

class Transaction:
  ''' Base "regular" transaction '''
  nVersion = 1
  
  def __init__(self):
    print('Creating a regular transaction')
    self.input = []
    self.output = []
    self.hash = None
    
  def add_input(self, inp):
    """ since inputs are really just outputs, this will be slowly converted to just accepting an input value
    and it finds previous output values from past transactions."""
    target_val = inp.value
    
    # find all previous unspent outputs....
    from db import DB
    db = DB()
    outputs = db.getUnspentOutputs(KeyStore.getPublicKey())
    
    # find enough outputs to total the requested input...
    val = 0
    for o in outputs:
      val += o.value
      inp = Transaction.Input(o.value, o.transaction, o.n)
      self.input.append(inp)
      db.removeUnspentOutput(o)
      if val > target_val:
        break
    # compute change and create a new output to ourselves.
    diff = val - target_val

    if diff < 0:
      raise Exception('Output exceeds input!')
    # 'manually' add the change as an output back to ourselves
    o = Transaction.Output(diff, KeyStore.getPublicKey())
    self.output.append(o)
    o.n = len(self.output)

    db.insertUnspentOutput(o, self)
    return self
    
  def add_output(self, output):
    """ Adds an output to this transaction
    
    Args:
      output: an Transaction.Output object that will be added to this transaction
      
    Returns:
      Self, for use as a factory type builder.
    """
    print('creating output...', output.value)
    self.output.append(output)
    output.n = len(self.output)
    self.add_input(output)
    #output.transaction = self.hash_transaction()

    from db import DB
    db = DB()
    db.insertUnspentOutput(output, self)
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
      p2pclient.broadcast_transaction(self.build_struct())
    except Exception as e:
      print(e)
    
  def hash_transaction(self):
    """ Hashes the transaction in raw format """
    self.hash = SHA256.new()
    self.hash.update(self.build_struct())
    return self.hash.digest()
    
  def get_hash(self):
    """ Retrieves this transaction's hash
    
    Returns:
      This transaction's hash as a hex string
    """
    if not self.hash:
      self.hash_transaction()
    return self.hash.hexdigest()
    
  def pay_diff_to_self(self):
    totalIn = sum([x.value for x in self.input])
    totalOut = sum([x.value for x in self.output])
    print(totalIn, totalOut, totalIn-totalOut)
    self.add_output(Transaction.Output(totalIn-totalOut, KeyStore.getPublicKey()))
    
  def finish_transaction(self):
    #self.pay_diff_to_self()
    self.store_transaction()
    self.broadcast()
    return self.build_struct()
    
  def store_transaction(self):
    from db import DB
    db = DB()
    db.insertTransaction(self)
    
  def build_struct(self):
    
    buffer = bytearray()
    buffer.extend(struct.pack('B', len(self.input)))
    self.pack_inputs(buffer)
    buffer.extend(struct.pack('B', len(self.output)))
    self.pack_outputs(buffer)
    return buffer
    
  def pack_inputs(self, buf):
    for inp in self.input:
      inp.pack(buf)
    return buf
    
  def pack_outputs(self, buf):
    for o in self.output:
      o.pack(buf)
    return buf
    
  def unpack(self, buf):
    """ unpacks a Transaction from a buffer of bytes
    
    """
    num_in = struct.unpack_from('B', buf)[0]
    offset = 1
    self.input = []
    print(num_in)
    for i in range(num_in):
      self.input.append(Transaction.Input.unpack(buf, offset))
      offset += 69
    num_out = struct.unpack_from('B', buf)[0]
    print(num_out)
    offset += 1
    for i in range(num_out):
      out = Transaction.Output.unpack(buf, offset)
      self.output.append(out)
      offset += 517
    
    
  def __repr__(self):
    return 'Transaction:' +\
    '\n#vin: ' + str(len(self.input)) +\
    '\nvin[]: ' + str(self.input) +\
    '\n#vout: ' + str(len(self.output)) +\
    '\nvout[]: ' + str(self.output)
    
  # inner class representing inputs/outputs to a transaction
  class Input:
    """ defines an input object in a transaction
    
    Attributes:
      value: the bitcoin value of this input in a transaction
      signature: the digital signature of the entity spending bitcoins
      n: the nth input in a transaction
    """
    
    @staticmethod
    def unpack(buf, offset):
      value = struct.unpack_from('B', buf, offset)[0]
      offset += 1
      prev = buf[offset:offset+32]
      offset += 32
      n = struct.unpack_from('I', buf, offset)[0]
      offset += 1
      signature = buf[offset:offset+32]
      i = Transaction.Input(value, prev, n)
      i.signature = signature
      i.n = n
      return i
    
    def __init__(self, value, prev, n):
      
      ### TODO: prev needs to eb the hash of the previous transaction
      
      self.value = value
      self.prev = prev
      key = KeyStore.getPrivateKey()
      # sign the input
      message = SHA256.new(str.encode('signature'))
      signer = PKCS1_v1_5.new(key)
      self.signature = signer.sign(message)

      self.n = n
      
    def __repr__(self):
      return str(self.value) + ', ' + str(self.hash_sig())
      
    def hash_sig(self, hex=True):
      hash = SHA256.new()
      hash.update(self.signature)
      if hex:
        return hash.hexdigest()
      else:
        return hash.digest()
    
    def hash_prev(self, hex=True):
      hash = SHA256.new()
      hash.update(self.signature)
      if hex:
        return hash.hexdigest()
      else:
        return hash.digest()
      
    def pack(self, buf):
      buf.extend(struct.pack('B', self.value))
      buf.extend(self.hash_prev(hex=False))
      buf.extend(struct.pack('I', self.n))
      buf.extend(self.hash_sig(hex=False))
      return buf
      
  class Output:
    """ defines an output object in a transaction
    
    Attributes:
      value: the bitcoin value of this output to be transfer to another user
      pubKey: the public key of the recipient of the bitcoins
      n: the nth output in a transaction
    """
    
    #_n = 0   # the output count
    
    def __init__(self, value, pubKey):
      self.value = value
      self.pubKey = pubKey
      # this will prevent accidentally storing the private key of a client
      if pubKey.has_private():
        raise Exception('Private key')
      self.timestamp = int(time.time())  # not sure if this is needed, but this will make each hash unique
      #self.transaction = None
      
    def __repr__(self):
      return str(self.value) + ', ' + str(self.pubKey.exportKey())
        
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
      #print('transaction hash length: ', len(self.transaction))
      #buf.extend(self.transaction)
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
      pubKey = RSA.importKey(buf[offset:offset+450])
      i = Transaction.Output(value, pubKey)
      i.n = n
      #i.transaction = transaction
      return i
      
if __name__ == '__main__':
  import sys, time
  from keystore import KeyStore
  from Crypto.PublicKey import RSA
  otherKey = RSA.generate(2048)
  from TransactionManager.coinbase import CoinBase
  c = CoinBase()
  t = Transaction()

  t.add_output(Transaction.Output(20, otherKey.publickey()))
  t.finish_transaction()
  time.sleep(10)
  
  t = Transaction()

  t.add_output(Transaction.Output(12, otherKey.publickey()))
  t.finish_transaction()