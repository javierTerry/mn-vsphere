#/usr/bin/env  python     #Linea de inicializacion
#"Modulo de ejemplo"       #Documentacion del script
# https://vdc-download.vmware.com/vmwb-repository/dcr-public/6b586ed2-655c-49d9-9029-bc416323cb22/fa0b429a-a695-4c11-b7d2-2cbc284049dc/doc/index.html
# https://vdc-download.vmware.com/vmwb-repository/dcr-public/6b586ed2-655c-49d9-9029-bc416323cb22/fa0b429a-a695-4c11-b7d2-2cbc284049dc/doc/vim.VirtualMachine.html

import sys
import os                 #Modulos que se importan
import ssl
import atexit
from datetime import datetime,timedelta
import time
from pytz import timezone

from pyVim import connect
from src import argumento
from src.Snapshot import Snapshot
from src.VirtualMachine import VirtualMachine 
import humanize
import json
import logging
 
# add filemode="w" to overwrite
logging.basicConfig(filename="logs/TimeSyncWithHostImpl.log", level=logging.INFO)


debug= True               #Declaracion de variables Globales
cdmx = timezone('America/Mexico_City')
# Se agregan Gb para solventar los snaps de Veeam
suporteVeeam = 50

class TimeSyncWithHostImpl:

    def csv_datastore( self, datastore ):
        for ds in datastore:
            #print (ds.summary) #dir(vm.datastore)
            #print self.sizeof_fmt(ds.summary.capacity)
            #print "--------------------------------------"
            #print ds.summary
            self.ds_name= ds.summary.name 
            
            self.ds_capacidad = self.sizeof_fmt(ds.summary.capacity)
            self.ds_espacioLibre = self.sizeof_fmt(ds.summary.freeSpace)

    def main(self):
        try:    
            logging.info("Iniciando Conexion")
            self.args = argumento.credencialesHipervisor()
            instanceEsxi = connect.SmartConnect(host=self.args.host,
                                                user=self.args.user,
                                                pwd=self.args.password,
                                                port=int(self.args.port)
                                                ,sslContext=self.args.disable_ssl_verification
                                                )
            atexit.register(connect.Disconnect, instanceEsxi)
            
            vms = VirtualMachine(instanceEsxi)

            csv_headers = "UUID, VM, SYNC WITH HOST"
            print csv_headers

            countSyncTrue = 0
            countSyncFalse = 0
            totalVMs = len(vms.all())

            for vm in vms.all():
                """
                    Ciclo para listar las VM
                """
                uuid = vm.summary.config.instanceUuid
                vmName = vm.summary.config.name
                flagStorageVeeam = True

                logging.info( "VM {} with UUID {}".format(vm.summary.config.name, uuid))

                if not ( bool(uuid)):
                    logging.debug("Sin uuid, revisar REVISAR")
                    continue
                vm = vms.findVM( uuid )
                    	
                if ( vm ):

                	logging.info((vm.config.tools.syncTimeWithHost))
                	if ( vm.config.tools.syncTimeWithHost is True ) :
                		logging.info("Sync Time With Host Activado")
                		SYNCWITHHOST = "ACTIVO"
                		countSyncTrue = countSyncTrue + 1;
                	else :
                		logging.info("Sync Time With Host Desactivado")
                		SYNCWITHHOST = "INACTIVO"
                		countSyncFalse = countSyncFalse + 1

                	print "{},{},{}".format(uuid, vmName, SYNCWITHHOST)

                
            print "Total de VMs {}  VMs con Sync Activo {} VMs con Sync Inactivo {}".format(totalVMs, countSyncTrue, countSyncFalse)
        except:
            raise
            logging.error("An error has happened!")



if __name__=='__main__':
	timeStart = datetime.now()
	vm = TimeSyncWithHostImpl()
	vm.main()


	receivers = ['chernandez.hernandez@masnegocio.com']

	timeEnd = datetime.now() 
	descripcionTiempo = " Tiempo de inicio {}, tiempo de termino {}".format(timeStart, timeEnd )
	timeDelta = timeEnd - timeStart
	logging.info(descripcionTiempo)

	descripcionTdelta = "EL proceso tardo {} dias {} horas {} minutos {} segundos ".format(
	    timeDelta.days, timeDelta.seconds / 3600, timeDelta.seconds / 60, timeDelta.seconds % 60 )
	logging.info(descripcionTdelta)