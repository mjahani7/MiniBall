# client.py
# Using the sockets framwork from Kyle Chin's demo (which was adapted form Rohan's demo)

def main(isHost=False, IP=''):
	import socket
	import threading
	from queue import Queue

	# Connect to the server
	if isHost: IP = socket.gethostbyname(socket.gethostname())
	HOST = IP
	PORT = 50004

	server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

	server.connect((HOST,PORT))
	print("connected to server")


	def handleServerMsg(server, serverMsg):
		server.setblocking(1)
		msg = ""
		command = ""
		while True:
			msg += server.recv(10).decode("UTF-8")
			command = msg.split("\n")
			while (len(command) > 1):
				readyMsg = command[0]
				msg = "\n".join(command[1:])
				serverMsg.put(readyMsg)
				command = msg.split("\n")

	import pygame
	from PygameGame import PygameGame
	from Player import Player
	from Ball import Ball
	from Scoreboard import Scoreboard

	class PlayGame(PygameGame):
		def __init__(self):
			super().__init__(width=1300, height=700, fps=60, title='MiniBall')
			self.bgColor = (50, 103, 68)

		def init(self):
			self.mode = 'lobbyScreen'
			self.showInstructions = False

			# Initialize the players
			self.playerGroup = pygame.sprite.Group()
			self.otherStrangers = dict()

			# Load the column images
			self.redCol = pygame.image.load('Images/LobbyScreen/redCol.png')
			redColWidth, redColHeight = self.redCol.get_size()
			self.redColRect = (self.width * 0.3 - redColWidth/2, self.height/2 - redColHeight/2,
						  self.width * 0.3 + redColWidth/2, self.height/2 + redColHeight/2)
			self.spectatorCol = pygame.image.load('Images/LobbyScreen/spectatorCol.png')
			spectatorColWidth, spectatorColHeight = self.spectatorCol.get_size()
			self.spectatorColRect = (self.width * 0.5 - spectatorColWidth/2, self.height/2 - spectatorColHeight/2,
								self.width * 0.5 + spectatorColWidth/2, self.height/2 + spectatorColHeight/2)
			self.blueCol = pygame.image.load('Images/LobbyScreen/blueCol.png')
			blueColWidth, blueColHeight = self.blueCol.get_size()
			self.blueColRect = (self.width * 0.7 - blueColWidth/2, self.height/2 - blueColHeight/2,
						  self.width * 0.7 + blueColWidth/2, self.height/2 + blueColHeight/2)

			self.startButtonDir = 'Images/LobbyScreen/startButton.png'
			startButton = pygame.image.load(self.startButtonDir)
			startButtonWidth, startButtonHeight = startButton.get_size()
			self.startButtonLeft, self.startButtonTop = self.width/2 - startButtonWidth/2, self.height * 0.9 - startButtonHeight/2
			self.startButtonRight, self.startButtonBottom = self.width/2 + startButtonWidth/2, self.height * 0.9 + startButtonHeight/2
			self.startButtonRect = (self.startButtonLeft, self.startButtonTop, self.startButtonRight, self.startButtonBottom)

			# Highlight the start game button if the mouse is over it
			if not isHost:
				self.startButtonDir = 'Images/LobbyScreen/waiting.png'
			else:
				mx, my = pygame.mouse.get_pos()
				if mx >= self.startButtonLeft and mx <= self.startButtonRight and my >= self.startButtonTop and my <= self.startButtonBottom:
					self.startButtonDir = 'Images/LobbyScreen/startButtonHigh.png'
				else: self.startButtonDir = 'Images/LobbyScreen/startButton.png'

			# Used for assigning teams
			self.redTeam = []
			self.blueTeam = []
			self.spectators = []
			self.teamNames = ['red', 'spectator', 'blue']
			self.teams = [self.redTeam, self.spectators, self.blueTeam]

			# Initialize the back button
			self.backButton = pygame.image.load('Images/backButton.png')
			self.backW, self.backH = self.backButton.get_size()
			self.backButtonMargin = self.width * 0.02
			self.backRect = (self.backButtonMargin, self.backButtonMargin, self.backButtonMargin + self.backW,
						self.backButtonMargin + self.backH)

		def initGame(self):
			self.mode = 'playGame'
			self.screenDimensions = (0, 0, self.width, self.height)

			# Initialize the field
			self.fieldImage = pygame.image.load('Images/pitch.png')
			self.fieldWidth, self.fieldHeight = self.fieldImage.get_size()
			self.fieldLeft, self.fieldBottom = self.width/2 - self.fieldWidth/2, self.height * 0.9
			self.fieldRight, self.fieldTop = self.width-self.fieldLeft, self.fieldBottom - self.fieldHeight
			
			self.fieldDimensions = (self.fieldLeft, self.fieldTop, self.fieldRight, self.fieldBottom)
			self.pitchDimensions = (0, self.fieldTop - self.height * 0.1, self.width, self.height)

			# Initialize the goals
			self.goal1Image, self.goal2Image = pygame.image.load('Images/goal1.png'), pygame.image.load('Images/goal2.png')
			self.goalWidth, self.goalHeight = self.goal1Image.get_size()
			self.goal1Left, self.goal1Right = self.fieldLeft - self.goalWidth, self.fieldLeft
			self.goal1Top, self.goal1Bottom = (self.fieldBottom + self.fieldTop)/2 - self.goalHeight/2, (self.fieldBottom + self.fieldTop)/2 + self.goalHeight/2
			self.goal2Left, self.goal2Right = self.fieldRight, self.fieldRight + self.goalWidth
			self.goal2Top, self.goal2Bottom = (self.fieldBottom + self.fieldTop)/2 - self.goalHeight/2, (self.fieldBottom + self.fieldTop)/2 + self.goalHeight/2

			self.goal1Rect = (self.goal1Left, self.goal1Top, self.goal1Right, self.goal1Bottom)
			self.goal2Rect = (self.goal2Left, self.goal2Top, self.goal2Right, self.goal2Bottom)
			self.goalsDimensions = (self.goal1Top, self.goal1Bottom, self.goalWidth)

			# Initialize the ball
			ball = Ball.init()
			self.ball = Ball((self.fieldLeft + self.fieldRight)/2, (self.fieldTop + self.fieldBottom)/2)
			self.ballGroup = pygame.sprite.Group(self.ball)

			# Initialize the scoreboard
			self.scoreboard = Scoreboard((self.width, self.height))
			self.possession = 'red'
			self.kickOff = False
			self.prevTime = 0

			# Place the players for red and blue onto the field
			self.playerGroup = pygame.sprite.Group()
			for i in range(len(self.redTeam)):
				redPlayer = self.redTeam[i]
				redPlayer.setPosition((self.fieldLeft + self.fieldRight)/4, self.fieldTop + (self.fieldHeight * (i + 1) / (len(self.redTeam) + 1)))
				self.playerGroup.add(redPlayer)

			for j in range(len(self.blueTeam)):
				bluePlayer = self.blueTeam[j]
				bluePlayer.setPosition((self.fieldLeft + self.fieldRight) * 3/4, self.fieldTop + (self.fieldHeight * (i + 1) / (len(self.blueTeam) + 1)))
				self.playerGroup.add(bluePlayer)

			self.helpButton = pygame.image.load('Images/helpButton.png')
			self.helpW, self.helpH = self.helpButton.get_size()
			self.helpButtonMargin = 2 * self.backButtonMargin + self.backW
			self.helpRect = (self.helpButtonMargin, self.backButtonMargin,
							self.helpButtonMargin + self.helpW, self.backButtonMargin + self.helpH)

		def reset(self):
			self.ball.resetPosition()
			for player in self.playerGroup:
				player.resetPosition()

		def quit(self):
			import __init__
			startScreen = __init__.StartGame()
			startScreen.run()

		def mousePressed(self, x, y):
			# Start button
			if isHost and self.mode == 'lobbyScreen':
				if x >= self.startButtonLeft and x <= self.startButtonRight and y >= self.startButtonTop and y <= self.startButtonBottom:
					msg = 'playGame None\n'
					print('sending: ', msg,)
					server.send(msg.encode())
					self.mode = 'playGame'
					self.initGame()
			# Back button
			if x >= self.backButtonMargin and x <= self.backButtonMargin + self.backW and \
				y >= self.backButtonMargin and y <= self.backButtonMargin + self.backH:
				if not self.showInstructions:
					msg = 'leftGame None\n'
					print('sending: ', msg,)
					server.send(msg.encode())
					self.quit()
				else:
					self.showInstructions = False

			elif x >= self.helpButtonMargin and x <= self.helpButtonMargin + self.helpW and \
				y >= self.backButtonMargin and y <= self.backButtonMargin + self.helpH:
				self.showInstructions = True

		def keyPressed(self, keyCode):
			if self.mode == 'lobbyScreen':
				# Players can change teams using the left and right keys
				if keyCode == (pygame.K_LEFT):
					currIndex = self.teamNames.index(self.me.team)
					nextIndex = (currIndex - 1) % 3
					if len(self.teams[nextIndex]) < 4:
						self.teams[currIndex].remove(self.me)
						self.me.changeTeam(self.teamNames[nextIndex])
						self.teams[nextIndex].append(self.me)
						# Send the message to the other players
						msg = 'changeTeam %s\n' % self.me.team
						print('sending: ', msg,)
						server.send(msg.encode())

				elif keyCode == (pygame.K_RIGHT):
					currIndex = self.teamNames.index(self.me.team)
					nextIndex = (currIndex + 1) % 3
					if len(self.teams[nextIndex]) < 4:
						self.teams[currIndex].remove(self.me)
						self.me.changeTeam(self.teamNames[nextIndex])
						self.teams[nextIndex].append(self.me)
						# Send the message to the other players
						msg = 'changeTeam %s\n' % self.me.team
						print('sending: ', msg,)
						server.send(msg.encode())

		def timerFired(self, dt):
			if self.mode == 'lobbyScreen' or not self.scoreboard.isGameOver():
				# Receive and execute instructions from other players
				while (serverMsg.qsize() > 0):
					msg = serverMsg.get(False)
					try:
						print('received: ', msg, '\n')
						msg = msg.split()
						command = msg[0]

						if command == 'myIDis':
							newPID = msg[1]
							self.me = Player(newPID, self.width/2, self.height/2)
							self.playerGroup.add(self.me)
							self.spectators.append(self.me)

						elif command == 'newPlayer':
							newPID = msg[1]
							self.otherStrangers[newPID] = Player(newPID, self.width/2, self.height/2)
							self.playerGroup.add(self.otherStrangers[newPID])
							self.spectators.append(self.otherStrangers[newPID])

						elif command == 'leftGame':
							PID = msg[1]
							player = self.otherStrangers[PID]
							currIndex = self.teamNames.index(player.team)
							self.teams[currIndex].remove(player)
							self.playerGroup.remove(player)

						elif command == 'playGame':
							self.mode = 'playGame'
							self.initGame()

						elif command == 'changeTeam':
							PID = msg[1]
							newTeam = msg[2]
							player = self.otherStrangers[PID]
							currIndex = self.teamNames.index(player.team)
							self.teams[currIndex].remove(player)
							player.changeTeam(newTeam)
							nextIndex = self.teamNames.index(player.team)
							self.teams[nextIndex].append(player)
							print(self.teamNames[nextIndex], self.teams[nextIndex])

						elif command == 'playerMoved':
							PID = msg[1]
							player = self.otherStrangers[PID]
							dx = int(msg[2])
							dy = int(msg[3])
							player.move(dx, dy)

						elif command == 'ballDribbled':
							PID = msg[1]
							player = self.otherStrangers[PID]
							self.ball.dribble(player)

						elif command == 'ballShot':
							PID = msg[1]
							player = self.otherStrangers[PID]
							self.ball.shoot(player)

						elif command == 'tick':
							self.scoreboard.tick()

						elif command == 'score':
							team = msg[2]
							self.scoreboard.teamScored(team)
							self.reset()
							if team == 'red': self.possession = 'blue'
							else: self.possession = 'red'
							self.scoreboard.toggleTimeRunning()
							self.kickOff = False

						elif command == 'updatePositions':
							self.ball.cx, self.ball.cy = float(msg[2]), float(msg[3])
							self.ball.vx, self.ball.vy = float(msg[4]), float(msg[5])
							numPlayers = (len(msg[2:]) - 4) // 4
							for i in range(1, numPlayers + 1):
								PID = 'Player' + str(i)
								if self.me.PID == PID: player = self.me
								else: player = self.otherStrangers[PID]
								player.cx, player.cy = float(msg[2 + (4 * i)]), float(msg[3 + (4 * i)])
								player.vx, player.vy = float(msg[4 + (4 * i)]), float(msg[5 + (4 * i)])

						elif command == 'kickOff':
							self.kickOff = True
							self.scoreboard.toggleTimeRunning()
					except:
						print('failed')
					serverMsg.task_done()

				# Send out instructions to other players
				if self.mode == 'playGame':
					# Move the players if the arrow keys are being pressed
					dx, dy = 0, 0
					if self.isKeyPressed(pygame.K_RIGHT): dx += 1
					if self.isKeyPressed(pygame.K_LEFT): dx += -1
					if self.isKeyPressed(pygame.K_UP): dy += -1
					if self.isKeyPressed(pygame.K_DOWN): dy += 1
					self.me.move(dx, dy)
					if not (dx == 0 and dy == 0):
						msg = 'playerMoved %d %d\n' % (dx, dy)
						print('sending: ', msg,)
						server.send(msg.encode())

					# If the are touching the ball then they can move it
					if pygame.sprite.collide_circle(self.me, self.ball):
						if not self.kickOff:
							self.scoreboard.toggleTimeRunning()
							msg = 'kickOff None\n'
							print('sending: ', msg,)
							server.send(msg.encode())
							self.kickOff = True
						self.ball.dribble(self.me)
						msg = 'ballDribbled None\n'
						print('sending: ', msg,)
						server.send(msg.encode())
						# If they press space they can shoot the ball
						if self.isKeyPressed(pygame.K_SPACE):
							self.ball.shoot(self.me)
							msg = 'ballShot None\n'
							print('sending: ', msg,)
							server.send(msg.encode())

					# Update the positions of the players and balls
					self.playerGroup.update(self.pitchDimensions, self.kickOff, self.possession)
					self.ball.update(self.fieldDimensions, self.goalsDimensions)

					# The hosts sends out the scoreboard information
					if isHost:
						# Handle the clock
						self.currTime = int(pygame.time.get_ticks() // 1000)
						if self.currTime == self.prevTime + 1:
							self.scoreboard.tick()
							msg = 'tick None\n'
							print('sending: ', msg,)
							server.send(msg.encode())
						self.prevTime = self.currTime
					
						# Handle the score
						scored = self.ball.isGoal(self.fieldDimensions, self.goalsDimensions)
						# Red team scores
						if scored[0]:
							self.scoreboard.teamScored('red')
							self.reset()
							self.possession = 'blue'
							self.scoreboard.toggleTimeRunning()
							self.kickOff = False
							msg = 'score red\n'
							print('sending: ', msg,)
							server.send(msg.encode())

						# Blue team scores
						elif scored[1]:
							self.scoreboard.teamScored('blue')
							self.reset()
							self.possession = 'red'
							self.scoreboard.toggleTimeRunning()
							self.kickOff = False
							msg = 'score blue\n'
							print('sending: ', msg,)
							server.send(msg.encode())

						# The host sends the position of all game objects so that the games don't go out of sync
						# and fuck shit up
						data = ''
						data += str(self.ball.cx) + ' ' + str(self.ball.cy) + ' ' + str(self.ball.vx) + ' ' + str(self.ball.vy)
						for i in range(1, len(self.otherStrangers) + 2):
							if i == 1: player = self.me
							else: player = self.otherStrangers['Player' + str(i)]
							data += ' ' + str(player.cx) + ' ' + str(player.cy) + ' ' + str(player.vx) + ' ' + str(player.vy)

						msg = 'updatePositions ' + data + '\n'
						print('sending update positions')
						server.send(msg.encode())

		def redrawAll(self, screen):
			if self.mode == 'lobbyScreen':
				# Place the players into their corresponding team columns
				for i in range(len(self.redTeam)):
					self.redTeam[i].setPosition(self.width * 0.3, self.height * 0.1 * (i + 3.5))

				for i in range(len(self.blueTeam)):
					self.blueTeam[i].setPosition(self.width * 0.7, self.height * 0.1 * (i + 3.5))

				if len(self.spectators) <= 4:
					for i in range(len(self.spectators)):
						self.spectators[i].setPosition(self.width * 0.5, self.height * 0.1 * (i + 3.5))
				else:
					for i in range(len(self.spectators)):
						if i < 4: xPos = self.width * 0.47
						else: xPos = self.width * 0.53
						self.spectators[i].setPosition(xPos, self.height * 0.1 * ((i % 4) + 3.5))

				# Draw the items onto the screen
				screen.blit(self.redCol, pygame.Rect(self.redColRect))
				screen.blit(self.spectatorCol, pygame.Rect(self.spectatorColRect))
				screen.blit(self.blueCol, pygame.Rect(self.blueColRect))
				screen.blit(pygame.image.load(self.startButtonDir), pygame.Rect(self.startButtonRect))
				self.drawIP(screen)
				self.playerGroup.draw(screen)
				screen.blit(self.backButton, pygame.Rect(self.backRect))

			elif self.mode == 'playGame':
				if self.showInstructions:
					instructions = pygame.image.load('Images/instructions1.png')
					screen.blit(instructions, (0,0))
					screen.blit(self.backButton, pygame.Rect(self.backRect))
				else:
					# Draw the field
					screen.blit(self.fieldImage, pygame.Rect(self.fieldLeft, self.fieldTop, self.fieldRight, self.fieldBottom))
					# Draw the goals
					screen.blit(self.goal1Image, pygame.Rect(self.goal1Rect))
					screen.blit(self.goal2Image, pygame.Rect(self.goal2Rect))
					# Draw the players
					self.playerGroup.draw(screen)
					self.ballGroup.draw(screen)
					self.scoreboard.display(screen)
					screen.blit(self.backButton, pygame.Rect(self.backRect))
					screen.blit(self.helpButton, pygame.Rect(self.helpRect))

					if self.scoreboard.isGameOver():
						winner = ''
						if self.scoreboard.redScore > self.scoreboard.blueScore: winner = 'red'
						else: winner = 'blue'
						gameOverImage = pygame.image.load('Images/' + winner + 'Wins.png')
						gOIWidth ,gOIHeight = gameOverImage.get_size()
						gameOverImageRect = (self.width/2 - gOIWidth/2, self.height/2 - gOIHeight/2, self.width/2 + gOIWidth/2, self.height/2 + gOIHeight/2)
						screen.blit(gameOverImage, pygame.Rect(gameOverImageRect))

		def drawIP(self, screen):
			width, height = pygame.image.load('Images/LobbyScreen/IPNumbers/0.png').get_size()
			width *= 0.7
			totalWidth = len(IP) * width
			startX = (self.width - totalWidth) / 2
			for i in range(len(IP)):
				s = IP[i]
				if s == '.': s = 'period'
				image = pygame.image.load('Images/LobbyScreen/IPNumbers/' + s + '.png')
				imageRect = (startX + (i * width), self.height * 0.02, startX + ((i + 1) * width), self.height * 0.02 + height)
				screen.blit(image, pygame.Rect(imageRect))

	serverMsg = Queue(100)
	threading.Thread(target = handleServerMsg, args = (server, serverMsg)).start()

	game = PlayGame()
	game.run()

if __name__ == '__main__':
	main()