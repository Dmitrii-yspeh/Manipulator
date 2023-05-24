import RPi.GPIO as GPIO
from time import sleep

GPIO.setmode(GPIO.BCM)
GPIO.setup(12, GPIO.IN)  #концевик
GPIO.setup(16, GPIO.OUT) #шаг мотора
GPIO.setup(1, GPIO.OUT)  #направление

# функция одного шага шаговго мотора (ШМ)
def step(i):
    GPIO.output(16, GPIO.HIGH)
    sleep(i)
    GPIO.output(16, GPIO.LOW)
    sleep(i)

# функция, вызываемая внешним прерыванием на 12-ом пине
def test_c4allback(channel):
    global a
    a = 0
    
# настройка 12-го пина на прерывание 
print('Waiting for IO12 state cahnges ...')
GPIO.add_event_detect(12, GPIO.RISING, callback=test_c4allback)

# функция самого концевика
def end_joint():
    GPIO.output(1, GPIO.LOW)              # настраиваем направление к концевику
    print('зашли в функцию')              # сигнал, что зашли в функцию
    global a                              # ГЛОБАЛИЗАЦИЯ переменной а (флаг)
    a = 1                                 # 
    while (a):                            # пока a = 1 вращаем мотор до концевика
        step(0.0003)                      # как только концевик сработал происходит прерывание, которое присваивает а = 0
    print('коснулись первый раз')         
    GPIO.output(1, GPIO.HIGH)             # меняем направлением от концевика
    print("отходим от концевика")
    for i in range(0, 1600, 1):           # отходим от концевика на 1600 шагов (кол. шаг. может отл)
        step(0.00045)                     # отходим со скоростью меньшей, чем раньше
    print("отошли от концевика")
    a = 1                                 # снова ставим флаг 
    GPIO.output(1, GPIO.LOW)              # снова меняем направление в сторону концевика
    while (a):                            # движемся к концевику 
        step(0.001)                       # ещё медленее 
    print("теперь коснулись второй раз")  
    print("вышли")	


try:
    while True:
	    end_joint()           # запускаем режим концевика
	    print('Полный конец') # сигнал, что отработвали функцию end_joint() 
	    sleep(100000)         # просто долго ждём
		
except KeyboardInterrupt:
    GPIO.cleanup()

GPIO.cleanup()
