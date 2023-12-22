import signal
import time
import RPi.GPIO as GPIO
import numpy as np
import math
import matplotlib.pyplot as plt

GPIO.setmode(GPIO.BCM)

GPIO.setmode(GPIO.BCM)
GPIO.setup(20, GPIO.IN)  #0 концевик
GPIO.setup(19, GPIO.IN)  #1 концевик
GPIO.setup(26, GPIO.IN)  #2 концевик
GPIO.setup(15, GPIO.OUT)  #шаг 0-го звена
GPIO.setup(18, GPIO.OUT) #напр. 0-го звена
GPIO.setup(2, GPIO.OUT)  #шаг 1-го звена
GPIO.setup(3, GPIO.OUT) #напр. 1-го звена
GPIO.setup(4, GPIO.OUT)  #шаг 2-го звена
GPIO.setup(14, GPIO.OUT) #напр. 2-го звена

def initialization(pins):
	for i in range(len(pins)-1, -1, -1):
	
		con[i] = True
		if GPIO.input(pins[i][0]):
			GPIO.output(pins[i][2], 0)
			while(con[i]):
				step(0.000001, pins[i][1])
		GPIO.output(pins[i][2], 1)
		for k in range(0, 4000):           # отходим от концевика на 1600 шагов (кол. шаг. может отл)
			step(0.000005, pins[i][1])
		GPIO.output(pins[i][2], 0)
		con[i] = True
		while(con[i]):
			step(0.0001, pins[i][1])
		if i==3:
			GPIO.output(pins[i][2], 1)
			for j in range(0, 59500):      # было 57000
				step(0.00001, pins[i][1])
		if i==4:
			GPIO.output(pins[i][2], 1)
			for j in range(0, 33400):	   # было 43000
				step(0.00001, pins[i][1])

def invers_kinematic(Dx, Dy, Dz):
	D = 95   #mm
	C = 95  #mm
	B = 214.6  #mm
	Ad = 44.5 #mm
	Ah = 107 #mm
	
	if Dx != 0:
		g1 = np.arctan(Dy/Dx)
	else:
		g1 = np.pi/2
	
	Ax =  Ad*np.cos(g1)
	Ay =  Ad*np.sin(g1)
	Az = Ah
	
	c_l = ((Dx-Ax)**2 + (Dy-Ay)**2 + (Dz-Az)**2)**0.5
	g2 = np.arctan((Dz-Ah)/((Dx-Ax)**2 + (Dy-Ay)**2)**0.5) + np.arccos(((C+D)**2 - c_l**2 - B**2)/(-2*c_l*B))
	
	g3 = np.arccos((c_l**2 - B**2 - (C+D)**2)/(-2*B*(C+D))) - np.pi
	
	return g1, g2, g3

def forw_kin(g1, g2, g3):
	D = 95   #mm
	C = 95  #mm
	B = 214.6  #mm
	Ad = 44.5 #mm
	Ah = 107 #mm
	
	a = np.cos(g1)
	b = np.sin(g1)

	c = np.cos(g2)
	d = np.sin(g2)

	e = np.cos(g3 + np.pi/2)
	f = np.sin(g3 + np.pi/2)
	
	X = (C+D)*(a*c*f+a*d*e)+a*(B*c+Ad)
	Y = (C+D)*(b*c*f+b*d*e)+b*(B*c+Ad)
	Z = (C+D)*(d*f-c*e)+B*d+Ah
	
	return X, Y, Z

# поиск точки по середине между двумя данными точками
def media_line(x1, x2, y1, y2, z1, z2):
	x = x1 + ((x2 - x1) / 2)
	y = y1 + ((y2 - y1) / 2)
	z = z1 + ((z2 - z1) / 2)
	return x, y, z

