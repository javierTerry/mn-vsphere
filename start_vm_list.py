#/usr/bin/env  python     #Linea de inicializacion
#"Modulo de ejemplo"       #Documentacion del script

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

import logging
 
# add filemode="w" to overwrite
logging.basicConfig(filename="start_vm_list.log", level=logging.INFO)


debug= True               #Declaracion de variables Globales
cdmx = timezone('America/Mexico_City')

def main():
    try:    
        logging.info("Iniciando Conexion")
        args = argumento.get()
        sslContext = ssl.SSLContext(ssl.PROTOCOL_SSLv23)
        sslContext.verify_mode = ssl.CERT_NONE
        instanceEsxi = connect.SmartConnect(host=args.host,
                                            user=args.user,
                                            pwd=args.password,
                                            port=int(args.port)
                                            ,sslContext=sslContext)
        atexit.register(connect.Disconnect, instanceEsxi)
        
        vms = VirtualMachine(instanceEsxi)

        logging.info("Total de VMs {} ".format(len(vms.all())))
        csv_headers = "Name, ip, RAM Mb, vCPUS, storage" 
        print csv_headers


       


        for vm in vms.all():
            """
                Ciclo para listar las VM
            """
            uuid = vm.summary.config.instanceUuid
            logging.info( "VM {} with UUID {}".format(vm.summary.config.name, uuid))
            vm = vms.findVM(uuid)

            if ( vm ):
                try:
                    i = 0
                    for devices in vm.config.hardware.device:
                        if 'disk' in devices.deviceInfo.label:
                            i +=  int(devices.deviceInfo.summary.replace(",","").replace("KB",""))
                        storage = (i / 1024) / 1024
                    capabilityHW = vm.config.hardware
                    summary = vm.summary
                    guest = vm.guest 
                    datastores = vm.datastore
                    print "{},{},{},{}, {}".format(summary.config.name, guest.ipAddress, capabilityHW.memoryMB,capabilityHW.numCPU, storage)
                    logging.info( "listar snaps")
                    

                   
                except:
                    raise
                    logging.info( "Error al listar VM")

           
        logging.info("Fin actividad")   
    except:
        raise
        logging.error("An error has happened!")

    

if __name__=='__main__':  #Cuerpo Principal
    timeStart = datetime.now()
    main()
    timeEnd = datetime.now() 
    descripcionTiempo = " Tiempo de inicio {}, tiempo de termino {}".format(timeStart, timeEnd )
    timeDelta = timeEnd - timeStart
    logging.info(descripcionTiempo)
    descripcionTdelta = "EL proceso tardo {} dias {} horas {} segundos {} microsegundos".format(timeDelta.days, timeDelta.seconds / 3600, timeDelta.seconds, timeDelta.microseconds)
    logging.info(descripcionTdelta)
    logging.shutdown()