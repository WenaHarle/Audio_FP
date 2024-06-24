import serial
import time
import random

def send_serial_data():
    # Open the serial port
    ser = serial.Serial('/dev/ttyUSB0', 115200, timeout=1)
    
    # Give some time to establish the connection
    time.sleep(0.01)
    
    # Data to be sent
    data = "0"
    
    # Send the data
    ser.write(data.encode())
    
    # Close the serial port

    ser.close()

if __name__ == "__main__":
    send_serial_data()
