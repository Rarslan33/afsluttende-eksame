import socket
from machine import Pin, SoftI2C
import ssd1306
import time
import network

i2c = SoftI2C(scl=Pin(22), sda=Pin(21))
oled = ssd1306.SSD1306_I2C(128, 64, i2c)

current_y = 0

ssid = 'Galaxy A42 5G0C95'
password = 'jhza3668'
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(ssid, password)

print("Connecting to WiFi...", end="")
while not wlan.isconnected():
    print(".", end="")
    time.sleep(0.5)
print("\nConnected!")
print("IP address:", wlan.ifconfig()[0])

def show_alert():
    global current_y

    if current_y > 54:
        oled.fill(0)
        current_y = 0

    oled.text("⚠ FALL DETECTED!", 0, current_y)
    oled.show()
    current_y += 10 

def clear_oled():
    oled.fill(0)
    oled.show()

def start_server():
    addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]
    s = socket.socket()
    s.bind(addr)
    s.listen(1)

    print("🖥️ Waiting for connection on port 80...")

    while True:
        cl, addr = s.accept()
        print('📥 Client connected from', addr)
        request = cl.recv(1024)
        request_str = request.decode()

        if "fall" in request_str:
            print("⚠️ FALL DETECTED!")
            show_alert()


        cl.send("HTTP/1.0 200 OK\r\nContent-Type: text/plain\r\n\r\nReceived")
        cl.close()

start_server()
