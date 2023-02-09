#!/usr/bin/python3
# -- coding: utf-8 --
'''Implementa un cliente MQTT para pruebas utilizando un archivo de configuración dado.

La clase "Cliente_MQTT" es un wrapper para el cliente PAHO de Eclipse, que establece las acciones 
asociadas alos eventos del protocolo mqtt, crea un Logger y expone los métodos para publicar y consumir 
mensajes transportados por el protocolo mqtt.
'''

__author__ = "Wilmar Arcila Castaño"
__copyright__ = "Æthyr Systems"
__credits__ = ["Wilmar Arcila Castaño", "Æthyr"]
__license__ = "GPL"
__version__ = "0.0.2"
__maintainer__ = "Wilmar Arcila Castaño"
__email__ = "wilmararcilac@gmail.com"
__status__ = "Prototipo"
__date__ = "02/06/2022"

import paho.mqtt.client as mqtt
import json
import logging
import inspect
from os.path import abspath, dirname
from random import choices

class Cliente_MQTT:

    def __init__(self, configfile='./mqttconfig.json'):
        self.logger     = self.get_logger(configfile)
        self.subscriber = False
        self.publisher  = False
        self.onmessage_fp = None

        with open(configfile, 'r') as f:
            self.info = json.loads(f.read())
            self.logger.debug(f'** Archivo de configuración (JSON) cargado: {configfile}')
        
        if self.info.get('devices_subscribe') is not None and len(self.info.get('devices_subscribe'))>0:
            self.devices_subscribe=self.info.get('devices_subscribe')
            print('** Cliente MQTT marcado como subscriber **')
            self.subscriber=True
            self.logger.debug('** Cliente MQTT marcado como subscriber')
        if self.info.get('devices_publish') is not None and len(self.info.get('devices_publish'))>0:
            self.devices_publish=self.info.get('devices_publish')
            print('** Cliente MQTT marcado como publisher **')
            self.publisher=True
            self.logger.debug('** Cliente MQTT marcado como publisher')

        self.host  = self.info.get("host")
        self.port  = self.info.get("port")
        self.topic = self.info.get('topic')
        self.devices_names = tuple(x.get('name') for x in self.devices_publish)
        print(self.devices_names)

        self.headers = { "Host":f'{self.host}:{self.port}',
                "Upgrade": "websocket",
                "Connection": "Upgrade",
                "Origin": "app.aethyr",
                # "Sec-WebSocket-Key": "Vh7pM/Sr0Ji8tX3QIiWE0Q==",
                "Sec-WebSocket-Extensions": "permessage-deflate; client_max_window_bits",
                "Sec-Websocket-Version": "13",
                # "Sec-Websocket-Protocol": "mqttv3.1"
                # "Sec-Websocket-Protocol": "mqtt"
                }

        self.client_id  = self.getClientId()
        self.client     = mqtt.Client(client_id=self.client_id, clean_session=self.info.get('clean'), transport=self.info.get('transport'), protocol=mqtt.MQTTv311)
        self.client.ws_set_options  (path="/"+self.info.get("sufix") if self.info.get("sufix") is not None else None, headers=None)
        self.logger.debug(f'** Websocket connection-> user:{self.info.get("user")} pass:{self.info.get("pass")}')
        self.client.username_pw_set (self.info.get('user'), password=self.info.get('pass'))
        self.client.enable_logger   (self.logger)
        # self.client.user_data_set({'topic':topic,'devices':devices})

        self.client.on_message      = self.on_message
        self.client.on_connect      = self.on_connect
        self.client.on_disconnect   = self.on_disconnect
        self.client.on_publish      = self.on_publish
        self.client.on_subscribe    = self.on_subscribe

    def connect(self):
        print(f'** Enviando CONN_REQ a {self.host}:{self.port} **')
        self.logger.debug(f'** Enviando CONN_REQ a {self.host}:{self.port}')
        self.client.connect_async(self.host, int(self.port), int(self.info.get("keepalive")))
        self.client.loop_start()

    def disconnect(self):
        print(f'** Enviando DISCONNECT a {self.host} **')
        self.logger.debug(f'** Enviando DISCONNECT a {self.host}')
        self.client.disconnect()
        self.client.loop_stop()

    def publish(self, device:str, msg:dict):
        if device not in self.devices_names:
            self.logger.error(f'Intento de publicar en un dispositivo no contenido en el archivo de configuración -> <{device}>')
            return False
        url=self.topic+device
        print(f'>> Publishing to {url}: {msg}')
        self.client.publish(url, payload=json.dumps(msg),qos=0,retain=False)
        return True

    def set_OnMessage(self,fp):
        self.onmessage_fp=fp

    def get_logger(self, suffix):
        if suffix.startswith('.'):
            # Inspecciona el módulo para obtener el nombre del archivo
            __frame = inspect.stack()[2]

            __abs_path = abspath((__frame)[1])
            __logfile_path = dirname(__abs_path)+suffix[1:]
            __logfile_path = __logfile_path[:__logfile_path.rfind('/')]
        else:
            __logfile_path = suffix[:suffix.rfind('/')]

        __logger_name='MQTT_CLIENT'
        logger = logging.getLogger(__logger_name)
        logger.setLevel(logging.DEBUG)

        # create formatter
        formatter = logging.Formatter('(%(asctime)s) [%(levelname)s]:%(message)s')

        # create console handler and set level to info
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)

        # create file handler and set level to debug
        print(f'** Creando archivo de logs: {__logfile_path}/mqtt_client.log **')
        fh = logging.FileHandler(f'{__logfile_path}/mqtt_client.log')
        fh.setLevel(logging.DEBUG)

        # add formatter to ch and fh
        ch.setFormatter(formatter)
        fh.setFormatter(formatter)

        # add ch and fh to logger
        logger.addHandler(ch)
        logger.addHandler(fh)
        return logger

    def getClientId(self):
        l = [i for i in "abcdefgWXYZ1234567890"]
        return ''.join(choices(l,k=len(l)))    

    def on_connect(self, client, obj, flags, rc):
        print(f'**Received Connect: {rc}')
        print(f'obj: {obj}\nflags: {flags}')
        if self.subscriber:
            top=self.topic
            for i in self.devices_subscribe:
                _dir=top+i.get('name')
                if len(i.get('vars'))==0:
                    self.client.subscribe(_dir, qos=0)
                else:
                    for j in i.get('vars'):
                        self.client.subscribe(_dir+'/'+j, qos=0)

    def on_disconnect(self, client, obj, rc):
        print(f'**Disconnect: {rc}')
        print(f'obj: {obj}')

    def on_message(self, client, obj, msg):
        print(f'<< {msg.topic}: {msg.qos} {msg.payload}')
        if self.onmessage_fp != None:
            self.onmessage_fp(client, obj, msg)

    def on_publish(self, client, obj, mid):
        print(f'>> mid: {mid}')
        pass

    def on_subscribe(self, client, obj, mid, granted_qos):
        print(f'** Subscribed: {mid} {granted_qos} **')


if __name__ == "__main__":
    print('********************************************')
    print('*****  Creando una conexión de prueba  *****')
    print('********************************************')

    from time import sleep
    cliente=Cliente_MQTT()
    cliente.connect()
    sleep(10)
    cliente.disconnect()