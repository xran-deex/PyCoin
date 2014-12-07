from tkinter import *
from tkinter import messagebox
from tkinter.ttk import Button, Style
from MiningManager.miningmanager import Miner
from P2P.client_manager import P2PClientManager
from TransactionManager.transaction import Transaction
from TransactionManager.coinbase import CoinBase
import threading, random, time
from keystore import KeyStore
from Crypto.PublicKey import RSA
from P2P.messages import Message
from db import DB
from Crypto.Hash import SHA
from logging.handlers import MemoryHandler

import logging
from globals import LOG_LEVEL
log = logging.getLogger()
log.setLevel(LOG_LEVEL)

class PyCoin(Frame):

  coin_balance = 0
  
  def __init__(self, parent):
    Frame.__init__(self, parent)
    self.parent = parent
    self.parent.protocol("WM_DELETE_WINDOW", self.quit)
    self.coin_balance = StringVar(self.parent, '0')
    self.db = DB()
    self.initApp()
    self.setupGUI()
      
  def quit(self, event=None):
    log.debug('quiting...')
    P2PClientManager.deleteClient()
    self.parent.destroy()

  def initApp(self):
    #Connect Here
    self.client = P2PClientManager.getClient(port=random.randint(40000, 60000))
    self.client.subscribe(Message.NEW_TRANSACTION, self.update_balance)
    self.client.subscribe_to_info(self.update_status)
    t = threading.Thread(target=self.start_miner)
    t.start()
    if not self.db.hasRanBefore():
      c = CoinBase(owner=KeyStore.getPrivateKey())
      c.finish_transaction()
      self.db.setRanBefore()
      #messagebox.showinfo('Welcome', 'This is your first time running the app. You get to start off with 100 PyCoins!')
    #Get balance, Save to variable below
    self.coin_balance.set(str(KeyStore.get_balance()))
    print('PyCoin Address: ', SHA.new(KeyStore.getPublicKey().exportKey()).hexdigest())
    log.debug("GUI created")
      
  def start_miner(self):
    self.miner = Miner()
    self.miner.subscribe(self.display_info)
    
  def display_info(self, info):
    #messagebox.showinfo("Info", info)
    pass
    
  def update_status(self, info):
    self.status.text = info

  def update_balance(self, t=None):
    bal = str(KeyStore.get_balance())
    self.coin_balance.set(bal)

  def create_menu(self):
    top = self.winfo_toplevel()
    self.menuBar = Menu(top)
    top['menu'] = self.menuBar

    self.subMenu = Menu(self.menuBar, tearoff=0)
    self.menuBar.add_cascade(label='File', menu=self.subMenu)
    self.subMenu.add_command(label='Verify Blockchain', command=self.verify_block_chain)
    self.subMenu.add_command(label='My PyCoin Address', command=self.show_address)
    self.subMenu.add_separator()
    self.subMenu.add_command(label='Quit', command=self.quit)
    
  def show_address(self):
    f = Tk()
    label = Label(f, text='PyCoin Address')
    label.pack()
    k = SHA.new(KeyStore.getPublicKey().exportKey()).hexdigest()
    key = Text(f, width=42, height=1)
    key.insert(INSERT, k)
    key.pack()
    
  def verify_block_chain(self):
    if self.miner.verify_block_chain():
      messagebox.showinfo("Verified", "Block chain verified.")
    else:
      messagebox.showwarning("Warning", "Block chain is invalid.")

  def open_debug_window(self):
    self.debug = Tk()
    self.tw = Text(self.debug, relief='flat')
    self.tw.pack()
  
  def setupGUI(self):
    
    self.parent.bind('<Control-q>', self.quit)
    self.parent.title("PyCoin")
    self.pack(fill=BOTH, expand=1)

    self.create_menu()

    #Labeled Frames for Status and Send
    lf = LabelFrame(self, text="Send BitCoins")
    lf.pack(side=BOTTOM, fill="both", expand="yes", padx=7, pady=7)

    lf2 = LabelFrame(self, text="BitCoin Status")
    lf2.pack(side=TOP, fill="both", expand="yes", padx=7, pady=7)
    
    #Labels for Bitcoin balance
    self.balanceHeading = Label(lf2, text="BitCoin Balance:",
                         font = "Helvetica 20")
    self.balanceHeading.pack()
    self.balance = Label(lf2, textvariable=self.coin_balance, font="Helvetica 20")
    self.balance.pack()
    
    #Label and Text field for BitCoin Amount

    self.amtFrame = Frame(lf)
    self.amtFrame.pack()
    
    self.label = Label(self.amtFrame, text="BitCoin Amount :")
    self.label.pack(side=LEFT)
    
    self.amountBox = Entry(self.amtFrame, bd=2)
    self.amountBox.pack(side=LEFT, pady=10, fill=X)
    

    #Label and Text filed for Reciever Key
    self.label = Label(lf, text="Receivers Public Key:")
    self.label.pack()

    self.recieverKey = Text(lf, width=42, height=1)
    self.recieverKey.pack()

    #Send Button
    self.sendBtn = Button(lf, text='\nSend BitCoin(s)\n', command=self.sendCoins)
    self.sendBtn.pack(fill=X, pady=5)

    #Status Bar
    status = Label(self.winfo_toplevel(), text="Ready", bd=1, relief=SUNKEN, anchor=W)
    status.pack(side=BOTTOM, fill=X)

  
  #Send Button Callback Function
  def sendCoins(self):
    sendAmt = self.amountBox.get()            #Amount to send
    recvKey = self.recieverKey.get("1.0",'end-1c')   #recievers public key

    if not sendAmt:
      messagebox.showwarning("Warning", "Please enter a BitCoin amount.")
    elif len(recvKey) <= 1:
      messagebox.showwarning("Warning", "Please enter the receivers key.")
    else:
      result = messagebox.askyesno("Send Confirmation", 'Sending {} BitCoins to reciever:\n {}'.format(sendAmt, recvKey))

      if result:
        print('Sending {} BitCoins to reciever:\n {}'.format(sendAmt, recvKey))
        t = Transaction(owner=KeyStore.getPrivateKey(), callback=self.update_balance)
        
        try:
          pubKey = self.client.keyTable[recvKey]
        except:
          messagebox.showwarning('Address not found.', 'Oops. That PyCoin address could not be found.')
          return
        try:
          t.add_output(Transaction.Output(int(sendAmt), RSA.importKey(pubKey)))
        except:
          messagebox.showwarning('Insufficient funds.', 'Oops. It looks like you ran out of money. :(')
          return
        t.finish_transaction()

      self.amountBox.delete(0,END)
 
def main():
  
    root = Tk()
    app = PyCoin(root)
    
    root.mainloop()


if __name__ == '__main__':
    main()
