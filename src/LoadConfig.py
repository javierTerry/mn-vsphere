#!/bin/python

import configparser

<<<<<<< HEAD



class ConfigInit:

	def __init__(self):
		self.config = configparser.ConfigParser()
			

	def loadFile(self):
		self.config = config.read('config/config.ini')
=======
class ConfigInit:

	def __init__(self):
		config = configparser.ConfigParser()
		config.read('config.ini')
		for section in config.sections():
			print(section)

		self.config	= config
>>>>>>> 22fd5fceb0dc7ccd500eebc739859afa17d0e013



if __name__=='__main__':  #Cuerpo Principal
<<<<<<< HEAD
    config = ConfigInit()
=======
    config = ConfigInit()
>>>>>>> 22fd5fceb0dc7ccd500eebc739859afa17d0e013
