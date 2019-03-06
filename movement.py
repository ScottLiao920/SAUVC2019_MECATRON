import serial
import time

ser = serial.Serial(
    port='/dev/ttyUSB0',# Change port
    baudrate=115200,
    parity=serial.PARITY_ODD,
    stopbits=serial.STOPBITS_ONE,
    bytesize=serial.EIGHTBITS
)

# Bytes format: 
# left right, up, down, foward, backward, arm
# first 6 bytes set to zero: stop
# arm: 1 for change current situation, 0 is to remain the same

def turn_left():
    ser.write('10000000\r\n'.encode('ascii'))
    return 0


def turn_right():
    ser.write('01000000\r\n'.encode('ascii'))
    return 0


def move_fwd():
    ser.write('00100000\r\n'.encode('ascii'))
    return 0


def move_bwd():
    ser.write('00010000\r\n'.encode('ascii'))
    return 0


def move_up():
    ser.write('00001000\r\n'.encode('ascii'))
    return 0


def move_down():
    ser.write('00000100\r\n'.encode('ascii'))
    return 0


def stop():
    ser.write('00000000\r\n'.encode('ascii'))
    return 0


def arm_drop():
    ser.write('00000010\r\n'.encode('ascii'))
    return 0


def arm_pick():
    ser.write('00000011\r\n'.encode('ascii'))
    return 0
