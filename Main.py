#!/usr/bin/python

import smtplib
from smtplib import SMTPException
from src import argumento
import vm-list

class Smtp:
	try:
		def __init__(self, receivers, message ):
			self.sender = ''
			self.receivers = receivers
			if ( len(receivers) < 1 ):
				self.receivers = self.sender
			
			self.message = message

		
		def send(self):
			smtpObj = smtplib.SMTP('', 25)
			smtpObj.sendmail(self.sender, self.receivers, self.message)         
			print "Successfully sent email"

	except SMTPException:
		raise
	   	print "Error: unable to send email"



if __name__=='__main__':  #Cuerpo Principal
	
	args = argumento.get()

	print args
	exit()
	receivers = ['javierv31@gmail.com']
	message = "Subject: Depuracion Snap - Alica - QRO \
	 \n\n hola mundo"
	smpt = Smtp(receivers, message)
	smpt.send()