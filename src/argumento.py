import argparse
import ssl
from ConfigParser import SafeConfigParser



def get():
    """
   Supports the command-line arguments listed below.
   """
    parser = argparse.ArgumentParser(
        description='Process args for retrieving all the Virtual Machines')
    
    parser.add_argument('-s', '--host', required=False, action='store',
                        help='Remote host to connect to')
    
    parser.add_argument('-o', '--port', required=False, type=int, default=443, action='store',
                        help='Port to connect on')
    
    parser.add_argument('-u', '--user', required=False, action='store',
                        help='User name to use when connecting to host')

    parser.add_argument('-p', '--password', required=False, action='store',
                        help='Password to use when connecting to host')
    
    parser.add_argument('-j', '--json', default=False, action='store_true',
                        help='Output to JSON')
    
    parser.add_argument('-S', '--disable_ssl_verification', required=False, action='store_true',
                        help='Disable ssl host certificate verification')


    subparsers = parser.add_subparsers(help='Vsphere que se usara',   dest='vsphere')
    
    # A list command
    list_parser = subparsers.add_parser('SF20975',help='vSphere Santa Fe')
    list_parser = subparsers.add_parser('ALICA', help='vSphere ALICA')
    list_parser = subparsers.add_parser('ALSEA', help='vSphere ALSEA')
    list_parser = subparsers.add_parser('MABESA', help='vSphere MABESA')
    list_parser = subparsers.add_parser('QRO', help='vSphere Queretaro')
    list_parser = subparsers.add_parser('REDIT', help='vSphere REDIT')
    list_parser = subparsers.add_parser('INTERLOMAS', help='vSphere Interlomas')
    list_parser = subparsers.add_parser('TULTI', help='vSphere Tultitlan')
    list_parser = subparsers.add_parser('PANAMA', help='vSphere PANAMA')
    list_parser = subparsers.add_parser('MEDICASUR', help='vSphere MEDICASUR')
    list_parser = subparsers.add_parser('DRPCAME', help='vSphere DRPCAME')
    list_parser = subparsers.add_parser('DRPSIVALE', help='vSphere DRPSIVALE')
    list_parser = subparsers.add_parser('VCLOUD', help='vSphere DRPSIVALE')
    list_parser = subparsers.add_parser('COMEX', help='vSphere DRPSIVALE')

    
    return parser.parse_args()


def credencialesHipervisor(CFG):

    args = get()

    VCSA = CFG['VCSA'][args.vsphere]
    args.user       = VCSA['CRED']['USER'] 
    args.password   = VCSA['CRED']['PWD']
    args.host       = VCSA['IP']

    sslContext = ssl.SSLContext(ssl.PROTOCOL_SSLv23)
    sslContext.verify_mode = ssl.CERT_NONE
    args.disable_ssl_verification = sslContext

    return args

if __name__=='__main__':

    args = credencialesHipervisor()
    args.user = ''
    print args
    print (args.vsphere)
