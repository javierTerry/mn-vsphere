#!/usr/bin/python

from smtplib import SMTPException
import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import json
import logging


class Smtp:
	try:

		def __init__(self):
			"""
			Validar
			"""	
			with open('src/config/config.json') as json_data_file :
				cfg = json.load(json_data_file)

			self.fromSmtp = "No Reply no_replay_default@kionetworks.com"
			self.host = cfg['SMTP']


			self.message = """From: {} \nTo: {} \nSubject: {}
			\nMensaje enviado de forma automatica  \n{}"""

		def send(self, subject, receivers, body):
			"""
				send_simple 
				Envia un correo sin adjuntos
			"""
			message = self.message.format( self.fromSmtp, receivers, subject, body)
			
			smtpObj = smtplib.SMTP(self.host, 25)
			smtpObj.sendmail(self.fromSmtp, receivers ,message)         
			
			logging.info("Successfully sent email")
			smtpObj.quit()

		def send_attach(self, subject, receiver_email,attachText):
						# Create secure connection with server and send email
			context = ssl.create_default_context()
			

			message = MIMEMultipart("alternative")
			message["Subject"] = "multipart test"
			message["From"] = sender_email
			message["To"] = receiver_email

			# Turn these into plain/html MIMEText objects
			part1 = MIMEText(attachText, "plain")
			#part2 = MIMEText(html, "html")

			# Add HTML/plain-text parts to MIMEMultipart message
			# The email client will try to render the last part first
			message.attach(part1)
			#message.attach(part2)
			# Create secure connection with server and send email
			#context = ssl.create_default_context()
			smtpObj = smtplib.SMTP('', 25,context=context)
			smtpObj.sendmail(sender_email, receiver_email, message)

			#with smtplib.SMTP("", 25) as server:
			    #server.login(sender_email, password)
			 #   server.sendmail(
			  #      sender_email, receiver_email, message.as_string()
			   # )

			logging.info("Successfully sent email")

	except SMTPException:
		raise
	   	print "Error: unable to send email"



if __name__=='__main__':  #Cuerpo Principal
	
	subject = "Prueba Subject"
	receiver_email = "chhernandezs@kionetworks.com"
	
	# Create the plain-text and HTML version of your message
	body = """\
	Hi,
	How are you?
	Real Python has many great tutorials:
	www.realpython.com"""
	html = """\
	<html>
	  <body>
	    <p>Hi,<br>
	       How are you?<br>
	       <a href="http://www.realpython.com">Real Python</a> 
	       has many great tutorials.
	    </p>
	  </body>
	</html>
	"""

	smtp = Smtp()
	smtp.send(subject, receiver_email, body )