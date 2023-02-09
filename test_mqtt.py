#!/usr/bin/python3
# -- coding: utf-8 --
'''Implementa un cliente MQTT para pruebas utilizando un archivo de configuración dado.

Falta la descripión completa.
'''

__author__ = "Wilmar Arcila Castaño"
__copyright__ = "Aethyr Systems"
__credits__ = ["Wilmar Arcila Castaño", "Ethyr"]
__license__ = "GPL"
__version__ = "0.0.2"
__maintainer__ = "Wilmar Arcila Castaño"
__email__ = "wilmararcilac@gmail.com"
__status__ = "Prototipo"
__date__ = "30/05/2022"

# from ~/IoT/iot_python/cores_temp import read_temp,locate_sensors
import sys
sys.path.insert(1, '~/IoT/iot_python')

import argparse
import mqtt_client
from cores_temp import read_temp,locate_sensors
from signal import signal as setSignalHandler
from signal import SIGINT
from time import sleep, time


def readTemp(sensors):
    t=read_temp(sensors)
    return (t[0][0],t[0][2],t[0][3])

def signal_handler(sig, frame):
    global run
    print('** You pressed Ctrl+C **')
    run=False

def getArgs():
    parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter,
                        description=__doc__.partition('\n')[0],
                        epilog=f'{__maintainer__} - {__copyright__.upper()}')
    parser.add_argument('-f, --file', dest='file', default='./mqttconfig',
                        help='Archivo de configuración para la conexión MQTT.')
    parser.add_argument('--version', action='version',
                        version=f'%(prog)s  v{__version__}, {__date__}\npor {__author__}')

    args = parser.parse_args()  
    return args

if __name__ == "__main__":
    args = getArgs()

    setSignalHandler(SIGINT, signal_handler)

    cliente=mqtt_client.Cliente_MQTT(configfile='./Ubidots/mqttconfig')
    cliente.connect()
    run=True
    sensors=locate_sensors()
    result = cliente.publish('pc_toshiba', {"position": {"lat": "6.5423", "lng": "-70.5783"}})
    while run:
        sleep(5)
        sensor,temperature,ts=readTemp(sensors)
        msg={"temp": {"value":temperature,"timestamp":(ts*1000), "context":{"sensor":sensor}}}
        # print('pc_toshiba:', msg)
        result = cliente.publish('pc_toshiba', msg)
    cliente.disconnect()



'''
id_dicontroller
01 -> bombillas
02 ->
03 -> TV
04 -> Reproductor (atrás, stop, adelante)
05 -> Aire acondicionado (menú, anterior, siguiente)
    'type_comand' == 'controller'
    comando="_TECLA_001"
    comando="_TECLA_002"
    comando="_TECLA_011"
    comando="_TECLA_012"
    comando="_TECLA_013"
    comando="_TECLA_014"
    comando="_TECLA_015"
    comando="_TECLA_016"
    comando="_TECLA_017"
    comando="_TECLA_018"
    comando="_TECLA_019"
    comando="_TECLA_026"
    comando="_TECLA_020"
    comando="_TECLA_029"
    comando="_TECLA_027"
    comando="_TECLA_028"
    comando="_TECLA_030"
    comando="_TECLA_031"
    comando="_TECLA_025"
    comando="_TECLA_032"
    comando="_TECLA_033"
    comando="_TECLA_021"
    comando="_TECLA_033"
    comando="_TECLA_024"
    comando="_TECLA_025"
    comando="_TECLA_022"
    comando="_TECLA_031"
    comando="_TECLA_023"
    comando="_TECLA_034"
    comando="_TECLA_031"
    comando="_TECLA_037"
    comando="_TECLA_030"
    comando="_TECLA_034"
    comando="_TECLA_032"
    comando="_TECLA_033"
    comando="_TECLA_036"
    comando="_TECLA_035"
    comando="_TECLA_021"
    comando="_TECLA_022"
    comando="_TECLA_023"
    comando="_TECLA_024"
    comando="02_TECLA_086"

'''