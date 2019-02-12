# Player.py

import pygame, math
from GameObject import GameObject

class Player(GameObject):
	def __init__(self, PID, cx, cy, team='spectator'):
		imageDir = 'Images/Players/' + team + PID + '.png'
		image = pygame.image.load(imageDir)
		super().__init__(cx, cy, image)
		self.PID = PID
		self.team = team
		self.maxSpeed = 40
		self.mass = 10
		self.friction = 0.8

	def setPosition(self, cx, cy):
		self.__init__(self.PID, cx, cy, self.team)

	def changeTeam(self, team):
		self.__init__(self.PID, self.cx, self.cy, team)

	def move(self, dx, dy):
		self.vx += (dx * self.maxSpeed)
		self.vy += (dy * self.maxSpeed)

	def update(self, pitchDimensions, kickOff, possession):
		pitchLeft, pitchTop, pitchRight, pitchBottom = pitchDimensions

		centerX, centerY = (pitchLeft + pitchRight) / 2, (pitchBottom + pitchTop) / 2
		centerRadius = (pitchRight - pitchLeft) * 5/70

		if not kickOff:
			if self.team == 'red' and self.cx + self.radius > centerX and \
				(self.cy + self.radius < centerY - centerRadius * 0.9 or self.cy - self.radius > centerY + centerRadius * 0.9):
				self.cx = centerX - self.radius
			elif self.team == 'blue' and self.cx - self.radius < centerX and \
				(self.cy + self.radius < centerY - centerRadius * 0.9 or self.cy - self.radius > centerY + centerRadius* 0.9):
				self.cx = centerX + self.radius

			if possession != self.team:
				minDist = centerRadius + self.radius
				dist = math.sqrt((self.cx - centerX) ** 2 + (self.cy - centerY) ** 2)
				if dist <= minDist:
					relAngle = math.atan2((self.cy - centerY), (self.cx - centerX))
					self.cx = centerX + (centerRadius + self.radius) * math.cos(relAngle)
					self.cy = centerY + (centerRadius + self.radius) * math.sin(relAngle)
			else:
				maxDist = centerRadius + self.radius
				dist = math.sqrt((self.cx - centerX) ** 2 + (self.cy - centerY) ** 2)
				relAngle = math.atan2((self.cy - centerY), (self.cx - centerX))
				if self.team == 'red' and self.cx > centerX:
					if dist >= maxDist - self.radius:
						self.cx = centerX + (centerRadius - self.radius) * math.cos(relAngle)
						self.cy = centerY + (centerRadius - self.radius) * math.sin(relAngle)
				elif self.team == 'blue' and self.cx < centerX:
					if dist >= maxDist - self.radius:
						self.cx = centerX + (centerRadius - self.radius) * math.cos(relAngle)
						self.cy = centerY + (centerRadius - self.radius) * math.sin(relAngle)

		angle = math.atan2(self.vy, self.vx)
		currSpeed = math.sqrt((self.vx ** 2) + (self.vy ** 2))
		# This keeps the speed of the player constant
		if currSpeed > self.maxSpeed:
			self.vx = self.maxSpeed * math.cos(angle)
			self.vy = self.maxSpeed * math.sin(angle)

		# Friction is in effect at all times and slows the players down
		self.vx *= (1-self.friction)
		self.vy *= (1-self.friction)

		super().update(pitchDimensions)