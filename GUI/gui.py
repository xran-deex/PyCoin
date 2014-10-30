''' The main user interface component for PyCoin '''

class GUI:
	
	''' Sets up the ui '''
	def setup(self):
		print('Setting up the ui...')

	''' Displays the user interface??? '''
	def show(self):
		self.setup()
		print('Showing the ui to the user...')

if __name__ == '__main__':
	gui = GUI()
	gui.show()
