# GameObject.py
# Creates the basics of motion for game objects

import pygame

class GameObject(pygame.sprite.Sprite): # Create the game objects as a sprite
	def __init__(self, cx, cy, image):
		super().__init__()
		self.cx, self.cy, self.image = cx, cy, image
		self.radius = self.image.get_width() / 2
		self.updateRect()
		self.vx, self.vy = 0, 0 # Object's velocity
		self.originalCx, self.originalCy = cx, cy

	def resetPosition(self):
		self.cx, self.cy = self.originalCx, self.originalCy

	def updateRect(self):
		# Update the object's rect attribute with the new x,y coordinates
		w, h = self.image.get_size()
		self.width, self.height = w, h
		self.rect = pygame.Rect(self.cx - w / 2, self.cy - h / 2, w, h)

	def update(self, surfaceDimensions):
		surfaceLeft, surfaceTop, surfaceRight, surfaceBottom = surfaceDimensions
		self.cx += self.vx
		self.cy += self.vy
		self.updateRect()

		# Prevent the object from leaving the surface
		if self.rect.right > surfaceRight:
			self.cx = surfaceRight - (self.width / 2)
		elif self.rect.left < surfaceLeft:
			self.cx = surfaceLeft + (self.width / 2)
		elif self.rect.bottom > surfaceBottom:
			self.cy = surfaceBottom - (self.height / 2)
		if self.rect.top < surfaceTop:
			self.cy = surfaceTop + (self.height / 2)
		self.updateRect()