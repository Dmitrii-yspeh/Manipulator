import RPi.GPIO as GPIO
from time import sleep
from multiprocessing import Pipe, Process, Barrier


GPIO.setmode(GPIO.BCM)
GPIO.setup(20, GPIO.IN)  #0 концевик
GPIO.setup(19, GPIO.IN)  #1 концевик
GPIO.setup(15, GPIO.OUT)  #шаг 0-го звена
GPIO.setup(18, GPIO.OUT) #напр. 0-го звена
GPIO.setup(2, GPIO.OUT)  #шаг 1-го звена
GPIO.setup(3, GPIO.OUT) #напр. 1-го звена

def steper(i, pin_step):     # функция шага мотора
    GPIO.output(pin_step, GPIO.HIGH)
    sleep(i)
    GPIO.output(pin_step, GPIO.LOW)
    sleep(i)

def loop0(bar, inp_step, inp_time):    # 0-е звено
	while True:
		bar.wait()                     # ожидаем, когда все 3 процесса будут готов
		step = inp_step.recv()         # присвоение step значения из канала
		i_time = inp_time.recv()       # присвоение i_time значения из канала     
		if step > 0:                   # проверка в какую сторону вращать мотор
			GPIO.output(18, GPIO.HIGH) # cигнал на враение по асовой
			print("+")                 # 
		else:                       
			GPIO.output(18, GPIO.LOW)  # против часовой
			print("-")                 # 
		
		for i in range(abs(step)):     # вращение мотора за заданое количество шагов на итерацию
			steper(i_time, 15)         # функция шага
	
def loop1(bar, inp_step, inp_time):    # тут всё идентично
	while True:
		bar.wait()
		step = inp_step.recv()
		i_time = inp_time.recv()
		if step > 0:
			GPIO.output(3, GPIO.HIGH)
			print("+")
		else:
			GPIO.output(3, GPIO.LOW)
			print("-")
		
		for i in range(abs(step)):
			steper(i_time, 2)
		

step_out_0, step_inp_0 = Pipe()   # канал для передачи процессу количества шагов на итерацию 0-му звену
step_out_1, step_inp_1 = Pipe()   # 1-му звену
time_step_out_0, time_step_inp_0 = Pipe() # передача времени между двумя шагами нулевого звена
time_step_out_1, time_step_inp_1 = Pipe() # 1-го зввена
bar = Barrier(3) # барьер на 3 процесса: основной процесс и процессы 0-го и 1-го звеньев

 
Process(target=loop0, args = (bar, step_inp_0, time_step_inp_0,)).start() # запуск процеса 0-го звена 
Process(target=loop1, args = (bar, step_inp_1, time_step_inp_1,)).start() # запуск процеса 1-го звена

t = 0.02    # время перемещения в секундах

angle_now_0 = -34   # начальный угол 0-го звена
angle_now_1 = -3    # начальный угол 1-го звена

mass0 = [0, 50, 30]  # списки с углами на итерацию, сначало принять угол 0 град, потом 50 ...
mass1 = [30, 50, 30] # 


for i in range(0, len(mass0)):
	bar.wait()
	
	stp0 = round(520 / 3 * (mass0[i] - angle_now_0))    # перевод из градусов в кол. шагов
	angle_now_0 = mass0[i]                              
	time0 = abs(t / 2 / stp0)                           # вычисление времени между шагами
	time_step_out_0.send(time0)
	step_out_0.send(stp0)

	stp1 = round(1280 / 3 * (mass1[i] - angle_now_1))
	angle_now_1 = mass1[i]
	time1 = abs(t / 2 / stp1)
	time_step_out_1.send(time1)
	step_out_1.send(stp1)
	
	
	
	print("Иттерация - ", i) 
	print("Дельта", stp0)
print("Всё")
