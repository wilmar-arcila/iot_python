#!/usr/bin/python3
# -- coding: utf-8 --
'''Lee la temperatura de los núcleos de la cpu.

Falta la descripión completa.
'''

__author__ = "Wilmar Arcila Castaño"
__copyright__ = "Æthyr Systems"
__credits__ = ["Wilmar Arcila Castaño", "Æthyr"]
__license__ = "GPL"
__version__ = "0.0.2"
__maintainer__ = "Wilmar Arcila Castaño"
__email__ = "wilmararcilac@gmail.com"
__status__ = "Prototipo"
__date__ = "31/05/2022"


from time import time, sleep
from pathlib import Path
__basedir__='/sys/devices/platform/'

def locate_sensors():
	'''Busca la referencia del sensor de temperatura en los nodos del sistema.

	Devuelve una lista de tuplas, cada una de tres elementos: (Variable,label,Path_to_temp_value)'''
	p=Path(__basedir__)
	dirs=list(filter(lambda r: r.match('*/*temp*'),[x for x in p.iterdir() if x.is_dir()]))
	print(dirs)
	if len(dirs)==0:
		print('No se ha encontrado driver para el sensor de temperatura del núcleo.')
		return -1
	elif len(dirs)==1:
		driver=dirs[0].stem
		print(f'Driver del sensor de temperatura: {driver}')
		while len(dirs)!=0:
			p=p / dirs[0].name
			dirs=list(filter(lambda r: r.match('*/hwmon*'),[x for x in p.iterdir() if x.is_dir()]))
		print(p)
		labels=sorted(list(filter(lambda r: r.match('*/temp[0-9]_label'),[x for x in p.iterdir() if not x.is_dir()])))
		values=sorted(list(filter(lambda r: r.match('*/temp[0-9]_input'),[x for x in p.iterdir() if not x.is_dir()])))
		sensors=[]
		for l,v in zip(labels,values):
			sensor=''
			label=l.name
			with l.open() as f: sensor=f.readline().rstrip('\n')
			sensors.append((sensor,label,v))
		return sensors
	elif len(dirs)>1:
		print('Se ha encontrado más de un driver para el sensor de temperatura del núcleo.\n--TBD--')
		return -1
	else:
		print('Error desconocido')
		return -1

def read_temp(sensors):
	'''Arg: Lista de tuplas, cada una de tres elementos, indicando nombre de la variable, 
	label y Path al archivo desde el cual leer el valor del sensor.
	Return: Lista de tuplas, cada una de cutro elementos. Los dos primeros son iguales a sus 
	equivalentes en el argumento (Arg), el tercer elemento es la temperatura leída para el 
	sensor, y el cuarto es el timestamp de la lectura.
	'''
	temp_values=[]
	for i in sensors:
		_timestamp=time()
		_temp=''
		with i[2].open() as f: _temp=f.readline().rstrip('\n')
		temp_values.append((i[0],i[1],float(_temp)/1000,_timestamp))
	return temp_values


if __name__ == "__main__":
	sensors=locate_sensors()
	print(sensors,'\n')
	cont=0
	while cont<5:
		cont+=1
		t_values=read_temp(sensors)
		for i in t_values:
			print(i)
		print()
		sleep(5)