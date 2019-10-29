"""
Este Archivo tiene la forma basica de conexion a un VCSA o ESXI 

"""

from pyVim import connect
import atexit

class Connection:
    """
    Connection Es la clase que encapsula los metodos basicos para coenctar
    o desconectar un sesion al VCSA.
    """
    def __init__(self):
        """
        Construct a new 'Foo' object.

        :param name: The name of foo
        :param age: The ageof foo
        :return: la conexion al VCSA
        """
        print "test"
        #self.name = name
        #self.age = age

    @staticmethod
    #@atexit.register
    def start(args):
    	
    	connectionVCSA = connect.SmartConnect(host=args.host,
                                                user=args.user,
                                                pwd=args.password,
                                                port=int(args.port)
                                                ,sslContext=args.disable_ssl_verification
                                                )
        return connectionVCSA

    @staticmethod
    def stop(connectionVCSA):
    	#atexit.unregister(start)
    	connect.Disconnect(connectionVCSA)


if __name__ == '__main__':
    f = Foo('John Doe', 42)
    bar("hello world")