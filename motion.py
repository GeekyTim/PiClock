from gpiozero import MotionSensor, LED
from signal import pause

pir = MotionSensor(25)


while 1==1:
    if (pir.motion_detected):
        print("Hello")
    else:
        print("Still")

pause()
