from pyVmomi import vim
import argumento
import ssl
import atexit
from pyVim import connect
import sys

class Datastore:

	def __init__(self, instanceEsxi ):
		self.instanceEsxi = instanceEsxi
		self.content = self.instanceEsxi.RetrieveContent()
		self.container = self.content.rootFolder  # starting point to look into
		self.viewType = [vim.Datastore]  # object types to look for
		self.recursive = True  # whether we should look into it recursively

	def all(self):
		containerView = self.	content.viewManager.CreateContainerView(
            self.container, self.viewType, self.recursive)
		children = containerView.view
		return children


if __name__=='__main__':  #Cuerpo Principal
		

		args = argumento.credencialesHipervisor()
		instanceVCSA = connect.SmartConnect(host=args.host,
                                            user=args.user,
                                            pwd=args.password,
                                            port=int(args.port)
                                            ,sslContext=args.disable_ssl_verification
                                            )
		atexit.register(connect.Disconnect, instanceVCSA)
		dataStores = Datastore(instanceVCSA)

		for ds in dataStores.all():
			print dir(ds)
			print ds.name
			print ds.vm
			


