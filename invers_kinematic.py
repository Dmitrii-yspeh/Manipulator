import numpy as np
import os

'''
переменная joint_... принимает длину звена, для звена А нужно указать 
раcтояние от нулевоё оси до первой по горизонтали (d) и вертикали (h)
'''

joint_F = 300   #mm  
joint_E = 200   #mm
joint_D = 250   #mm
joint_C = 1000  #mm
joint_B = 1500  #mm
joint_A_d = 250 #mm
joint_A_h = 300 #mm

   
flag_write_point_F = True
while(flag_write_point_F):   # ввод координаты инструмента
	
	print("Введите координату конечного положения конца инструмента в мм через пробел\n")
	print('             x    y    z')
	print('             ↓    ↓    ↓')
	point_F567 = input('Координата: ').split()
	point_F = list(map(float, point_F567))
	dfg = True
	while(dfg):
		
		#print(point_F)
		print('\nВы уверены в правильности введённых координат?\nВведите ДА или НЕТ')
		flag123 = input()
		
		if (flag123 == 'ДА'):
			flag_write_point_F = False
			dfg = False
			os.system('clear')
		else:
			if (flag123 == 'НЕТ'):
				os.system('clear')
				dfg = False
			else:
				os.system('clear')
				print('команда не определена\n')
				print(' x    y    z')
				print(' ↓    ↓    ↓')
				print(point_F)
	

flag_write_orientation_F = True
while(flag_write_orientation_F):   # ввод ориентации инструмента
	print("Введите ориентацию последнего звена в пространстве 2-мя углами в градусах через пробел")
	print("Если угол к оси z острый, то третьим элементом введите 1, иначе -1, если 90 градусам, то любое значение")
	print('Первый угол к оси X, второй угол к оси Y')
	print('        angl_x    angl_y')
	print('             ↓    ↓')
	
	orientation_F1232 = input('Ориентация: ').split()
	orientation_F = list(map(float, orientation_F1232))
	lifan = orientation_F
	dfg = True
	while(dfg):
		
		#print(point_F)
		print('\nВы уверены в правильности введённых координат?\nВведите ДА или НЕТ')
		flag123 = input()
		
		if (flag123 == 'ДА'):
			flag_write_orientation_F = False
			dfg = False
			os.system('clear')
		else:
			if (flag123 == 'НЕТ'):
				os.system('clear')
				dfg = False
			else:
				os.system('clear')
				print('команда не определена\n')
				print('angl_x angl_y')
				print(' ↓     ↓')
				print(orientation_F)
				
'''
после ввода углов программа проверит, есть ли решение для существования 3-го 
угла, например, не существует такой ориентации, где вектор находиться под углом 
1 градус к трём осям
'''
if ((1 - np.cos(float(lifan[0]) * np.pi / 180)**2 - np.cos(float(lifan[1]) * np.pi / 180)**2) >= 0):
	angle_gamma = np.arccos(np.sqrt(1 - np.cos(float(lifan[0]) * np.pi / 180)**2 - np.cos(float(lifan[1]) * np.pi / 180)**2))
	if lifan[2] == -1:
		angle = np.pi - angle_gamma
		angle_gamma = angle
		#print(angle * 180 / np.pi)
	else:
		angle = angle_gamma
		#print(angle * 180 / np.pi)
else:
	print('ошиБКА')

'''
расчёт проекций последнего звена на оси X, Y и Z
'''

joint_F_X = joint_F * np.cos(lifan[0] * np.pi / 180)
joint_F_Y = joint_F * np.cos(lifan[1] * np.pi / 180)
joint_F_Z = joint_F * np.cos(angle_gamma)

'''
раcсчёт координаты конца 5-го звена
'''

orientation_F1232 = [0, 0, 0]
point_E = list(map(float, orientation_F1232))
point_E[0] = point_F[0] + joint_F_X
point_E[1] = point_F[1] + joint_F_Y
point_E[2] = point_F[2] + joint_F_Z


'''
рассчёт проекции 5-го звена на оси X, Y и Z
'''

joint_E_X = joint_E * np.cos(lifan[0] * np.pi / 180)
joint_E_Y = joint_E * np.cos(lifan[1] * np.pi / 180)
joint_E_Z = joint_E * np.cos(angle_gamma)


'''
раcсчёт координаты конца 4-го звена
'''

