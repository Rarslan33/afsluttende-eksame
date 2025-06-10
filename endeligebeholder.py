import network
import ntptime
import time
from machine import Pin, PWM
import urequests

SSID = 'Galaxy A42 5G0C95'
PASSWORD = 'jhza3668'

def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print("🔌 Forbinder til Wi-Fi...")
        wlan.connect(SSID, PASSWORD)
        while not wlan.isconnected():
            time.sleep(1)
    print("✅ Wi-Fi tilsluttet:", wlan.ifconfig())

servo = PWM(Pin(14), freq=50)
led = Pin(4, Pin.OUT)

def set_angle(angle):
    min_duty = 26
    max_duty = 128
    duty = int(min_duty + (max_duty - min_duty) * angle / 180)
    servo.duty(duty)

sensor = Pin(32, Pin.IN, Pin.PULL_UP)

RECEIVER_IP = "192.168.43.190" 

def kør_servo():
    print("🏁 Starter servo-sekvens")
    angle = 0
    set_angle(angle)
    time.sleep(1)

    while angle < 80:
        angle += 0.5
        set_angle(angle)
        time.sleep(0.05)
        if sensor.value() == 1:
            print("📦 Objekt opdaget! Sender signal til modtager.")
            led.on()
            try:
                url = f"http://{RECEIVER_IP}/Pilletid"
                response = urequests.post(url, data="Pilletid")
                print("📨 Svar fra modtager:", response.text)
                response.close()
            except Exception as e:
                print("❌ Fejl ved sending:", e)
            
            time.sleep(2)
            led.off()
            break
            
    while angle > 0:
        angle -= 1
        set_angle(angle)
        time.sleep(0.05)

def main():
    connect_wifi()
    ntptime.settime()

    done_today = False

    while True:
        now = time.localtime()
        hour, minute, second = now[3], now[4], now[5]
        print("🕒 Tid nu: {:02d}:{:02d}:{:02d}".format(hour, minute, second))

        if hour == 08 and minute == 51 and not done_today:
            kør_servo()
            done_today = True
        elif hour != 05 or minute != 51:
            done_today = False

        time.sleep(1)

main()
