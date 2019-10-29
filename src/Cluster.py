from pyVmomi import vim
import argumento
import ssl
import atexit
from pyVim import connect
import humanize
from datetime import datetime,timedelta


class ClusterImp:

	def __init__(self, instanceEsxi ):
		self.instanceEsxi = instanceEsxi
		self.content = self.instanceEsxi.RetrieveContent()
		self.container = self.content.rootFolder  # starting point to look into
		self.viewType = [vim.ClusterComputeResource]  # object types to look for
		self.recursive = True  # whether we should look into it recursively
		containerView = self.content.viewManager.CreateContainerView(self.container, self.viewType, self.recursive)
		self.clusters = containerView.view


	def findVM(self,criteria):
		try:
			search_index = self.instanceEsxi.content.searchIndex
			self.vm = search_index.FindByUuid(None, criteria, True, True)
			if self.vm is None:
				print ("Unable to locate VirtualMachine.")
				print("Could not find virtual machine '{0}'".format(criteria))
				return False				

			#print("Found Virtual Machine")
			vm = self.vm
			details = {'name': vm.summary.config.name,
			           'instance UUID': vm.summary.config.instanceUuid,
			           'bios UUID': vm.summary.config.uuid,
			           'path to VM': vm.summary.config.vmPathName,
			           'guest OS id': vm.summary.config.guestId,
			           'guest OS name': vm.summary.config.guestFullName,
			           'host name': vm.runtime.host.name,
			           'last booted timestamp': vm.runtime.bootTime,
			           }
			#print details

			return vm
		except:
			raise

	def list_all(self):


		#print self.clusters
		#exit()
		memoryByHosts = 0
		memoryUsedByhosts = 0
		MBFACTOR = float(1 << 20)
		print "{},{},{} ".format("CLUSTER NAME","NODO","VM NAME", "DS NAME")
		for cluster  in self.clusters:
			self.cluster = cluster
			#print cluster.summary
			#print (cluster.host)
			for nodo in cluster.host:
				self.nodo = nodo
				#print dir(nodo.vm)
				for vm in nodo.vm:
					self.vm = vm
					for ds in vm.datastore:
						self.ds = ds
					
					print "{},{},{}, {}".format(self.cluster.name, self.nodo.name, self.vm.name, self.ds.name)




if __name__=='__main__':  #Cuerpo Principal
	timeStart = datetime.now()
	args = argumento.get()
	sslContext = ssl.SSLContext(ssl.PROTOCOL_SSLv23)
	sslContext.verify_mode = ssl.CERT_NONE

	instanceEsxi = connect.SmartConnect(host=args.host,
                                        user=args.user,
                                        pwd=args.password,
                                        port=int(args.port)
                                        ,sslContext=sslContext)
	atexit.register(connect.Disconnect, instanceEsxi)

	cluster = ClusterImp(instanceEsxi)
	cluster.list_all()
    
    
	#receivers = ['virtualizacion@masnegocio.com']

	timeEnd = datetime.now() 
	descripcionTiempo = " Tiempo de inicio {}, tiempo de termino {}".format(timeStart, timeEnd )
	timeDelta = timeEnd - timeStart
	logging.info(descripcionTiempo)

	descripcionTdelta = "EL proceso tardo {} dias {} horas {} minutos {} segundos {} microsegundos".format(
	    timeDelta.days, timeDelta.seconds / 3600, timeDelta.seconds / 60, timeDelta.seconds % 60 ,  timeDelta.microseconds)
	logging.info(descripcionTdelta)