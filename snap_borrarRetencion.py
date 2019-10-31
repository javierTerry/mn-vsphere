#/usr/bin/env  python     #Linea de inicializacion
#"Modulo de ejemplo"       #Documentacion del script

import sys
import os                 #Modulos que se importan
import ssl
import atexit
from datetime import datetime,timedelta
import time
from pytz import timezone
import json
import logging

from pyVim import connect
from  src import argumento
from src.Snapshot import Snapshot
from src.VirtualMachine import VirtualMachine
from src.Smtp import Smtp
from src.Connection import Connection


strFileLog = "logs/{}-{}".format(datetime.now().strftime("%Y%m%d"), __file__.replace(".py",".log") )
with open('src/config/config.json') as json_data_file:
    cfg = json.load(json_data_file)


# add filemode="w" to overwrite
logging.basicConfig(filename=strFileLog, level=logging.INFO)

debug= True               #Decla""racion de variables Globales
cdmx = timezone('America/Mexico_City')

class RetencionEliminar:
    HORAS_RETENCION = 24

    def obtenerRetencion(self,descripcion):
        retencion = 0
        try:
            logging.info("Iniciando obtener retencion")
            tmp = descripcion.split()
            retencion = self.HORAS_RETENCION * int(tmp[0])
        except:
            logging.info("Valor '{}' no aceptado para la retencion".format(tmp[0]))

        return retencion

    def verificaBorrarSnap(self,snapshot):
        borrarSnap = False 
        retencionHora = self.obtenerRetencion(snapshot.description)
        snapCreateTimeStr = snapshot.createTime.astimezone(cdmx).strftime("%Y-%m-%d %H:%M:%S")
        snapCreateTime = datetime.strptime(snapCreateTimeStr, "%Y-%m-%d %H:%M:%S")
        
        actual = datetime.now()
        actualStr = actual.strftime("%Y-%m-%d %H:%M:%S")
        boolTiempoRetencion = datetime.now() >  snapCreateTime + timedelta(hours=retencionHora )
        
        diasTranscurridos = ( actual - snapCreateTime )
        logging.info("Tiempo transcurridos del snap {} horas".format(diasTranscurridos))
        strVerificaBorrar = "Fecha creacion snap {}, fecha actual {} Tiempo trascurridos {} horas, tiempo de retencion {} horas" \
                        .format(snapCreateTimeStr, actualStr,diasTranscurridos, retencionHora)
        logging.info( strVerificaBorrar )
        self.msj = "{} \n{}".format(self.msj, strVerificaBorrar)

        if ( retencionHora != 0 and  boolTiempoRetencion ):
            logging = True
            logging.info( "VerificaBorrarSnap return {}".format(borrarSnap) )

        return borrarSnap

    def veeamSnap(self,name, snapCreateTime):
        deleted = False
        try:
            logging.info("Iniciando obtener snap de Veeam")
            if name.strip() == 'VEEAM BACKUP TEMPORARY SNAPSHOT'  :
                logging.info( "borrar snap de veeam" )
                veeamDaysAgoDate = datetime.now()# - timedelta(days=2)
                veeamDaysAgoStr = veeamDaysAgoDate.strftime("%Y-%m-%d %H:%M")
                veeamDaysAgo = time.strptime(veeamDaysAgoStr, "%Y-%m-%d %H:%M")
                differenceDelta = veeamDaysAgoDate - snapCreateTime 
        
                if (differenceDelta.days > 2) :
                    self.msj = " {}  \n {}  ".format(self.msj, "Snap de Veeam con tiempo mayor a 48 horas")
                    logging.info( "Bandera borar snap de veeam" )
                    deleted = True
                else :
                    logging.info( "Si es un snap de Veeam pero no cumple retencion" ) 

            else :
                 logging.info(  "no es Snap de Veeam " )

        except:
            logging.debug("Error inesperado")
            raise


        return deleted


    def verificaSnap(self, snapshot):
        logging.info("Seccion VerificaSnap")

        retencion = self.obtenerRetencion(snapshot.description)

        snapCreateTimeStr = snapshot.createTime.astimezone(cdmx).strftime("%Y-%m-%d")
        snapCreateTime = datetime.strptime(snapCreateTimeStr, "%Y-%m-%d")
        borrarSnapVeeam = False
        if ( self.veeamSnap(snapshot.name, snapCreateTime) ): 
            logging.info( "Bandera borrar snap de veeam" )
            return True

        else :
            logging.info(  "Inicia validacion de snap por retencion" )
            return self.verificaBorrarSnap(snapshot)


    def main(self):
        try:    
            count = 0
            snapDescripcion = ""
            self.msj = "Listado de snaps a borrar"
            
            logging.info("Iniciando Conexion")
            self.args = argumento.credencialesHipervisor(cfg)
            
            instanceVCSA = Connection.start( self.args )
            
            vms = VirtualMachine(instanceVCSA)
            logging.info("Total de VMs {} ".format(len(vms.all()))) 
            for vm in vms.all():
                uuid = vm.summary.config.instanceUuid

                ip = vm.guest.ipAddress

                vmUuid = "VM {} con IP {}".format(vm.summary.config.name, ip)
                
                if not ( bool(uuid) ):
                    continue
                
                vm = vms.findVM(uuid)
                if ( vm ):
                    try:
                        sn = Snapshot( vm )
                        logging.info( "listar snaps")
                        snapshots = sn.list_snapshots_recursively(sn.vm.snapshot.rootSnapshotList)
                        logging.info( "total de snaps {}".format(len(snapshots)))

                        """
                            Ciclo para borrar los snaps con relacion a la retencion solicitada
                        """

                        if (len(snapshots) > 0 ) : 
                            logging.info( vmUuid )

                        self.msj = "{} \n {}".format(self.msj, vmUuid)
                        logging.info ("inicia ciclo de borrado de Snaps")
                        for snapshot in snapshots:      

                            if ( self.verificaSnap(snapshot) ) : 
                                snapDescripcion = "Snapshot Name {} , Descripcion {}".format(snapshot.name, snapshot.description)
                                logging.info( snapDescripcion )
                                
                                self.msj = "{} \n {} \n".format(self.msj, snapDescripcion)
                                logging.info( "borrando Snap " )
                                sn.delete(snapshot)
                    except Exception as error:
                        logging.debug( "No existen snaps para borrar")
                        logging.debug ( repr(error) )

             
            logging.info("Fin actividad")   
        except:
            raise
            logging.error("An error has happened!")

    

if __name__=='__main__':  #Cuerpo Principal
    
    timeStart = datetime.now()
    
    snap = RetencionEliminar()
    
    snap.main()
   

    timeEnd = datetime.now() 
    descripcionTiempo = " Tiempo de inicio {}, tiempo de termino {}".format(timeStart, timeEnd )
    timeDelta = timeEnd - timeStart
    logging.info(descripcionTiempo)
    descripcionTdelta = "EL proceso tardo {} dias {} horas {} minutos {} segundos".format(
        timeDelta.days, timeDelta.seconds / 3600, timeDelta.seconds / 60, timeDelta.seconds % 60 )
    logging.info(descripcionTdelta)
    
    msj = "{} \n{}".format(descripcionTdelta,snap.msj)

    subject = "Revision snap - {} - {}".format(snap.args.vsphere,snap.args.host)
    smpt = Smtp()
    smpt.send(subject, cfg['NOTIFICATION']['RECEIVERS'], msj)
    logging.info("fin del script") 
    sys.exit()

     