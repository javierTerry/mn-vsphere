#/usr/bin/env  python
#Christian Hernandez <christian.hernandez@masnegocio>
#201806014
#https://vdc-download.vmware.com/vmwb-repository/dcr-public/6b586ed2-655c-49d9-9029-bc416323cb22/fa0b429a-a695-4c11-b7d2-2cbc284049dc/doc/left-pane.html

import argumento


from pyVim import connect
import atexit
import sys
from pyVmomi import vim
class Alarma():

	def __init__(self, instanceEsxi ):
		self.instanceEsxi = instanceEsxi
		self.content = self.instanceEsxi.RetrieveContent()
		self.container = self.content.rootFolder  # starting point to look into
		self.viewType = [vim.Datacenter]  # object types to look for
		self.recursive = True  # whether we should look into it recursively
		containerView = self.content.viewManager.CreateContainerView(self.container, self.viewType, self.recursive)
		self.alarms = containerView.view
        


if __name__=='__main__':  #Cuerpo Principal
	args = argumento.credencialesHipervisor()
	#sslContext = ssl.SSLContext(ssl.PROTOCOL_SSLv23)
	#sslContext.verify_mode = ssl.CERT_NONE
	print args
	instanceEsxi = connect.SmartConnect(host=args.host,
                                        user=args.user,
                                        pwd=args.password,
                                        port=int(args.port)
                                        ,sslContext=args.disable_ssl_verification
                                        )
	atexit.register(connect.Disconnect, instanceEsxi)


	print instanceEsxi

	alertas = Alarma(instanceEsxi)#
	#alarma.alarms
	print dir(alertas.alarms)
	for alarma in alertas.alarms:
		print dir(alarma)
		print alarma.name
		print len(alarma.triggeredAlarmState)
		print dir(alarma.parent)
		print alarma.parent.name
		print alarma.parent.triggeredAlarmState


	sys.exit()	
