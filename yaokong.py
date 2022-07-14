#UTF-8
import LPi.GPIO as GPIO
import tty,sys,select,termios
GPIO.setmode(GPIO.LS2K)
LEFT=4
RIGHT=5
GPIO.setup(LEFT,GPIO.OUT)
GPIO.setup(RIGHT,GPIO.OUT)
GPIO.output(LEFT,GPIO.HIGH)
GPIO.output(RIGHT,GPIO.HIGH) 

def getKey(settings):
    tty.setraw(sys.stdin.fileno())
    rlist = select.select([sys.stdin],[],[],0.1)
    
    if rlist:
        key = sys.stdin.read(1)
    else:
        key = ""
    
    termios.tcsetattr(sys.stdin,termios.TCSADRAIN,settings)
    return key
def Forward():
    GPIO.output(LEFT,GPIO.LOW)
    GPIO.output(RIGHT,GPIO.LOW)
    print("forward")
def left():
    GPIO.output(LEFT,GPIO.LOW)
    GPIO.output(RIGHT,GPIO.HIGH)
    print("left")
def right():
    GPIO.output(LEFT,GPIO.HIGH)
    GPIO.output(RIGHT,GPIO.LOW)   
    print("right") 
def stop():
    GPIO.output(LEFT,GPIO.HIGH)
    GPIO.output(RIGHT,GPIO.HIGH) 
    print("stop")
while True:
    setting = termios.tcgetattr(sys.stdin)
    inp=getKey(setting)
    if inp == 'w':
        Forward()
    if inp == 'a':
        left()
    if inp == 'd':
        right()
    if inp == 's':
        stop()
    if inp == 'q':
        stop()
        quit()
