int ENA = 4;                // Разрешение драйверу вращать мотор - 4-ый контакт 
int DIR = 3;                // Подключение для направления вращения - 3-ий контакт
int STEP = 2;               // Контакт подачи импулса для сигнала сделать шаг - 2-ой контакт
void setup()
{                             
     pinMode(ENA, OUTPUT);       // Контакты ENA, DIR и STEP НА вывод сигнала
     pinMode(DIR, OUTPUT);       // 
     pinMode(STEP, OUTPUT);      // 
}                                        
                                          
void loop()
{    
  digitalWrite(ENA, 0);          // Разрешаем работу двигателя
  digitalWrite(DIR, 0);          // Выбираем направление вращения.
     
  for(int i=0; i<1600; i++)      // Совершаем 1600 шагов, что соответствует 8-ми оборотам шагового двигателя
  {        
    digitalWrite(STEP, 1 );      // Подаём сигнал
    delayMicroseconds(300);      // Ждём 300 микрсекунд
    digitalWrite(STEP, 0);       // Прекращаем сигнал
    delayMicroseconds(300);      // Ждём 300 микрсекунд
  }                                    
  
  digitalWrite(DIR, 1);          //   Меняем направление движения вала
  for(int i=0; i<1600; i++)
  {
    digitalWrite(STEP, 1);       // Подаём сигнал
    delayMicroseconds(300);      // Ждём 300 микрсекунд
    digitalWrite(STEP, 0);       // Прекращаем сигнал
    delayMicroseconds(300);      // Ждём 300 микрсекунд
  }                                   
} 
