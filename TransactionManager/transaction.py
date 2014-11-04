from Crypto.Hash import SHA256
from Crypto.Signature import PKCS1_v1_5
from Crypto.PublicKey import RSA
from Crypto import Random

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
  
  def build_raw_transaction(self):
    import array
    raw = bytearray()
    raw += len(self.input).to_bytes(4, byteorder='big')
    raw += self.hash_inputs().digest()
    raw += len(self.output).to_bytes(4, byteorder='big')
    raw += self.hash_outputs().digest()
    return raw
    
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
    
    
    
    
  # inner class representing inputs/outputs to a transaction
  class Input:
    """ defines an input object in a transaction
    
    Attributes:
      value: the bitcoin value of this input in a transaction
      signature: the digital signature of the entity spending bitcoins
      n: the nth input in a transaction
    """
    
    _n = 0  # the input count
    
    def __init__(self, value):
      self.value = value
      key = KeyStore.getPublicKey()
      # sign the input
      message = SHA256.new(str.encode('signature'))
      signer = PKCS1_v1_5.new(key)
      self.signature = signer.sign(message)
      
      Transaction.Input._n += 1
      self.n = Transaction.Input._n
      
      print('input #', self.n)
      
    def __repr__(self):
      return str(self.value) + ' ' + str(self.signature) + ' ' + str(self.n)
      
    def get_bytes(self):
      return (self.__repr__()).encode('ascii')
      
    def hash_sig(self):
      hash = SHA256.new()
      hash.update(self.signature)
      return hash.hexdigest()
      
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
        return str(self.value) + ' ' + self.hash_key()
        
    def get_bytes(self):
      return (self.__repr__()).encode('ascii')
        
    def hash_key(self):
      hash = SHA256.new()
      hash.update(self.pubKey.exportKey())
      return hash.hexdigest()