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
from  src import argumento
from src.Snapshot import Snapshot
from src.VirtualMachine import VirtualMachine 

import logging
 
# add filemode="w" to overwrite
logging.basicConfig(filename="sample.log", level=logging.INFO)
 
logging.debug("This is a debug message")
logging.info("Informational message")
logging.error("An error has happened!")


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
        for vm in vms.all():
            uuid = vm.summary.config.instanceUuid
            logging.info( "VM {} with UUID {}".format(vm.summary.config.name, uuid))
            vm = vms.findVM(uuid)
            if ( vm ):
                try:
                    sn = Snapshot( vm )
                    #sn.create()
                    logging.info( "listar snaps")
                    snapshots = sn.list_snapshots_recursively(sn.vm.snapshot.rootSnapshotList)
                    
                    logging.info( "total de snaps {}".format(len(snapshots)))

                    """
                        Ciclo para borrar los nsaps con mas de 7 dias de creacion
                    """
                    for snapshot in snapshots:
                        logging.info("Snapshot Name {}".format(snapshot.name))
                        
                        snapCreateTimeStr = snapshot.createTime.astimezone(cdmx).strftime("%Y-%m-%d %H:%M")
                        snapCreateTime = time.strptime(snapCreateTimeStr, "%Y-%m-%d %H:%M")
                        

                        sevenDaysAgo = datetime.now() - timedelta(days=6)
                        sevenDaysAgoStr = sevenDaysAgo.strftime("%Y-%m-%d %H:%M")
                        sevenDaysAgo = time.strptime (sevenDaysAgoStr, "%Y-%m-%d %H:%M")
                        logging.info( "{} < {} {}".format(snapCreateTimeStr, sevenDaysAgoStr, snapCreateTime < sevenDaysAgo))
                        if snapCreateTime < sevenDaysAgo:
                            logging.info( "borrando" )
                            sn.delete(snapshot)
                except:
                    logging.info( "No existen snaps para borrar")

                            
                
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