# генерация базисных функций
def bas_fun(n, k, X, x, y, z, b, h):
	x1 = []
	y1 = []
	z1 = []
	G = []
	N = np.zeros((k, n+1))
	for i in range(0, len(X)-1):
		if X[i] < X[i+1]:
			G.append(i+1)
	for i in range(0, len(G)):                        # обход через каждые промежутки от t_i до t_i+1 
		for colon in range(0, k):
			for level in range(0, n+1):
				N[colon][level] = 0
		
		for t in range(0, b):                         # инкрементация t в промежутке от t_i до t_i+1 на b частей
			t = X[G[i]-1] + t*(X[G[i]] - X[G[i]-1])/b 
			for j in range(0, k):                     # порядок базисных функций по степени кривой 
				for i_ in range(0, n+1, 1):                # номер базисной функции порядка k
					if j == 0: 
						if X[i_] <= t and t < X[i_+1] and X[i_] != X[i_+1]:
							N[0][i_] = 1
					else:
						if X[j+i_] - X[i_] != 0 and X[j+i_+1] - X[i_+1] != 0:
							N[j][i_] = ((t-X[i_])*N[j-1][i_]  /  (X[j+i_] - X[i_]))  +  ((X[j+i_+1]-t)*N[j-1][i_+1]  /  (X[j+i_+1] - X[i_+1]))
						elif X[j+i_] - X[i_] == 0 and X[j+i_+1] - X[i_+1] != 0:
							N[j][i_] = ((X[j+i_+1]-t)*N[j-1][i_+1]  /  (X[j+i_+1] - X[i_+1]))
						elif X[j+i_] - X[i_] != 0 and X[j+i_+1] - X[i_+1] == 0:
							N[j][i_] = ((t-X[i_])*N[j-1][i_])  /  (X[j+i_] - X[i_])
						elif X[j+i_] - X[i_] == 0 and X[j+i_+1] - X[i_+1] == 0:
							N[j][i_] = 0	
			_x = 0
			_y = 0
			_z = 0
			odn_koor = 0
			for GN in range(0, n+1):         # финишное вычисление координаты от параметра t 
				if GN == 0 or GN == n:
					_x += x[GN]*N[k-1][GN]
					_y += y[GN]*N[k-1][GN]
					_z += z[GN]*N[k-1][GN]
					odn_koor += N[k-1][GN]
				else:
					_x += x[GN]*h*N[k-1][GN]
					_y += y[GN]*h*N[k-1][GN]
					_z += z[GN]*h*N[k-1][GN]
					odn_koor += h*N[k-1][GN]		
			
			x1.append(_x / odn_koor)
			y1.append(_y / odn_koor)
			z1.append(_z / odn_koor)
	return x1, y1, z1

