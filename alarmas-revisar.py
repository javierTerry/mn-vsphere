#/usr/bin/env  python

import sys
import os 
import ssl

# add filemode="w" to overwrite
logging.basicConfig(filename="start_vm_list.log", level=logging.INFO)


debug= True               #Declaracion de variables Globales
cdmx = timezone('America/Mexico_City')

if __name__=='__main__':  #Cuerpo Principal
    
    
    timeStart = datetime.now()
    snap = RetencionEliminar()
    snap.main()