point_D = list(map(float, orientation_F1232))
point_D[0] = point_E[0] + joint_E_X
point_D[1] = point_E[1] + joint_E_Y
point_D[2] = point_E[2] + joint_E_Z

########################################################################
'''
Угол звена А к плоскости XOZ вдоль оси Z
'''
angle_A = np.arctan(point_D[1] / point_D[0])   # угол для первого звена

'''
раcсчёт координаты конца 1-го звена 
'''

'''
Рассчёты треугольника, образованного звенями В, С и D
'''
point_A = list(map(float, orientation_F1232))
point_A[0] = joint_A_d * np.cos(angle_A)
point_A[1] = joint_A_d * np.sin(angle_A)
point_A[2] = joint_A_h

AK = np.sqrt((point_D[0] - point_A[0])**2 + (point_D[1] - point_A[1])**2)
h_AD = point_D[2] - point_A[2]
AD = np.sqrt(h_AD**2 + AK**2)

fi = np.arccos(((joint_C + joint_D)**2 - joint_B**2 - AD**2) / (-2 * joint_B * AD))
angle_B = np.arctan(h_AD / AK) + fi

AG = joint_B * np.cos(angle_B)

'''
раcсчёт координаты конца 2-го звена
'''

point_B = list(map(float, orientation_F1232))
point_B[0] = point_A[0] + AG * np.cos(angle_A)
point_B[1] = point_A[1] + AG * np.sin(angle_A)
point_B[2] = point_A[2] + joint_B * np.sin(angle_B)

'''
Рассчёт угла между звенами B и C
'''
angle_C = np.arccos((AD**2 - joint_B**2 - (joint_C + joint_D)**2) / (-2 * joint_B * (joint_C + joint_D)))

#print(angle_C * 180 / np.pi)

########################################################################
'''
Рассчёт матрицы для угла между звеньями C и D
'''
A1_ = np.array([[(point_B[1] - point_A[1]) / 1000, (point_B[2] - point_A[2]) / 1000],
			    [(point_D[1] - point_A[1]) / 1000, (point_D[2] - point_A[2]) / 1000]])
			    
B1_ = np.array([[(point_B[0] - point_A[0]) / 1000, (point_B[2] - point_A[2]) / 1000],
			    [(point_D[0] - point_A[0]) / 1000, (point_D[2] - point_A[2]) / 1000]])
			    
A2_ = np.array([[(point_B[1] - point_F[1]) / 1000, (point_B[2] - point_F[2]) / 1000],
			    [(point_D[1] - point_F[1]) / 1000, (point_D[2] - point_F[2]) / 1000]])

B2_ = np.array([[(point_B[0] - point_F[0]) / 1000, (point_B[2] - point_F[2]) / 1000],
			    [(point_D[0] - point_F[0]) / 1000, (point_D[2] - point_F[2]) / 1000]])

C2_ = np.array([[(point_B[0] - point_F[0]) / 1000, (point_B[1] - point_F[1]) / 1000],
			    [(point_D[0] - point_F[0]) / 1000, (point_D[1] - point_F[1]) / 1000]])

A1 = np.linalg.det(A1_)
B1 = np.linalg.det(B1_) 
B1 *= -1

A2 = np.linalg.det(A2_)
B2 = np.linalg.det(B2_)
B2 *= -1
C2 = np.linalg.det(C2_)

'''
рассчёт угла между звеньями C и D
'''
angle_D = np.arccos((A1 * A2 + B1 * B2) / (np.sqrt(A1**2 + B1**2) * np.sqrt(A2**2 + B2**2 + C2**2)))

########################################################################
'''
рассчёт угла между звеньями D и E
'''
angle_E = np.arccos(( (point_B[0] - point_D[0]) * (point_F[0] - point_D[0]) + (point_B[1] - point_D[1]) * (point_F[1] - point_D[1]) + (point_B[2] - point_D[2]) * (point_F[2] - point_D[2]) ) / (np.sqrt((point_B[0] - point_D[0])**2 + (point_B[1] - point_D[1])**2 + (point_B[2] - point_D[2])**2) * np.sqrt((point_F[0] - point_D[0])**2 + (point_F[1] - point_D[1])**2 + (point_F[2] - point_D[2])**2)))

print('angle_A', angle_A * 180 / np.pi)
print('angle_B', angle_B * 180 / np.pi)
print('angle_C', angle_C * 180 / np.pi)
print('angle_D', angle_D * 180 / np.pi)
print('angle_E', angle_E * 180 / np.pi)