# генерация сплайна
def general_spline(x2, y2, z2, k, n, b, h):
	if n < k:                    
		n = k
	
	# генерация узлового вектора
	X = []
	for i in range(1, n+k+2):         
		if 1 <= i and i <= k:
			X.append(0)
		elif k+1 <= i and i <= n+1:
			X.append(i-k)	
		elif n+2 <= i and i <= n+k+1:
			X.append(n-k+2)

	x_supp = [0]*(n+1)
	y_supp = [0]*(n+1)
	z_supp = [0]*(n+1)
	xf = []
	yf = []
	zf = []

	###################################################################################
	# генерация первого сегмента
	for i in range(0, n+1):                          
		if i != n:
			x_supp[i] = x2[i]
			y_supp[i] = y2[i]
			z_supp[i] = z2[i]
		else:
			x_media, y_media, z_media = media_line(x2[n-1], x2[n], y2[n-1], y2[n], z2[n-1], z2[n])
			x_supp[i] = x_media
			y_supp[i] = y_media
			z_supp[i] = z_media
	x_, y_, z_ = bas_fun(n, k, X, x_supp, y_supp, z_supp, b, h)
	xf.extend(x_)
	yf.extend(y_)
	zf.extend(z_)
	#ax.scatter(xf, yf, s = 0.5)

	# генерация сегментов между 1-ым и последним сегментами
	cor= 0             
	for i in range(1, (len(x2)-2)//(n-1)-1):                                         
		x_media, y_media, z_media = media_line(x2[n*i-1 - cor], x2[n*i - cor], y2[n*i-1 - cor], y2[n*i - cor], z2[n*i-1 - cor], z2[n*i - cor])
		x_supp[0] = x_media
		y_supp[0] = y_media
		z_supp[0] = z_media
		x_supp[1] = x2[n*i - cor]
		y_supp[1] = y2[n*i - cor]
		z_supp[1] = z2[n*i - cor]
		for j in range(2, n-1):
			x_supp[j] = x2[j+i*n-1 - cor]
			y_supp[j] = y2[j+i*n-1 - cor]
			z_supp[j] = z2[j+i*n-1 - cor]
		x_supp[n-1] = x2[n*(i+1)-2 - cor]
		y_supp[n-1] = y2[n*(i+1)-2 - cor]
		z_supp[n-1] = z2[n*(i+1)-2 - cor]
		x_media, y_media, z_media = media_line(x2[n*(i+1)-2 - cor], x2[n*(i+1)-1 - cor], y2[n*(i+1)-2 - cor], y2[n*(i+1)-1 - cor], z2[n*(i+1)-2 - cor], z2[n*(i+1)-1 - cor])
		x_supp[n] = x_media
		y_supp[n] = y_media
		z_supp[n] = z_media
		cor += 1
		x_, y_, z_ = bas_fun(n, k, X, x_supp, y_supp, z_supp, b, h)
		xf.extend(x_)
		yf.extend(y_)
		zf.extend(z_)   

	# генерация последненго сегмента
	doorstep = (len(x2)-2)%(n-1)   
	x_supp = [0]*(n+1+doorstep)
	y_supp = [0]*(n+1+doorstep)
	z_supp = [0]*(n+1+doorstep)

	X = []
	for i in range(1, n+doorstep+k+2):   # генерация узлового вектора
		if 1 <= i and i <= k:
			X.append(0)
		elif k+1 <= i and i <= n+doorstep+1:
			X.append(i-k)	
		elif n+doorstep+2 <= i and i <= n+doorstep+k+1:
			X.append(n+doorstep-k+2)

	x_media, y_media, z_media = media_line(x2[len(x2) - n - doorstep - 1], x2[len(x2) - n - doorstep], y2[len(x2) - n - doorstep - 1], y2[len(x2) - n - doorstep], z2[len(x2) - n - doorstep - 1], z2[len(x2) - n - doorstep])
	x_supp[0] = x_media
	y_supp[0] = y_media
	z_supp[0] = z_media
	for i in range(0, n + doorstep):
		x_supp[i + 1] = x2[len(x2) - n - doorstep + i]
		y_supp[i + 1] = y2[len(x2) - n - doorstep + i]
		z_supp[i + 1] = z2[len(x2) - n - doorstep + i]
	x_, y_, z_ = bas_fun(n + doorstep, k, X, x_supp, y_supp, z_supp, b, h)
	xf.extend(x_)
	yf.extend(y_)
	zf.extend(z_)
	xf.append(x2[-1])
	yf.append(y2[-1])
	zf.append(z2[-1])
	# конец генерации сплайна по точкам x2 и y2	
	###################################################################################
	return xf, yf, zf

time_0 = 0
time_1 = 0
time_2 = 0

def handler(sig_num, curr_stack_frame):
	global time_0
	global time_1
	global time_2
	time_0 += 0.00005
	time_1 += 0.00005
	time_2 += 0.00005
	
if __name__ == "__main__":
	signal.signal(signal.SIGALRM, handler)
	
	k = 3                  # степень кривой
	n = 3                  # количество базисных функций
	b = 20                 # количество областей одного сегмент после разбиения
	h = 50                  # масса точки
	min_dopusk = 1         # допуск по близлежащим точкам (удаление точек в радиусе заданного значения)+1+p
	dopusk_line = 0.999    # допуск по точкам на линии
	
	if n < k:                         # условие возможности создания сплайна, порядок кривой k не должен быть больше чем количество сегментов n
		n = k

	u = 50          	   # мм/с
	increment = 10   	   # мм

	step_now_0 = 0
	step_now_1 = 38400
	step_now_2 = -38400
	
	#target = [[0, 200], [-32, 208], [-59, 221], [-75, 250], [-80, 280], [-75, 310], [-58, 335], [-32, 352],  [0, 360], [32, 352], [58, 335], [72, 310], [80, 280], [75, 250], [58, 222], [32, 208], [0, 200], [-300, 217], [180, 217]]
	#target = [[0, 200, 0], [-300, 217, 50], [0, 100, 30], [0, 390, 3], [191, 217, 56], [342, 0, 322]]
	target = [[50, 0, 310], [50, -200, 100], [250, -200, 310], [255, 0, 100], [50, 0, 310], [50, -200, 100], [250, -200, 310], [255, 0, 100], [234.5, 0, 321.6]]
	
	x = []
	y = []
	z = []
	x_now, y_now, z_now = forw_kin(np.pi*step_now_0/31200, np.pi*step_now_1/76800, np.pi*step_now_2/76800)
	x.append(x_now)
	y.append(y_now)
	z.append(z_now)
	for i in range(len(target)):
		x.append(target[i][0])
		y.append(target[i][1])
		z.append(target[i][2])
	
	xf, yf, zf = general_spline(x, y, z, k, n, b, h)
	
	for i in range(len(xf)):
		signal.setitimer(signal.ITIMER_REAL, 0.001, 0.00005)	
		x_now, y_now, z_now = forw_kin(np.pi*step_now_0/31200, np.pi*step_now_1/76800, np.pi*step_now_2/76800)
		dx = xf[i] - x_now
		dy = yf[i] - y_now
		dz = zf[i] - z_now
		
		print("dx  -  ", dx)
		
		dl = (dx**2 + dy**2 + dz**2)**0.5
		q_l = math.ceil(dl / increment)
		tim = dl / u
		
		if q_l != 0:
			i_d_x = dx / q_l
			i_d_y = dy / q_l
			i_d_z = dz / q_l
		else:
			i_d_x = 0
			i_d_y = 0
			i_d_z = 0
		
		b = time.time()
		for i in range(1, q_l+1, 1):
			angle_A, angle_B, angle_C = invers_kinematic(x_now + i*i_d_x, y_now + i*i_d_y, z_now + i*i_d_z)
			#angle_A = np.pi*angle_A/180
			
			#steps_0 = round(9.75*angle_A * 16000 / 9)
			print("step_now  -  ", 31200*angle_A / np.pi)
			steps_0 = round(31200*angle_A / np.pi)
			steps_1 = round(angle_B * 76800 / np.pi)
			steps_2 = round(angle_C * 76800 / np.pi)
									
			d_steps_0 = steps_0 - step_now_0
			d_steps_1 = steps_1 - step_now_1
			d_steps_2 = steps_2 - step_now_2
						
			#############################################################
			if d_steps_0 != 0:
				del_tim_0 = tim / (abs(d_steps_0) * (q_l+1))
			else:
				del_tim_0 = 10000000000
			
			if d_steps_1 != 0:
				del_tim_1 = tim / (abs(d_steps_1) * (q_l+1))
			else:
				del_tim_1 = 10000000000
			
			if d_steps_2 != 0:
				del_tim_2 = tim / (abs(d_steps_2) * (q_l+1))	
			else:
				del_tim_2 = 10000000000
				
							
			#############################################################
			if d_steps_0 > 0:
				GPIO.output(18, GPIO.HIGH)
				inv0 = 1
			else:
				GPIO.output(18, GPIO.LOW)
				inv0 = -1
			
			if d_steps_1 > 0:
				GPIO.output(3, GPIO.LOW)
				inv1 = 1
			else:
				GPIO.output(3, GPIO.HIGH)
				inv1 = -1
					
			if d_steps_2 > 0:
				GPIO.output(14, GPIO.HIGH)
				inv2 = 1
			else:
				GPIO.output(14, GPIO.LOW)
				inv2 = -1	
			
			#############################################################
			
			steper_0 = 0
			steper_1 = 0
			steper_2 = 0
		
			#############################################################
			while(steper_2 < abs(d_steps_2)):
				if time_0 >= del_tim_0:
					GPIO.output(15, GPIO.HIGH)
					steper_0 += 1
					step_now_0 += inv0
					time_0 -= del_tim_0
					GPIO.output(15, GPIO.LOW)
				
				if time_1 >= del_tim_1:
					GPIO.output(2, GPIO.HIGH)
					steper_1 += 1
					step_now_1 += inv1
					time_1 -= del_tim_1
					GPIO.output(2, GPIO.LOW)
				
				if time_2 >= del_tim_2:
					GPIO.output(4, GPIO.HIGH)
					steper_2 += 1
					step_now_2 += inv2
					time_2 -= del_tim_2
					GPIO.output(4, GPIO.LOW)
		signal.setitimer(signal.ITIMER_REAL, 0, 0)		
				
		#print("углы - ", angle_A, angle_B)
		print("time - ", time.time() - b)
		print("step_now_0 - ", step_now_0)
		print("step_now_1 - ", step_now_1)
		print("step_now_2 - ", step_now_2)
		print("")
	
	GPIO.cleanup()
	
	
	fig, ax = plt.subplots()
	fig.subplots_adjust(left=0.02, right=0.99, top=0.98, bottom=0.2)
	fig = plt.figure()
	ax1 = plt.axes(projection='3d')
	
	ax1.plot3D(x, y, z)
	ax1.plot3D(xf, yf, zf)
	
	plt.show()
