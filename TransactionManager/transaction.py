from Crypto.Hash import SHA256
from Crypto.Signature import PKCS1_v1_5
from Crypto.PublicKey import RSA
from Crypto import Random
import struct

from keystore import *

class Transaction:
  ''' Base "regular" transaction '''
  nVersion = 1
  
  def __init__(self):
    print('Creating a regular transaction')
    self.input = []
    self.output = []

  def build(self):
    ''' build a transaction
      this will eventually be encoded in binary format
    '''
    #print(self.payee, self.input, self.output)
    print('Transaction:')
    #print('nVersion: ', Transaction.nVersion)
    print('#vin: ', len(self.input))
    print('vin[]: ', self.input)
    print('#vout: ', len(self.output))
    print('vout[]: ', self.output)
    
  def add_input(self, inp):
    self.input.append(inp)
    return self
    
  def add_output(self, output):
    """ Adds an output to this transaction
    
    Args:
      output: an Transaction.Output object that will be added to this transaction
      
    Returns:
      Self, for use as a factory type builder.
    """
    self.output.append(output)
    return self
    
  def broadcast(self):
    """ Broadcast this transaction to peers
    
    Broadcast this transaction in json format to the peer network
    
    """
    print('Broadcasting transaction...')
    
  def hash_transaction(self):
    """ Hashes the transaction in raw format """
    self.hash = SHA256.new()
    self.hash.update(self.build_raw_transaction())
    
  def get_hash(self):
    """ Retrieves this transaction's hash
    
    Returns:
      This transaction's hash as a hex string
    """
    return self.hash.hexdigest()
    
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
    
  def hash_inputs(self):
    """ Hashes all the inputs
    
    Returns:
      A hash of the inputs
    """
    hash = SHA256.new()
    for i in self.input:
      hash.update(i.get_bytes())
    return hash
    
  def hash_outputs(self):
    """ Hashes all the outputs
    
    Returns:
      A hash of the outputs
    """
    hash = SHA256.new()
    for i in self.output:
      hash.update(i.get_bytes())
    return hash
    
  def get_input_bytes(self):
    result = bytearray()
    for i in self.input:
      result += i.get_bytes()
    return result
    
  def get_output_bytes(self):
    result = bytearray()
    for i in self.output:
      result += i.get_bytes()
    return result
    
  def unpack(self, buf):
    num_in = struct.unpack_from('B', buf)[0]
    offset = 1
    self.input = []
    for i in range(num_in):
      self.input.append(Transaction.Input.unpack(buf, offset))
      offset += 66
    print(self.build())
    
  # inner class representing inputs/outputs to a transaction
  class Input:
    """ defines an input object in a transaction
    
    Attributes:
      value: the bitcoin value of this input in a transaction
      signature: the digital signature of the entity spending bitcoins
      n: the nth input in a transaction
    """
    
    _n = 0  # the input count
    
    def unpack(buf, offset):
      value = struct.unpack_from('B', buf, offset)[0]
      offset += 1
      prev = buf[offset:offset+32]
      offset += 32
      n = struct.unpack_from('B', buf, offset)[0]
      offset += 1
      signature = buf[offset:offset+32]
      i = Transaction.Input(value, prev)
      i.signature = signature
      i.n = n
      return i
      
    
    def __init__(self, value, prev):
      self.value = value
      self.prev = prev
      key = KeyStore.getPublicKey()
      # sign the input
      message = SHA256.new(str.encode('signature'))
      signer = PKCS1_v1_5.new(key)
      self.signature = signer.sign(message)
      
      Transaction.Input._n += 1
      self.n = Transaction.Input._n
      
      print('input #', self.n)
      
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
      print('buf length: ', len(buf))
      buf.extend(struct.pack('B', self.value))
      buf.extend(self.hash_prev(hex=False))
      buf.extend(struct.pack('B', self.n))
      buf.extend(self.hash_sig(hex=False))
      print('buf length: ', len(buf))
      return buf
      
  class Output:
    """ defines an output object in a transaction
    
    Attributes:
      value: the bitcoin value of this output to be transfer to another user
      pubKey: the public key of the recipient of the bitcoins
      n: the nth output in a transaction
    """
    
    _n = 0   # the output count
    
    def __init__(self, value, pubKey):
      self.value = value
      self.pubKey = pubKey
      Transaction.Output._n += 1
      self.n = Transaction.Output._n
      
    def __repr__(self):
        return str(self.value) + ', ' + self.hash_key()
        
    def hash_key(self, hex=True):
      hash = SHA256.new()
      hash.update(self.pubKey.exportKey())
      if hex:
        return hash.hexdigest()
      else:
        return hash.digest()
        
    def pack(self, buf):
      buf.extend(struct.pack('I', self.value))
      buf.extend(self.hash_key(hex=False))
      return buf
      
if __name__ == '__main__':
  t = Transaction()
  t.add_input(Transaction.Input(100, b''))
  t.add_output(Transaction.Output(20, KeyStore.getPublicKey()))
  t.build()