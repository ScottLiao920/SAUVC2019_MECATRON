import serial
import time

ser = serial.Serial(
    port='/dev/ttyUSB0',# Change port
    baudrate=115200,
    parity=serial.PARITY_ODD,
    stopbits=serial.STOPBITS_ONE,
    bytesize=serial.SEVENBITS
)

while True:
    binary_input = input("input 8 bit binary >> ")
    if binary_input == "exit":
        ser.close()
        exit()
    else:
        #string_value = str(int(binary_input, base=2))
        ser.write((binary_input + '\r\n').encode('ascii'))
        if ser.is_open:
            print("open")
        time.sleep(1)

