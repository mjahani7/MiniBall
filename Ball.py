# Ball.py

import pygame, math
from GameObject import GameObject

class Ball(GameObject):
	@staticmethod
	def init():
		Ball.image = pygame.image.load('Images/ball.png')

	def __init__(self, cx, cy): # All players have a radius of 5
		super().__init__(cx, cy, Ball.image)
		self.speed = 25
		self.mass = 10
		self.friction = 0.05

	def resetPosition(self):
		super().resetPosition()
		self.vx, self.vy = 0, 0

	def dribble(self, player):
		# Find the angle at which the ball is hit
		x1, y1, r1 = self.cx, self.cy, self.radius
		x2, y2, r2 = player.cx, player.cy, player.radius
		angle = math.atan2((y1-y2), (x1-x2))

		# The player cannot go through the ball (the player dribbles the ball)
		distance = math.sqrt((x1-x2)**2 + (y1-y2)**2)
		minDistance = r1 + r2
		if distance < minDistance:
			self.cx = x2 + (minDistance * math.cos(angle))
			self.cy = y2 + (minDistance * math.sin(angle))

	def shoot(self, player):
		# Find the angle at which the ball is hit
		x1, y1, r1 = self.cx, self.cy, self.radius
		x2, y2, r2 = player.cx, player.cy, player.radius
		angle = math.atan2((y1-y2), (x1-x2))

		# The ball accelerates away from the player in the angle which it is hit
		self.vx += self.speed * math.cos(angle)
		self.vy += self.speed * math.sin(angle)

	def update(self, fieldDimensions, goalDimensions):
		# Friction always acts on the ball
		self.vx *= (1-self.friction)
		self.vy *= (1-self.friction)

		# This keeps the speed of the ball constant
		if (self.vx > self.speed): self.vx = self.speed
		elif (self.vx < -self.speed): self.vx = -self.speed
		if (self.vy > self.speed): self.vy = self.speed
		elif (self.vy < -self.speed): self.vy = -self.speed

		# Make the ball bounce when it hits a wall
		fieldLeft, fieldTop, fieldRight, fieldBottom = fieldDimensions
		goalTop, goalBottom, goalWidth = goalDimensions
		self.updateRect()

		# When the ball hits a wall it (not the goals) bounces and slows down
		if (self.rect.right > fieldRight) and (self.rect.bottom < goalTop or self.rect.top > goalBottom):
			self.cx = fieldRight - (self.width / 2)
			self.vx *= -0.75
		elif self.rect.left < fieldLeft and (self.rect.bottom < goalTop or self.rect.top > goalBottom):
			self.cx = fieldLeft + self.width / 2
			self.vx *= -0.75
		if self.rect.bottom > fieldBottom:
			self.cy = fieldBottom - (self.height / 2)
			self.vy *= -0.75
		elif self.rect.top < fieldTop:
			self.cy = fieldTop + self.height / 2
			self.vy *= -0.75

		# When the ball enters the goal make it stop
		if (self.rect.right > fieldRight) and (self.rect.bottom > goalTop) and (self.rect.top < goalBottom):
			if self.rect.right > fieldRight + goalWidth:
				self.vx, self.vy = 0, 0
				self.cx = fieldRight + goalWidth - self.radius
			if self.rect.top < goalTop:
				self.cy = goalTop + self.radius
			elif self.rect.bottom > goalBottom:
				self.cy = goalBottom - self.radius
		elif (self.rect.left < fieldLeft) and (self.rect.bottom > goalTop) and (self.rect.top < goalBottom):
			if self.rect.left < fieldLeft - goalWidth:
				self.vx, self.vy = 0, 0
				self.cx = fieldLeft - goalWidth + self.radius
			if self.rect.top < goalTop:
				self.cy = goalTop + self.radius
			elif self.rect.bottom > goalBottom:
				self.cy = goalBottom - self.radius

		self.cx += self.vx
		self.cy += self.vy
		self.updateRect()

	def isGoal(self, fieldDimensions , goalDimensions):
		fieldLeft, fieldTop, fieldRight, fieldBottom = fieldDimensions
		goalTop, goalBottom, goalWidth = goalDimensions
		redTeam, blueTeam = False, False
		if (self.rect.left > fieldRight) and (self.rect.bottom > goalTop) and (self.rect.top < goalBottom):
			redTeam = True
		elif (self.rect.right < fieldLeft) and (self.rect.bottom > goalTop) and (self.rect.top < goalBottom):
			blueTeam = True
		return (redTeam, blueTeam)