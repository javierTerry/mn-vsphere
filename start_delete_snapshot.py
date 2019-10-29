#/usr/bin/env  python     #Linea de inicializacion
# Alica       
# 

import sys
import os                 #Modulos que se importan
import ssl
import atexit
import time
import logging
from datetime import datetime,timedelta
from pytz import timezone
from pyVim import connect
import json

from src import argumento
from src.Snapshot import Snapshot
from src.VirtualMachine import VirtualMachine
from src.Smtp import Smtp 
 
strFileLog = "logs/{}-{}".format(datetime.now().strftime("%Y%m%d"), __file__.replace(".py",".log") )
with open('src/config/config.json') as json_data_file:
    cfg = json.load(json_data_file)



# add filemode="w" to overwrite
logging.basicConfig(filename=strFileLog, level=logging.INFO)

debug= True               #Decla""racion de variables Globales
cdmx = timezone('America/Mexico_City')

def obtenerRetencion(descripcion):
    retencion = False
    tmp = descripcion.split()
    try:
        log.debug("Iniciando obtener retencion")
        #log.info("Count descripcion {}".format( len(tmp)))
        dias = int( tmp[0] )
        if dias > 0 :
            retencion = True

    except:
        log.debug("Valor '{}' no aceptado para la retencion".format(descripcion))
        retencion = True

    return retencion

def veeamSnapOld(name):
    deleted = False
    try:
        log.debug("Iniciando obtener retencion")
        if name.strip() == 'VEEAM BACKUP TEMPORARY SNAPSHOT'  :
            log.info( "borrar snap de veeam" ) 
            deleted = True
        else :
             log.info(  "no es veeam" )

    except:
        log.debug("Iniciando obtener retencion")


    return deleted


def exceptionVM (nameVM):
    noBorrarSnapLst = []
    blnException = len( filter(lambda x: nameVM in x, noBorrarSnapLst))
    return bool(blnException);

def main():


    try:    
        log.info("Iniciando Conexion")
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

        strTotalVM = "Total de VMs {} ".format(len(vms.all())) 
        log.info(strTotalVM) 
        evidencia = ""
        msj = "Analisis de eliminacion de snaps o retencion para Alica {}".format(strTotalVM) 
        count = 0

        for vm in vms.all():

            #print vm.summary.config
            #exit()
            uuid = vm.summary.config.instanceUuid
            nameVM = vm.summary.config.name
            nameVMstr = "VM NAME -> {} --------------------".format(nameVM)
            uuidVM = "UUID -> {}".format(uuid)
            log.info( nameVM )
            log.info( uuidVM )
            
            if ( exceptionVM( nameVM ) ):
                log.info( "VM en excepcion" ) 
                msj = "{} \n {} \n {}".format(msj, nameVMstr, "En lista de excepciones")
                continue

            vm = vms.findVM( uuid )
            if ( vm ):
                try:
                    sn = Snapshot( vm )
                        
                    log.info( "listar snaps ")
                    snapshots = sn.list_snapshots_recursively(sn.vm.snapshot.rootSnapshotList)
                    
                    log.info( "total de snaps {}".format(len(snapshots)))

                    """
                        Ciclo para borrar los nsaps con mas de 7 dias de creacion
                    """
                    msj = " {} \n {} ".format(msj,nameVMstr )
                    for snapshot in snapshots:
                        
                        mensajeNameSnap = "Snapshot Name {} - {}".format(snapshot.name, snapshot.description)
                        log.info(mensajeNameSnap)
                        snapCreateTimeStr = snapshot.createTime.astimezone(cdmx).strftime("%Y-%m-%d %H:%M")
                        snapCreateTime = time.strptime(snapCreateTimeStr, "%Y-%m-%d %H:%M")

                        if ( veeamSnapOld(snapshot.name) ): 
                            #print "borrando"
                            
                            veeamDaysAgo = datetime.now() - timedelta(days=2)
                            #print veeamDaysAgo
                            veeamDaysAgoStr = veeamDaysAgo.strftime("%Y-%m-%d %H:%M")
                            veeamDaysAgo = time.strptime (sevenDaysAgoStr, "%Y-%m-%d %H:%M")

                            

                            msj = " {}  \n {}  ".format(msj, "Test")
                            log.info( "borrando snap de veeam" )
                            count = count + 1
                            log.info("Borrar final de veeam" ) 
                            #sn.delete(snapshot)

                        else : 
                            #print "borrar por retencion"
                            sevenDaysAgo = datetime.now() - timedelta(days=6)
                            sevenDaysAgoStr = sevenDaysAgo.strftime("%Y-%m-%d %H:%M")
                            sevenDaysAgo = time.strptime (sevenDaysAgoStr, "%Y-%m-%d %H:%M")

                            mensajeValidaRetencion = "Valida tiempo de retencion {} < {} {}".format(snapCreateTimeStr, sevenDaysAgoStr, snapCreateTime < sevenDaysAgo)
                            #print snapshot.description
                            isOnDemand = True #obtenerRetencion(snapshot.description)     
                            log.info( mensajeValidaRetencion )
                            if not (isOnDemand):
                                msj = " {}  \n No se borraron Snap OnDemand {} ".format(msj, mensajeNameSnap)

                            if ( snapCreateTime < sevenDaysAgo   and isOnDemand):
                                evidencia = mensajeNameSnap + mensajeValidaRetencion
                                msj = " {}  \n {}  ".format(msj, evidencia)
                                log.info( "borrando" )
                                count = count + 1
                                sn.delete(snapshot)

                except Exception as e:
                    s = str(e)
                    log.info( e )
                    #print e
                    log.info( "No existen snaps para borrar")
                    
            

        log.info(msj)
        msj = "{} \n Total de snaps eliminados {}".format(msj, count)
        receivers = ['virtualizacion@']

        msj = "Subject: Depuracion  \n\n {} ".format(msj)
        smpt = Smtp(receivers, msj)
        smpt.send()

        log.info("Fin actividad")   
    except:
        raise
        log.error("An error has happened!")

    

if __name__=='__main__':  #Cuerpo Principal
    timeStart = datetime.now()
    main()
    timeEnd = datetime.now() 
    descripcionTiempo = " Tiempo de inicio {}, tiempo de termino {}".format(timeStart, timeEnd )
    timeDelta = timeEnd - timeStart
    log.info(descripcionTiempo)
    descripcionTdelta = "EL proceso tardo {} dias {} horas {} minutos {} segundos {} microsegundos".format(
        timeDelta.days, timeDelta.seconds / 3600, timeDelta.seconds / 60, timeDelta.seconds % 60 ,  timeDelta.microseconds)
    log.info(descripcionTdelta)
    log.removeHandler(fh)
    del log, fh