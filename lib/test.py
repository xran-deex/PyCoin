### The code in the file is just for scratch purposes. Actual tests are in the tests folder. ###

# from keystore import *
# from TransactionManager.transaction import *

# from Crypto.Signature import PKCS1_v1_5
# from Crypto.Hash import SHA256

# key = KeyStore.getPublicKey()

# cb = Transaction('')
# #cb.add_payee('Bob')

# # sign
# message = SHA256.new(str.encode('sig'))
# signer = PKCS1_v1_5.new(key)
# signature = signer.sign(message)

# cb.add_input(Transaction.Input(20))
# cb.add_output(Transaction.Output(10, key.publickey()))
# cb.add_input(Transaction.Input(5))
# cb.build()

# cb.broadcast()

# # verify
# message = SHA256.new(str.encode('sig'))
# verifier = PKCS1_v1_5.new(cb.output[0].pubKey)

# if verifier.verify(message, cb.input[0].signature):
#   print('Signature verified')

# cb.hash_transaction()
# print(cb.get_hash())

# i = Transaction.Input(1)
# i.pack(bytearray(), 0)

import sys, time
from keystore import KeyStore
from P2P.client_manager import *
from TransactionManager.transaction import *
from Crypto.PublicKey import RSA
otherKey = RSA.generate(2048)
from TransactionManager.coinbase import CoinBase

c = CoinBase()
#c.pack(withSig=True)

c.finish_transaction()

t = Transaction()

t.add_output(Transaction.Output(20, otherKey.publickey()))
t.finish_transaction()

#time.sleep(10)

# t = Transaction()

# t.add_output(Transaction.Output(12, otherKey.publickey()))
# t.finish_transaction()