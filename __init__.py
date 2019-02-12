# __init__.py

import pygame
from PygameGame import PygameGame
import threading

class StartGame(PygameGame):
	def __init__(self):
		super().__init__(width=1300, height=700, fps=60, title='MiniBall')
		self.bgColor = (50, 103, 68)
		self.mode = 'startScreen'

	def init(self):
		# Title Image
		self.titleImage = pygame.image.load('Images/StartScreen/title.png')
		titleWidth, titleHeight = self.titleImage.get_size()
		self.titleRect = (self.width/2 - titleWidth/2, self.height * 0.15 - titleHeight/2,
						  self.width/2 + titleWidth/2, self.height * 0.15 + titleHeight/2)

		# Game options (Start Screen)
		self.option1Image = pygame.image.load('Images/StartScreen/playComp.png')
		self.option1Dir = 'Images/StartScreen/playComp.png'
		option1Width, option1Height = self.option1Image.get_size()
		self.option1Left, self.option1Top = self.width * 0.2 - option1Width/2, self.height * 0.6 - option1Height/2
		self.option1Right, self.option1Bottom = self.width * 0.2 + option1Width/2, self.height * 0.6 + option1Height/2
		self.option1Rect = (self.option1Left, self.option1Top, self.option1Right, self.option1Bottom)

		self.option2Image = pygame.image.load('Images/StartScreen/playFriend.png')
		self.option2Dir = 'Images/StartScreen/playFriend.png'
		option2Width, option2Height = self.option2Image.get_size()
		self.option2Left, self.option2Top = self.width * 0.5 - option2Width/2, self.height * 0.6 - option2Height/2
		self.option2Right, self.option2Bottom = self.width * 0.5 + option2Width/2, self.height * 0.6 + option2Height/2
		self.option2Rect = (self.option2Left, self.option2Top, self.option2Right, self.option2Bottom)

		self.option3Image = pygame.image.load('Images/StartScreen/createGame.png')
		self.option3Dir = 'Images/StartScreen/createGame.png'
		option3Width, option3Height = self.option3Image.get_size()
		self.option3Left, self.option3Top = self.width * 0.8 - option3Width/2, self.height * 0.46 - option3Height/2
		self.option3Right, self.option3Bottom = self.width * 0.8 + option3Width/2, self.height * 0.46 + option3Height/2
		self.option3Rect = (self.option3Left, self.option3Top, self.option3Right, self.option3Bottom)

		self.option4Image = pygame.image.load('Images/StartScreen/joinGame.png')
		self.option4Dir = 'Images/StartScreen/joinGame.png'
		option4Width, option4Height = self.option4Image.get_size()
		self.option4Left, self.option4Top = self.width * 0.8 - option4Width/2, self.height * 0.74 - option4Height/2,
		self.option4Right, self.option4Bottom = self.width * 0.8 + option4Width/2, self.height * 0.74 + option4Height/2
		self.option4Rect = (self.option4Left, self.option4Top, self.option4Right, self.option4Bottom)

		self.redTeam = ['Player1', 'Player3', 'Player5', 'Player7']
		self.blueTeam = ['Player2', 'Player4', 'Player6', 'Player8']

		# This is the input box to enter the ip address of a host for someone wanting to play online multiplayer
		# This module is from Silas Gyger found at https://github.com/Nearoo/pygame-text-input
		import textInput.pygame_textinput
		self.textinput = textInput.pygame_textinput.TextInput(font_size=65)

	###################################
	# Mode dispatcher
	###################################

	def mousePressed(self, x, y):
		if self.mode == 'startScreen':
			self.startScreenMousePressed(x, y)
		elif self.mode == 'joinGame':
			self.joinGameMousePressed(x, y)

	def timerFired(self, dt):
		if self.mode == 'playFriend':
			# Initialize the game (offline)
			import local
			offlineGame = local.PlayGame()
			offlineGame.init()
			offlineGame.run()

		elif self.mode == 'createGame':
			import server
			threading.Thread(target = server.main).start()

			import client
			client.main(isHost=True)

		elif self.mode == 'joinGame':
			self.joinGameTimerFired(dt)

		elif self.mode == 'playComputer':
			import playAI
			playComputer = playAI.PlayGame()
			playComputer.init()
			playComputer.run()

	def redrawAll(self, screen):
		if self.mode == 'startScreen':
			self.startScreenRedrawAll(screen)
		elif self.mode == 'joinGame':
			self.joinGameRedrawAll(screen)

	###################################
	# Start Screen
	###################################

	def startScreenMousePressed(self, x, y):
		if x >= self.option1Left and x <= self.option1Right and y >= self.option1Top and y <= self.option1Bottom:
			self.mode = 'playComputer'
		if x >= self.option2Left and x <= self.option2Right and y >= self.option2Top and y <= self.option2Bottom:
			self.mode = 'playFriend'
		if x >= self.option3Left and x <= self.option3Right and y >= self.option3Top and y <= self.option3Bottom:
			self.mode = 'createGame'
		if x >= self.option4Left and x <= self.option4Right and y >= self.option4Top and y <= self.option4Bottom:
			self.mode = 'joinGame'

	def startScreenRedrawAll(self, screen):
		screen.blit(self.titleImage, pygame.Rect(self.titleRect))

		# Highlight an option if the mouse is over it
		mx, my = pygame.mouse.get_pos()
		if mx >= self.option1Left and mx <= self.option1Right and my >= self.option1Top and my <= self.option1Bottom:
			option1Dir = self.option1Dir[:-4] + 'High' + self.option1Dir[-4:]
		else: option1Dir = self.option1Dir
		if mx >= self.option2Left and mx <= self.option2Right and my >= self.option2Top and my <= self.option2Bottom:
			option2Dir = self.option2Dir[:-4] + 'High' + self.option2Dir[-4:]
		else: option2Dir = self.option2Dir
		if mx >= self.option3Left and mx <= self.option3Right and my >= self.option3Top and my <= self.option3Bottom:
			option3Dir = self.option3Dir[:-4] + 'High' + self.option3Dir[-4:]
		else: option3Dir = self.option3Dir
		if mx >= self.option4Left and mx <= self.option4Right and my >= self.option4Top and my <= self.option4Bottom:
			option4Dir = self.option4Dir[:-4] + 'High' + self.option4Dir[-4:]
		else: option4Dir = self.option4Dir

		option1Image = pygame.image.load(option1Dir)
		option2Image = pygame.image.load(option2Dir)
		option3Image = pygame.image.load(option3Dir)
		option4Image = pygame.image.load(option4Dir)
		screen.blit(option1Image, pygame.Rect(self.option1Rect))
		screen.blit(option2Image, pygame.Rect(self.option2Rect))
		screen.blit(option3Image, pygame.Rect(self.option3Rect))
		screen.blit(option4Image, pygame.Rect(self.option4Rect))

	###################################
	# Join Game Screen
	###################################
	
	def joinGameMousePressed(self, x, y):
		if x >= self.backButtonMargin and x <= self.backButtonMargin + self.backW and \
			y >= self.backButtonMargin and y <= self.backButtonMargin + self.backH:
			self.mode = 'startScreen'

	def joinGameTimerFired(self, dt):
		# Ask for IP address
		if self.textinput.update(pygame.event.get(pygame.KEYDOWN)):
			# When they hit enter join the server
			IPAdd = self.textinput.get_text()
			import client
			client.main(isHost=False, IP=IPAdd)

	def joinGameRedrawAll(self, screen):
		popup = pygame.image.load('Images/enterIP.png')
		width, height = popup.get_size()
		popupRect = (self.width/2 - width/2, self.height * 0.46 - height/2, self.width/2 + width/2, self.height * 0.46 + height/2)
		textbox = pygame.image.load('Images/textbox.png')
		txtW, txtH = textbox.get_size()
		txtRect = (self.width/2 - txtW/2, self.height/2 - txtH/2, self.width/2 + txtW/2, self.height + txtH/2)
		backButton = pygame.image.load('Images/backButton.png')
		self.backW, self.backH = backButton.get_size()
		self.backButtonMargin = self.width * 0.02
		backRect = (self.backButtonMargin, self.backButtonMargin, self.backButtonMargin + self.backW, self.backButtonMargin + self.backH)

		screen.blit(popup, pygame.Rect(popupRect))
		screen.blit(textbox, pygame.Rect(txtRect))
		screen.blit(self.textinput.get_surface(), (self.width/2 - txtW * 0.48, self.height/2 - txtH * 0.3))
		screen.blit(backButton, pygame.Rect(backRect))

def main():
	game = StartGame()
	game.run()

if __name__ == '__main__':
    main()