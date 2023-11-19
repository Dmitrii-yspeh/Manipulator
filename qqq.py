import signal
import time
import RPi.GPIO as GPIO
from numpy import arccos, arctan, pi, cos, sin, pi
import math

GPIO.setmode(GPIO.BCM)
GPIO.setup(20, GPIO.IN)  #0 концевик
GPIO.setup(19, GPIO.IN)  #1 концевик
GPIO.setup(15, GPIO.OUT)  #шаг 0-го звена
GPIO.setup(18, GPIO.OUT) #напр. 0-го звена
GPIO.setup(2, GPIO.OUT)  #шаг 1-го звена
GPIO.setup(3, GPIO.OUT) #напр. 1-го звена
GPIO.setup(4, GPIO.OUT)  #шаг 2-го звена
GPIO.setup(14, GPIO.OUT) #напр. 2-го звена

def inv_kin(x, y):
	A = 217 # мм
	B = 180 # мм
	betta = 180 * (arccos((A**2 + B**2 - x**2 - y**2) / (2*A*B))) / pi
	if x != 0:
		alfa = 180 * (pi - arccos((x**2 + y**2 + A**2 - B**2) / (2*A*(x**2 + y**2)**0.5)) - arccos(x / (x**2 + y**2)**0.5)) / pi
	else:
		alfa = 180 * (pi - arccos((x**2 + y**2 + A**2 - B**2) / (2*A*(x**2 + y**2)**0.5)) - pi / 2) / pi
	return alfa, betta

def forw_kin(angle_A, angle_B):
	angle_A = angle_A * pi / 180
	angle_B = angle_B * pi / 180
	A = 217 # мм
	B = 180 # мм
	x = -A * cos(angle_A) + B * cos(angle_B - angle_A)
	y = A * sin(angle_A) + B * sin(angle_B - angle_A)
	return(x, y)

time_0 = 0
time_1 = 0
time_2 = 0
time_3 = 0
time_4 = 0
time_5 = 0
time_6 = 0

def handler(sig_num, curr_stack_frame):
	global time_1
	global time_2
	time_1 += 0.00005
	time_2 += 0.00005
	
	
if __name__ == "__main__":
	signal.signal(signal.SIGALRM, handler)
	

	tim = 5 # секунд
	increment = 10 # мм

	step_now_0 = 0
	step_now_1 = 38400
	step_now_2 = 38400
	
	target = [[-300, 217], [0, 390], [180, 217], [-300, 217], [0, 390], [180, 217]]
	
	for i in range(len(target)):
		#print("")
		signal.setitimer(signal.ITIMER_REAL, 0.001, 0.00005)
		x_now, y_now = forw_kin(3*step_now_1/1280, 3*step_now_2/1280)
		#print("x_now - ", x_now)
		#print("y_now - ", y_now)
		dx = target[i][0] - x_now
		dy = target[i][1] - y_now
		#print("dx - ", dx)
		#print("dy - ", dy)
		dl = (dx**2 + dy**2)**0.5
		q_l = math.ceil(dl / increment)
		#print("q_l - ", q_l)
		i_d_x = dx / q_l
		i_d_y = dy / q_l
		#print("i_d_x - ", i_d_x)
		#print("i_d_y - ", i_d_y)
		b = time.time()
		for i in range(1, q_l+1, 1):
			#print(x_now + i*i_d_x, y_now + i*i_d_y)
			angle_A, angle_B = inv_kin(x_now + i*i_d_x, y_now + i*i_d_y)
			print("tim - ", tim)
			#print("углы", angle_A, angle_B)
			#print("")
			steps_1 = round(8*angle_A * 160 / 3)
			steps_2 = round(8*angle_B * 160 / 3)
			
			d_steps_1 = steps_1 - step_now_1
			d_steps_2 = steps_2 - step_now_2
			
			#print("d_steps_1 - ", d_steps_1)
			#print("d_steps_2 - ", d_steps_2)
			#print("")
			#############################################################
			if d_steps_1 != 0:
				del_tim_1 = tim / (abs(d_steps_1) * (q_l+1))
			if d_steps_2 != 0:
				del_tim_2 = tim / (abs(d_steps_2) * (q_l+1))	
				
			print(del_tim_1)
			print(del_tim_2)	
			print("")
			#############################################################
			if d_steps_1 > 0:
				GPIO.output(3, GPIO.HIGH)
				inv1 = 1
			else:
				GPIO.output(3, GPIO.LOW)
				inv1 = -1
					
			if d_steps_2 > 0:
				GPIO.output(14, GPIO.HIGH)
				inv2 = 1
			else:
				GPIO.output(14, GPIO.LOW)
				inv2 = -1	
			#############################################################

			steper_1 = 0
			steper_2 = 0
		
			#############################################################
			while(steper_2 < abs(d_steps_2)):
				if time_1 >= del_tim_1:
					GPIO.output(2, GPIO.HIGH)
					steper_1 += 1
					step_now_1 += inv1
					GPIO.output(2, GPIO.LOW)
					time_1 -= del_tim_1
					
					
				if time_2 >= del_tim_2:
					GPIO.output(4, GPIO.HIGH)
					steper_2 += 1
					step_now_2 += inv2
					GPIO.output(4, GPIO.LOW)
					time_2 -= del_tim_2
		signal.setitimer(signal.ITIMER_REAL, 0, 0)
		#print("углы - ", angle_A, angle_B)
		print("time - ", time.time() - b)
		print("step_now_1 - ", step_now_1)
		print("step_now_2 - ", step_now_2)
		#time.sleep(3)

		
	
	signal.setitimer(signal.ITIMER_REAL, 0, 0)
	GPIO.cleanup()
