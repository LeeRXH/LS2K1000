
import LPi.GPIO as GPIO		
import time					

GPIO.setmode(GPIO.LS2K)     	

TRIG = 9					
ECHO = 11                    
LEFT=4
RIGHT=5

GPIO.setup(LEFT,GPIO.OUT)
GPIO.setup(RIGHT,GPIO.OUT)
GPIO.output(LEFT,GPIO.HIGH)
GPIO.output(RIGHT,GPIO.HIGH) 
GPIO.setup(TRIG,GPIO.OUT)
GPIO.setup(ECHO,GPIO.IN)

#小车控制函数
def Forward():
    GPIO.output(LEFT,GPIO.LOW)
    GPIO.output(RIGHT,GPIO.LOW)
    print("小车前进")
def left():
    GPIO.output(LEFT,GPIO.LOW)
    GPIO.output(RIGHT,GPIO.HIGH)
    print("小车左转")
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
 
# '''
# ECHO 负责接收超声波
# '''
def wait_for_echo(value,timeout):
    count = timeout
    #通过该代码持续获取ECHO的状态
    while GPIO.input(ECHO)!= value and count>0:
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
def fangdou():
    dis=[0,0,0,0]
    dis[0] = get_distance()
    time.sleep(0.001)
    dis[1] = get_distance()
    time.sleep(0.001)
    dis[2] = get_distance()
    time.sleep(0.001)
    dis[3] = get_distance()
    time.sleep(0.001)
    if ((abs(dis[0]-dis[3])+abs(dis[1]-dis[2]))/2) < 5:
        return  sum(dis)/4         
#避障函数
def Obstacle_Avoidance():
    dis= fangdou()
    print("距离 ",dis,"cm")
    if (dis<30):              #距离小于30cm时启动避障程序
        stop()
        time.sleep(5)
        while dis<30:
            left()
            dis = fangdou()
    Forward()				#继续前进
    time.sleep(0.5)
print("超声波避障系统运行中,按Ctrl+C退出...")
try:
    Forward()				#初始状态为前进
    Obstacle_Avoidance()
except KeyboardInterrupt:
    stop()
