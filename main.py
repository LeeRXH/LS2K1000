#coding=gbk
import LPi.GPIO as GPIO
import time
GPIO.setmode(GPIO.LS2K)


TRIG = 9					
ECHO = 11                    
LEFT=4
RIGHT=5

#小车控制函数
def Forward():
    if guangming()==0:
      GPIO.output(LEFT,GPIO.LOW)
      GPIO.output(RIGHT,GPIO.LOW)
      print("小车前进")
    else:
      stop()
def left():
    if guangming()==0:
      GPIO.output(LEFT,GPIO.LOW)
      GPIO.output(RIGHT,GPIO.HIGH)
      print("小车左转")
    else:
      stop()
def right():
    GPIO.output(LEFT,GPIO.HIGH)
    GPIO.output(RIGHT,GPIO.LOW)   
    print("小车右转") 
def stop():
    GPIO.output(LEFT,GPIO.HIGH)
    GPIO.output(RIGHT,GPIO.HIGH) 
    print("小车停止")

#超声波测距函数
def send_trigger_pulse():
    #发送超声波，一直发
    GPIO.output(TRIG,1)
    # 为了防止错误，因为紧接着就需要把发射端置为高电平
    time.sleep(0.0001)
    #发射端置为高电平
    GPIO.output(TRIG,0)
 
#'''
#ECHO 负责接收超声波
#'''
def wait_for_echo(value,timeout):
    count = timeout
    #通过该代码持续获取ECHO的状态
    while GPIO.input(ECHO)!= value and count>0:
        count = count-1
 
#'''
#计算距离
#'''
def get_distance():
    # 发射
    send_trigger_pulse()
    # 接收高电平 1/True
    wait_for_echo(True,10000)
    # 等待
    start = time.time()
    #接收低电平
    wait_for_echo(False,10000)
    finish = time.time()
    pulse_len = finish-start
    distance_cm = pulse_len/0.000058
    return distance_cm

def fangdouget():
    distance0=get_distance()
    distance1=get_distance()
    while abs(distance0-distance1)>5:
      distance0=get_distance()
      distance1=get_distance()
    distance=(distance0+distance1)/2  
    return distance  
     
#避障函数
def Obstacle_Avoidance():
    dis= fangdouget()
    print("距离 ",dis,"cm")
    if (dis<30):              #距离小于30cm时启动避障程序
        stop()
        time.sleep(5)
        while(dis<30):   
          left()
          time.sleep(0.5)
          dis = fangdouget()
    Forward()				#继续前进




def init():
  LED_PIN1 = 1
  LED_PIN2 = 2
  LED_PIN3 = 3
  LED_PIN4 = 4
  LED_PIN5 = 5
  LED_PIN6 = 6
  LED_PIN7 = 7
  LED_PIN8 = 8
  LED_PIN9 = 9
  LED_PIN10 = 10
  LED_PIN11 = 11
  LED_PIN12 = 12
  LED_PIN13 = 13


  GPIO.setup(LED_PIN1, GPIO.OUT)
  GPIO.output(LED_PIN1, GPIO.HIGH)
  GPIO.setup(LED_PIN2, GPIO.OUT)
  GPIO.output(LED_PIN2, GPIO.HIGH)
  GPIO.setup(LED_PIN3, GPIO.IN)
  GPIO.setup(LED_PIN4, GPIO.OUT)
  GPIO.output(LED_PIN4, GPIO.HIGH)
  GPIO.setup(LED_PIN5, GPIO.OUT)
  GPIO.output(LED_PIN5, GPIO.HIGH)
  GPIO.setup(LED_PIN6,GPIO.OUT)
  GPIO.output(LED_PIN6,GPIO.LOW)
  time.sleep(0.02)
  GPIO.setup(LED_PIN6, GPIO.IN )
  GPIO.setup(LED_PIN7, GPIO.IN)
  GPIO.setup(LED_PIN8, GPIO.OUT)
  GPIO.output(LED_PIN8, GPIO.HIGH)
  GPIO.setup(LED_PIN9, GPIO.OUT)
  GPIO.output(LED_PIN9, GPIO.HIGH)
  GPIO.setup(LED_PIN11, GPIO.IN)



def shuiwei():
  shuiwei_out= 6
  baojing_pin= 8
  SHUIWEI=GPIO.input(shuiwei_out)
  if SHUIWEI==0:
    print('水位低')
    GPIO.output(baojing_pin, GPIO.LOW)
    time.sleep(0.5)
    GPIO.output(baojing_pin, GPIO.HIGH)
    return 0
  else :
    print('水位正常')
    return 1
def guangming():
	GMSWITCH=7
	ZHI=GPIO.input(GMSWITCH)
	if ZHI==GPIO.HIGH:
		return 0
	else:
		return 1
		
def juli(dis_last):
	trigger_pin =2
	echo_pin =3
	 
	# '''
	# TRIG 负责发射超声波，Echo 负责接收超声波
	# '''
	def send_trigger_pulse():
	    #发送超声波，一直发
		GPIO.output(trigger_pin,1)
	    # 为了防止错误，因为紧接着就需要把发射端置为高电平
		time.sleep(0.0001)
	    #发射端置为高电平
		GPIO.output(trigger_pin,0)
	 
	# '''
	# ECHO 负责接收超声波
	# '''
	def wait_for_echo(value,timeout):
		count = timeout
	    #通过该代码持续获取ECHO的状态
		while GPIO.input(echo_pin)!= value and count>0:
			count = count-1 
	# '''
	# 计算距离
	# '''
	def get_distance():
		# 发射
		send_trigger_pulse()
	    # 接收高电平 1/True
		wait_for_echo(True,10000)
		# 等待
		start = time.time()
		#接收低电平
		wait_for_echo(False,10000)
		finish = time.time()
		pulse_len = finish-start
		distance_cm = pulse_len/0.000058
		return distance_cm
	distance0=get_distance()
	if dis_last==0:
		if (distance0>1) & (distance0<60):
			distance1=get_distance()
			if abs(distance0-distance1)<5:
				print(" %0.2f cm"%distance1)
				dis_last = distance1
	else :	
		distance0=dis_last
		distance1=get_distance()
		if (abs(distance0-distance1)<5) | (guangming()):
			print(" %0.2f cm"%distance1)
			dis_last = distance1
		else:
			distance1=distance0
	return dis_last
	   
def dianji(val):
	MotorPin1 = 1
	GPIO.output(MotorPin1,val)

if __name__=='__main__':
    distance = 0
    init()
    try:
      Forward()#初始状态为前进
      while True:
        Obstacle_Avoidance()
        print("超声波避障系统运行中,按Ctrl+C退出...")
        waterlevel=shuiwei()
        cup=guangming()
        if cup==0:
            print('cup is unexist')
        else:
            print('cup is exist')
        distance=juli(distance)
        if (waterlevel==1)&(cup==1)&(distance>5):
            time.sleep(0.25)
            if (waterlevel==1)&(cup==1)&(distance>5):
              time.sleep(0.25)
              if (waterlevel==1)&(cup==1)&(distance>5):
                time.sleep(0.25)
                if (waterlevel==1)&(cup==1)&(distance>5):
                  time.sleep(0.25)
                  if (waterlevel==1)&(cup==1)&(distance>5):
                     time.sleep(0.25)
                     if (waterlevel==1)&(cup==1)&(distance>5):
                       dianji(0)
                       
                     else:
                      dianji(1)   
                  else:
                    dianji(1)    
                else:
                    dianji(1)   
              else:
                  dianji(1)   
            else:
              dianji(1)  
        else:
            dianji(1)
    except KeyboardInterrupt:
      stop()