# Scoreboard.py

import pygame

class Scoreboard(object):
	def __init__(self, screenDimensions):
		self.redScore, self.blueScore = 0, 0
		self.time = 0
		self.timeRunning = False
		self.width, self.height = screenDimensions
		
		# Team icon
		self.redTeamImage, self.blueTeamImage = pygame.image.load('Images/redTeam.png'), pygame.image.load('Images/blueTeam.png')
		teamImageWidth, teamImageHeight = self.redTeamImage.get_size()
		self.redTeamRect = (self.width * 0.43 - teamImageWidth/2, self.height * 0.09 - teamImageHeight/2,\
							self.width * 0.43 + teamImageWidth/2, self.height * 0.09 + teamImageHeight/2)
		self.blueTeamRect = (self.width * 0.57 - teamImageWidth/2, self.height * 0.09 - teamImageHeight/2,\
							 self.width * 0.57 + teamImageWidth/2, self.height * 0.09 + teamImageHeight/2)

		# The dash between the scores
		self.dashImage = pygame.image.load('Images/Numbers/dash.png')
		dashWidth, dashHeight = self.dashImage.get_size()
		self.dashRect = (self.width/2 - dashWidth/2, self.height * 0.095 - dashHeight/2, self.width/2 + dashWidth/2, self.height * 0.095 + dashHeight/2)

		# The colon between the minute and seconds
		self.colonImage = pygame.image.load('Images/Numbers/colon.png')
		colonWidth, colonHeight = self.colonImage.get_size()
		self.colonRect = (self.width * 0.8 - colonWidth/2, self.height * 0.095 - colonHeight/2, self.width * 0.8 - colonWidth/2, self.height * 0.095 - colonHeight/2)

	def teamScored(self, team):
		if team == 'red': self.redScore += 1
		else: self.blueScore += 1

	def toggleTimeRunning(self):
		self.timeRunning = not self.timeRunning

	def setTime(self, time):
		if self.timeRunning:
			self.time = time

	def tick(self):
		if self.timeRunning:
			self.time += 1

	def isGameOver(self):
		# If either team has scored 5 goals or the game has gone on for 5 minutes (300 seconds), the game is over
		if self.redScore >= 5 or self.blueScore >= 5 and self.redScore != self.blueScore:
			return True
		elif self.time >= 300 and self.redScore != self.blueScore:
			return True
		return False

	def display(self, screen):
		# Find the image for the scores
		redScoreDir = 'Images/Numbers/' + str(self.redScore) + '.png'
		blueScoreDir = 'Images/Numbers/' + str(self.blueScore) + '.png'
		redScoreImage = pygame.image.load(redScoreDir)
		redScoreWidth, redScoreHeight = redScoreImage.get_size()
		redScoreRect = (self.width * 0.475 - redScoreWidth/2, self.height * 0.1 - redScoreHeight/2,\
						self.width * 0.475 + redScoreWidth/2, self.height * 0.1 + redScoreHeight/2)
		blueScoreImage = pygame.image.load(blueScoreDir)
		blueScoreWidth, blueScoreHeight = blueScoreImage.get_size()
		blueScoreRect = (self.width * 0.525 - blueScoreWidth/2, self.height * 0.1 - blueScoreHeight/2,\
						self.width * 0.525 + blueScoreWidth/2, self.height * 0.1 + blueScoreHeight/2)

		# Draw the scoreboard
		screen.blit(self.dashImage, pygame.Rect(self.dashRect))
		screen.blit(self.redTeamImage, pygame.Rect(self.redTeamRect))
		screen.blit(self.blueTeamImage, pygame.Rect(self.blueTeamRect))
		screen.blit(redScoreImage, pygame.Rect(redScoreRect))
		screen.blit(blueScoreImage, pygame.Rect(blueScoreRect))

		# Initalize the time
		minute = self.time // 60
		seconds = self.time % 60
		tensSeconds, onesSeconds = seconds // 10, seconds % 10
		minuteDir = 'Images/Numbers/' + str(minute) + '.png'
		tensDir = 'Images/Numbers/' + str(tensSeconds) + '.png'
		onesDir = 'Images/Numbers/' + str(onesSeconds) + '.png'
		minuteImage = pygame.image.load(minuteDir)
		minuteWidth, minuteHeight = minuteImage.get_size()
		minuteRect = (self.width * 0.78 - minuteWidth/2, self.height * 0.1 - minuteHeight/2, self.width * 0.78 + minuteWidth/2, self.height * 0.1 + minuteHeight/2)
		tensImage = pygame.image.load(tensDir)
		tensWidth, tensHeight = tensImage.get_size()
		tensRect = (self.width * 0.82 - tensWidth/2, self.height * 0.1 - tensHeight/2, self.width * 0.82 + tensWidth/2, self.height * 0.1 + tensHeight/2)
		onesImage = pygame.image.load(onesDir)
		onesWidth, onesHeight = onesImage.get_size()
		onesRect = (self.width * 0.8425 - onesWidth/2, self.height * 0.1 - onesHeight/2, self.width * 0.8425 + onesWidth/2, self.height * 0.1 + tensHeight/2)

		if self.time <= 300:
			# Draw the time
			screen.blit(self.colonImage, pygame.Rect(self.colonRect))
			screen.blit(minuteImage, pygame.Rect(minuteRect))
			screen.blit(tensImage, pygame.Rect(tensRect))
			screen.blit(onesImage, pygame.Rect(onesRect))
		else:
			overtime = pygame.image.load('Images/Numbers/overtime.png')
			screen.blit(overtime, (self.width * 0.78 - minuteWidth/2, self.height * 0.1 - minuteHeight/2))