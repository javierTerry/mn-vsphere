#/usr/bin/env  python     #Linea de inicializacion
#"Modulo de ejemplo"       #Documentacion del script
# https://vdc-download.vmware.com/vmwb-repository/dcr-public/6b586ed2-655c-49d9-9029-bc416323cb22/fa0b429a-a695-4c11-b7d2-2cbc284049dc/doc/index.html

import sys
import os                 #Modulos que se importan
import ssl

from datetime import datetime,timedelta
import time
from pytz import timezone

#from pyVim import connect
from src import argumento
from src.Connection import Connection
from src.Snapshot import Snapshot
from src.VirtualMachine import VirtualMachine 
from src.Smtp import Smtp 
import humanize
import json
import logging
 

strFileLog = "logs/{}-{}".format(datetime.now().strftime("%Y%m%d"), __file__.replace(".py",".log") )
with open('src/config/config.json') as json_data_file:
    cfg = json.load(json_data_file)



# add filemode="w" to overwrite
logging.basicConfig(filename=strFileLog, level=logging.INFO)

debug= True               #Decla""racion de variables Globales
cdmx = timezone('America/Mexico_City')
# Se agregan Gb para solventar los snaps de Veeam
suporteVeeam = 10

class VirtualMachineImpl:

    def csv_datastore( self, datastore ):
        for ds in datastore:
            #print (ds.summary) #dir(vm.datastore)
            #print self.sizeof_fmt(ds.summary.capacity)
            #print "--------------------------------------"
            #print ds.summary
            self.ds_name= ds.summary.name 
            
            self.ds_capacidad = self.sizeof_fmt(ds.summary.capacity)
            self.ds_espacioLibre = self.sizeof_fmt(ds.summary.freeSpace)
            #print ds_detalle 

        #exit()

    def sizeof_fmt(self, num):
        """
        Returns the human readable version of a file size

        :param num:
        :return:
        """
        #print "antes de dividir {} ".format(num) 
        num = num / 1024 /1024 / 1024
        #print "Despues de dividir {}".format(num) 

        for item in ['bytes', 'KB', 'MB', 'GB']:
            #print "en el for"
            #print num

            if num < 1024.0:
                return "%3.0f" % (num)
            #num /= 1024.0
        return "%3.0f" % (num)



    def sw_case(self, item, sizes):
        case = {
            'KB' : lambda x: x
            ,'MB' : lambda x: x * 1024
            ,'GB' : lambda x: x * 1
            
            }
        return case[item](sizes)


    def main(self):
        try:
            self.countVMs = 0
            logging.info("Iniciando Conexion")
            self.args = argumento.credencialesHipervisor(cfg)
            instanceVCSA = Connection.start( self.args )

            vms = VirtualMachine(instanceVCSA)
            logging.info("Total de VMs {} ".format(len(vms.all())))

            csv_headers = "CLUSTER,HOST, NOMBRE,IPS, RAM MB, vCPUS,ESTATUS, STORAGE APR GB,DS_NAME, DS_CAPACIDAD, DS_ESPACIO LIBRE, RESIZE, RESIZE ESP, ETIQUETA-VM, SISTEMA OP." 
            print csv_headers
            for vm in vms.all():
                """
                    Ciclo para listar las VM
                """
                uuid = vm.summary.config.instanceUuid
                flagStorageVeeam = True
                logging.info( "VM {} with UUID {}".format(vm.summary.config.name, uuid))

                if not ( bool(uuid)):
                    logging.debug("Sin uuid, revisar REVISAR")
                    continue
                
                vm = vms.findVM( uuid )
                    
                if ( vm ):
                    try:
                        i = 0

                        self.csv_datastore( vm.datastore )

                        for devices in vm.config.hardware.device:
                            if 'disk' in devices.deviceInfo.label:
                                i +=  int(devices.deviceInfo.summary.replace(",","").replace("KB",""))
                            storage = (i / 1024) / 1024

                        capabilityHW = vm.config.hardware
                        summary = vm.summary.vm
                        guest = vm.guest 
                        estatusPower = vm.summary.runtime.powerState
                        ips = ""
                        for net  in guest.net:
                            #print (net)
                            for ip in net.ipAddress:
                                #print ip.find(":")
                                if ( ip.find(":") > 0 ):
                                    continue
                                #print ip
                                ips = "{} {} {} ".format(ips,net.network , ip)
                            #print ips

                        datastores = vm.datastore
                        storageTotal = (storage + suporteVeeam + (capabilityHW.memoryMB / 1024) )
                        
                        flagStorageVeeam = int(self.ds_capacidad) < storageTotal
                        resizeByVeeam =  storageTotal - int(self.ds_capacidad)

                        print "{},{},{},{}, {}, {}, {}, {} , {}, {}, {}, {}, {}, {},{}"   \
                            .format(vm.runtime.host.parent.name, vm.runtime.host.name, summary.config.name, ips, capabilityHW.memoryMB,capabilityHW.numCPU,estatusPower, storage, self.ds_name, self.ds_capacidad \
                                , self.ds_espacioLibre, flagStorageVeeam,resizeByVeeam, vm ,guest.guestFullName)
                        logging.info( "listar snaps")
                        self.countVMs += 1   
                    except:
                        raise
                        logging.info( "Error al listar VM")
                #print "---------------------------------------"

            Connection.stop(instanceVCSA)
            logging.info("Fin actividad")   
        except:
            Connection.stop(instanceVCSA)
            raise
            logging.error("An error has happened!")

if __name__=='__main__':  #Cuerpo Principal
    timeStart = datetime.now()

    vm = VirtualMachineImpl()
    vm.main()
        
    timeEnd = datetime.now() 
    descripcionTiempo = " Tiempo de inicio {}, tiempo de termino {}".format(timeStart, timeEnd )
    timeDelta = timeEnd - timeStart
    logging.info(descripcionTiempo)

    descripcionTdelta = "EL proceso tardo {} dias {} horas {} minutos {} segundos ".format(
        timeDelta.days, timeDelta.seconds / 3600, timeDelta.seconds / 60, timeDelta.seconds % 60 )
    logging.info(descripcionTdelta)


    subject = "Inventario - {} - {}".format(vm.args.vsphere,"Temporal")
    msj =  "Numero Total de VMs {} \n {}".format(vm.countVMs,descripcionTdelta)
    print cfg['NOTIFICATION']['RECEIVERS']
    print ""
    smpt = Smtp()
    smpt.send(subject, cfg['NOTIFICATION']['RECEIVERS'], msj)

    #logging.removeHandler(fh)
   