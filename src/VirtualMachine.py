from pyVmomi import vim
import argumento
import ssl
import atexit
from pyVim import connect

#import com.vmware.cis.tagging_client
#from com.vmware.cis.tagging_client import CategoryModel


class VirtualMachine:

	def __init__(self, instanceEsxi ):
		self.instanceEsxi = instanceEsxi
		self.content = self.instanceEsxi.RetrieveContent()
		self.container = self.content.rootFolder  # starting point to look into
		self.viewType = [vim.VirtualMachine]  # object types to look for
		self.recursive = True  # whether we should look into it recursively
        

	def all(self):
		containerView = self.content.viewManager.CreateContainerView(
            self.container, self.viewType, self.recursive)
		children = containerView.view
		return children

	def findVM(self,criteria):
		try:
			if ( len(criteria) is not 36):
				raise ValueError('Represents a hidden bug, do not catch this')

			search_index = self.instanceEsxi.content.searchIndex
			self.vm = search_index.FindByUuid(None, criteria, True, True)
			
			if self.vm is None:
				print ("Unable to locate VirtualMachine.")
				print("Could not find virtual machine '{0}'".format(criteria))
				return False				

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

			return vm
		except ValueError as err:
			print(err.args)
			return False
		except:
			print "print Error no reconocido"
			return False
			#raise


if __name__=='__main__':  #Cuerpo Principal
	self.args = argumento.credencialesHipervisor()
        instanceEsxi = connect.SmartConnect(host=self.args.host,
                                            user=self.args.user,
                                            pwd=self.args.password,
                                            port=int(self.args.port)
                                            ,sslContext=self.args.disable_ssl_verification
                                            )
        atexit.register(connect.Disconnect, instanceEsxi)

    
        
        vms = VirtualMachine(instanceEsxi)


        logging.info("Total de VMs {} ".format(len(vms.all())))
        csv_headers = "CLUSTER, IPS,NOMBRE, RAM MB, vCPUS, STORAGE APR GB,DS_NAME, DS_CAPACIDAD, DS_ESPACIO LIBRE, RESIZE, RESIZE ESP,ESTATUS, ETIQUETA-VM, SISTEMA OP." 
        print csv_headers
        #for vm in vms.all():