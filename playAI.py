# playAI.py
# Play against the computer

import pygame, math
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

		self.kickOff = False
		self.possession = 'red'
		
		# Initialize the back button and instructions page
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

	def moveComputer(self):
		# First determine the game state
		# Possible game states are: 
    #             1) Opponent is in possession of the ball
		#							2) Computer is in possession of the ball
		#							3) Neither players are in possession of the ball
		if pygame.sprite.collide_circle(self.player1, self.ball):
			gameState = 'defense'
		elif pygame.sprite.collide_circle(self.player2, self.ball):
			gameState = 'attack'
		else:
			# If neither players are in possession of the ball then whoever is closest
			# is considered to have possession
			playerDist = math.sqrt((self.ball.cx - self.player1.cx) ** 2 + (self.ball.cy - self.player1.cy) ** 2)
			computerDist = math.sqrt((self.ball.cx - self.player2.cx) ** 2 + (self.ball.cy - self.player2.cy) ** 2)
			if playerDist < computerDist: gameState = 'defense'
			else: gameState = 'attack'

		marginOfError = self.player2.radius / 2

		if gameState == 'defense':
			dx, dy = 0, 0
			marginOfDef = 100
			# Determine which half the ball is in
			if self.ball.cx >= (self.fieldRight + self.fieldLeft)/2:
				ballHalf = 'own'
			else: ballHalf = 'opponent'
			
			# If the ball is in own half, block the line to goal if there is one,
			# and move closer to the ball if not
			if ballHalf == 'own':
				# m = (y2-y1)/(x2-x1)
				slope = (self.ball.cy - self.player1.cy) / (self.ball.cx - self.player1.cx)
				# b = y - mx
				intercept = self.ball.cy - (slope * self.ball.cx)
				# Extrapolate where the ball will end up if hit at the current angle
				y = (slope * self.fieldRight) + intercept
				# If the ball will end up in the goal, move towards that line to block the angle
				if (y >= self.goal2Top) and (y <= self.goal2Bottom):
					desiredPos = (slope * self.player2.cx) + intercept
					if self.player2.cy <= desiredPos + marginOfError and self.player2.cy >= desiredPos - marginOfError:
						dy = 0
					elif self.player2.cy < desiredPos - marginOfError:
						dy = 1
					else: dy = -1
					# If the ball is behind you move back
					if (self.ball.cx + marginOfDef <= self.fieldRight) and \
						(self.ball.cx + marginOfDef > self.player2.cx):
						dx = 1

				# If not move towards the ball and close in on the opponent
				else:
					if self.ball.cy - marginOfError <= self.player2.cy and self.ball.cy + marginOfError >= self.player2.cy:
						dy = 0
					elif self.ball.cy - marginOfError > self.player2.cy:
						dy = 1
					else:
						dy = -1

					# If the ball is infront, move forward
					if (self.ball.cx + marginOfDef - marginOfError <= self.player2.cx) and (self.ball.cx + marginOfDef + marginOfError >= self.player2.cx):
						dx = 0
					elif self.ball.cx + marginOfDef + marginOfError < self.player2.cx:
						dx = -1
					# The player shouldn't be behidn the goal line
					elif self.player2.cx <= self.fieldRight:
						dx = 1

			# If the ball is in opponent's half
			elif ballHalf == 'opponent':
				# Prevent the ball from getting to your half by standing in front of the ball
				if self.ball.cy - marginOfError <= self.player2.cy and self.ball.cy + marginOfError >= self.player2.cy:
					dy = 0
				elif self.ball.cy - marginOfError > self.player2.cy:
					dy = 1
				else:
					dy = -1

				# If the ball is infront, move forward
				if (self.ball.cx - marginOfError <= self.player2.cx) and (self.ball.cx + marginOfError >= self.player2.cx):
					dx = 0
				elif self.ball.cx + marginOfError < self.player2.cx:
					dx = -1
				else: dx = 1

			# Move the player
			self.player2.move(dx, dy)

		elif gameState == 'attack':
			dx, dy = 0, 0
			kick = False
			# Check if in possession of the ball
			if pygame.sprite.collide_circle(self.player2, self.ball):
				possess = True
				if not self.kickOff: self.scoreboard.toggleTimeRunning()
				self.kickOff = True
			else: possess = False

			# If not in possession of the ball go towards it
			if not possess:
				desiredPos = self.ball.cx + self.ball.radius + self.player2.radius
				if self.player2.cx >= desiredPos - marginOfError and self.player2.cx <= desiredPos:
					dx = 0
				elif self.player2.cx > desiredPos:
					dx = -1
				else: dx = 1
				
				if self.ball.cy - marginOfError <= self.player2.cy and self.ball.cy + marginOfError >= self.player2.cy:
					dy = 0
				elif self.ball.cy - marginOfError > self.player2.cy:
					dy = 1
				else:
					dy = -1

			else: # If in possession
				# Move forward
				dx = -1
				# Determine if opponent is behind or infront of you
				if self.player1.cx >= self.player2.cx: behind = True
				else: behind = False

				# If the opponent is behind you then try to kick it forward
				if behind:
					if self.player2.cx >= self.ball.cx: # Only kick if behind the ball
						slope = (self.ball.cy - self.player2.cy) / (self.ball.cx - self.player2.cx)
						intercept = self.ball.cy - (slope * self.ball.cx)
						y = (slope * self.fieldLeft) + intercept
						# If the ball will go towards the goal kick it
						if (y >= self.goal1Top) and (y <= self.goal1Bottom):
							kick = True
						# If not then adjust so that it would
						elif y < self.goal1Top: dy = -1
						else: dy = 1

				else: # If not behind
					# Determine which half the opponent is in
					if self.player1.cx >= (self.fieldRight + self.fieldLeft)/2:
						ballHalf = 'own'
					else: ballHalf = 'opponent'

					# If in opponent half and have a clear shot,take it
					slope = (self.ball.cy - self.player2.cy) / (self.ball.cx - self.player2.cx)
					intercept = self.ball.cy - (slope * self.ball.cx)
					y = (slope * self.fieldLeft) + intercept
					oppY = (slope * self.player1.cx) + intercept
					threshold = 200
					# If the opponent is not blocking it shoot
					if ballHalf == 'opponent' and self.player2.cx >= self.ball.cx and \
						(y >= self.goal1Top) and (y <= self.goal1Bottom) and \
						not ((self.player1.cy + self.player1.radius) >= oppY and (self.player1.cy - self.player1.radius) <= oppY):
						kick = True

					# If there's no clear shot dribble forward, when near the opponent kick the ball around a wall
					elif self.player2.cx - self.player1.cx < threshold and self.player2.cx >= self.ball.cx:
						# Move away from the closest wall and kick in that direction
						if self.fieldBottom - self.player2.cy >= self.fieldWidth / 2:
							closestWall = 'top'
						else: closestWall = 'bottom'
						if closestWall == 'top':
							dy = 1
						else: dy = -1
						kick = True
					elif self.player2.cx < self.ball.cx:
						dx = 1
						dy = -1
					elif self.player2.cy <= self.ball.cy + marginOfError and self.player2.cy >= self.ball.cy - marginOfError:
						dy = 0
						dx = 1
					else:
						dx = -1

			self.player2.move(dx, dy)
			self.ball.dribble(self.player2)
			if kick: self.ball.shoot(self.player2)

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
					self.moveComputer()
				# Update the positions of the players and balls
			self.playerGroup.update(self.pitchDimensions, self.kickOff, self.possession)
			self.ball.update(self.fieldDimensions, self.goalsDimensions)
			
			scored = self.ball.isGoal(self.fieldDimensions, self.goalsDimensions)
			# Red team scores
			if scored[0]:
				self.scoreboard.teamScored('red')
				self.reset()
				self.possession = 'blue'
				self.kickOff = False

			# Blue team scores
			elif scored[1]:
				self.scoreboard.teamScored('blue')
				self.reset()
				self.possession = 'red'
				self.kickOff = False

	def redrawAll(self, screen):
		if self.mode == 'instructions':
			instructions = pygame.image.load('Images/instructions1.png')
			screen.blit(instructions, (0,0))
			screen.blit(self.backButton, pygame.Rect(self.backRect))

		elif self.mode == 'game':
			# Back button
			screen.blit(self.backButton, pygame.Rect(self.backRect))
			# Draw the field
			screen.blit(self.fieldImage, pygame.Rect(self.fieldLeft, self.fieldTop, self.fieldRight, self.fieldBottom))
			# Draw the goals
			screen.blit(self.goal1Image, pygame.Rect(self.goal1Rect))
			screen.blit(self.goal2Image, pygame.Rect(self.goal2Rect))
			# Draw the players
			self.playerGroup.draw(screen)
			# Draw the ball
			self.ballGroup.draw(screen)
			# Draw the scoreboard and the help button
			self.scoreboard.display(screen)
			screen.blit(self.helpButton, pygame.Rect(self.helpRect))

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