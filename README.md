# iot_python
Módulos en Python para hacer pruebas IoT
### Tecnologías:  
- Python
- MQTT
---
### Uso:  
1. Para simplemente leer el valor de temperatura reportado por los sensores del computador:  
```
python3 cores_temp.py
```
2. Para probar el cliente local MQTT:  
```
python3 mqtt_client.py
```
3. Para enviar los valores de temperatura reportado por los sensores del computador a un servicio de almacenamiento remoto:  
```
python3 test_mqtt.py [-h] [-f, --file FILE] [--version]
```

## Archivo de configuración
Crear el archivo **mqttconfig** (__formato json__) en la carpeta correspondiente al servicio de almacenamiento remoto.  
Ej: Ubidots --> __Ubidots/mqttconfig__ con la siguiente estructura: 
```
{"host":"industrial.api.ubidots.com",
"port":"1883",
"transport":"tcp",
"sufix":"None",
"keepalive":"300",
"clean":"True",
"user":xxxx,
"pass":yyyy,
"topic":zzzz,
"devices_subscribe":[{"name":"pc_toshiba","vars":["temp"]}],
"devices_publish":[{"name":"pc_toshiba","vars":["temp"]}]
}
```
donde:  
__**xxxx**__: Usuario asignado por el servicio de nube  
__**yyyy**__: Contraseña asignada por el servicio de nube  
__**zzzz**__: Tópico sobre el cual se realizará la publicación de los datos

---
### Ejemplo
```
python3 test_mqtt.py -f ./Ubidots/mqttconfig
``
