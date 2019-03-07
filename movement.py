import serial

ser = serial.Serial(
    port='/dev/ttyUSB0',  # Change port
    baudrate=115200,
    parity=serial.PARITY_ODD,
    stopbits=serial.STOPBITS_ONE,
    bytesize=serial.SEVENBITS
)


# Bytes format:
# left right, up, down, foward, backward, arm
# first 6 bytes set to zero: stop
# arm: 1 for change current situation, 0 is to remain the same

def turn_left():
    ser.write('1000000\r\n'.encode('ascii'))
    return 0


def turn_right():
    ser.write('0100000\r\n'.encode('ascii'))
    return 0


def move_fwd():
    ser.write('0010000\r\n'.encode('ascii'))
    return 0


def move_bwd():
    ser.write('0001000\r\n'.encode('ascii'))
    return 0


def move_up():
    ser.write('0000100\r\n'.encode('ascii'))
    return 0


def move_down():
    ser.write('0000010\r\n'.encode('ascii'))
    return 0


def stop():
    ser.write('0000000\r\n'.encode('ascii'))
    return 0


def arm_drop():
    ser.write('0000000\r\n'.encode('ascii'))
    return 0


def arm_pick():
    ser.write('0000001\r\n'.encode('ascii'))
    return 0
