# local.py
# Offline Multiplayer (1v1)

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
		self.mode = 'game'
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

		# Initialize the players
		self.player1 = Player('Player1', (self.fieldLeft + self.fieldRight)/4, (self.fieldTop + self.fieldBottom)/2, 'red')
		self.player2 = Player('Player2', (self.fieldLeft + self.fieldRight) * 3/4, (self.fieldTop + self.fieldBottom)/2, 'blue')
		self.playerGroup = pygame.sprite.Group(self.player1, self.player2)

		# Initialize the scoreboard
		self.scoreboard = Scoreboard((self.width, self.height))

		self.possession = 'red'
		self.kickOff = False

		# Initialize the back button
		self.backButton = pygame.image.load('Images/backButton.png')
		self.backW, self.backH = self.backButton.get_size()
		self.backButtonMargin = self.width * 0.02
		self.backRect = (self.backButtonMargin, self.backButtonMargin, self.backButtonMargin + self.backW,
					self.backButtonMargin + self.backH)

		self.helpButton = pygame.image.load('Images/helpButton.png')
		self.helpW, self.helpH = self.helpButton.get_size()
		self.helpButtonMargin = 2 * self.backButtonMargin + self.backW
		self.helpRect = (self.helpButtonMargin, self.backButtonMargin,
						self.helpButtonMargin + self.helpW, self.backButtonMargin + self.helpH)

		self.prevTime = 0

	def reset(self):
		self.ball.resetPosition()
		for player in self.playerGroup:
			player.resetPosition()

	def mousePressed(self, x, y):
		if x >= self.backButtonMargin and x <= self.backButtonMargin + self.backW and \
			y >= self.backButtonMargin and y <= self.backButtonMargin + self.backH:
			if self.mode == 'game':
				import __init__
				start = __init__.StartGame()
				start.run()
			elif self.mode == 'instructions':
				self.mode = 'game'
				self.scoreboard.toggleTimeRunning()
		elif x >= self.helpButtonMargin and x <= self.helpButtonMargin + self.helpW and \
			y >= self.backButtonMargin and y <= self.backButtonMargin + self.helpH:
			self.mode = 'instructions'
			self.scoreboard.toggleTimeRunning()

	def timerFired(self, dt):
		if not self.scoreboard.isGameOver():
			# Set the time on the scoreboard
			self.currTime = int(pygame.time.get_ticks() // 1000)
			if self.currTime >= self.prevTime + 1:
				self.scoreboard.tick()
			self.prevTime = self.currTime

			# Detect collisisons between the ball and the players and only move the ball if a player is moving it
			for player in self.playerGroup:
				if player is self.player1:
					# Move the players if the arrow keys are being pressed
					dx, dy = 0, 0
					if self.isKeyPressed(pygame.K_RIGHT): dx += 1
					if self.isKeyPressed(pygame.K_LEFT): dx += -1
					if self.isKeyPressed(pygame.K_UP): dy += -1
					if self.isKeyPressed(pygame.K_DOWN): dy += 1
					player.move(dx, dy)

					# If the are touching the ball then they can move it 
					if pygame.sprite.collide_circle(player, self.ball):
						if not self.kickOff: self.scoreboard.toggleTimeRunning()
						self.kickOff = True
						self.ball.dribble(player)
						# If they press space they can shoot the ball
						if self.isKeyPressed(pygame.K_SPACE):
							self.ball.shoot(player)
				elif player is self.player2:
					# Move the players if the arrow keys are being pressed
					dx, dy = 0, 0
					if self.isKeyPressed(pygame.K_d): dx += 1
					if self.isKeyPressed(pygame.K_a): dx += -1
					if self.isKeyPressed(pygame.K_w): dy += -1
					if self.isKeyPressed(pygame.K_s): dy += 1
					player.move(dx, dy)

					# If the are touching the ball then they can move it 
					if pygame.sprite.collide_circle(player, self.ball):
						if not self.kickOff: self.scoreboard.toggleTimeRunning()
						self.kickOff = True
						self.ball.dribble(player)
						# If they press space they can shoot the ball
						if self.isKeyPressed(pygame.K_TAB):
							self.ball.shoot(player)
				# Update the positions of the players and balls
			self.playerGroup.update(self.pitchDimensions, self.kickOff, self.possession)
			self.ball.update(self.fieldDimensions, self.goalsDimensions)
			
			scored = self.ball.isGoal(self.fieldDimensions, self.goalsDimensions)
			# Red team scores
			if scored[0]:
				self.scoreboard.teamScored('red')
				self.reset()
				self.possession = 'blue'
				self.scoreboard.toggleTimeRunning()
				self.kickOff = False

			# Blue team scores
			elif scored[1]:
				self.scoreboard.teamScored('blue')
				self.reset()
				self.possession = 'red'
				self.scoreboard.toggleTimeRunning()
				self.kickOff = False

	def redrawAll(self, screen):
		if self.mode == 'instructions':
			instructions = pygame.image.load('Images/instructions2.png')
			screen.blit(instructions, (0,0))
			screen.blit(self.backButton, pygame.Rect(self.backRect))

		elif self.mode == 'game':
			# Draw the field
			screen.blit(self.fieldImage, pygame.Rect(self.fieldLeft, self.fieldTop, self.fieldRight, self.fieldBottom))
			# Draw the goals
			screen.blit(self.goal1Image, pygame.Rect(self.goal1Rect))
			screen.blit(self.goal2Image, pygame.Rect(self.goal2Rect))
			# Draw the players
			self.playerGroup.draw(screen)
			# Draw the ball
			self.ballGroup.draw(screen)
			# Draw the scoreboard and back button
			self.scoreboard.display(screen)
			screen.blit(self.helpButton, pygame.Rect(self.helpRect))
			screen.blit(self.backButton, pygame.Rect(self.backRect))

		if self.scoreboard.isGameOver():
			winner = ''
			if self.scoreboard.redScore > self.scoreboard.blueScore: winner = 'red'
			else: winner = 'blue'
			gameOverImage = pygame.image.load('Images/' + winner + 'Wins.png')
			gOIWidth ,gOIHeight = gameOverImage.get_size()
			gameOverImageRect = (self.width/2 - gOIWidth/2, self.height/2 - gOIHeight/2, self.width/2 + gOIWidth/2, self.height/2 + gOIHeight/2)
			screen.blit(gameOverImage, pygame.Rect(gameOverImageRect))

def main():
	game = PlayGame()
	game.run()

if __name__ == '__main__':
    main()