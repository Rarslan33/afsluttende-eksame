from machine import Pin, PWM, SoftI2C
import network
import socket
import ntptime
import time
import urequests
from MPU6050 import MPU6050


ssid = 'Galaxy A42 5G0C95'
password = 'jhza3668'

sta = network.WLAN(network.STA_IF)
sta.active(True)
sta.connect(ssid, password)

while not sta.isconnected():
    time.sleep(0.3)

print("✅ Connected to Wi-Fi")
ip = sta.ifconfig()[0]
print("📡 IP address:", ip)

ntptime.settime()

led = Pin(2, Pin.OUT)
buzzer_pin = Pin(25)
buzzer = PWM(buzzer_pin)
buzzer.deinit() 
buzzer_active = False

i2c = SoftI2C(scl=Pin(22), sda=Pin(21))
mpu = MPU6050()
fall_threshold = 1.2 * 9.8
receiver_ip = "192.168.43.161" 

timezone_offset = 2

last_fall_sent = 0
fall_cooldown = 2 

addr = socket.getaddrinfo("0.0.0.0", 80)[0][-1]
server_socket = socket.socket()
server_socket.bind(addr)
server_socket.listen(1)
server_socket.settimeout(0.05) 

def check_for_led_command():
    try:
        cl, _ = server_socket.accept()
        request = cl.recv(1024).decode()

        if "/Pilletid" in request:
            print("💡 LED trigger received!")
            led.on()

        cl.send("HTTP/1.0 200 OK\r\n\r\nReceived")
        cl.close()

    except:
        pass 

while True:
    check_for_led_command()

    now = time.localtime(time.time() + timezone_offset * 3600)
    hour, minute, second = now[3], now[4], now[5]
    print(f"🕒 Time: {hour:02d}:{minute:02d}:{second:02d}")

    if hour == 12 and minute == 58 and second == 0 and not buzzer_active:
        buzzer = PWM(buzzer_pin)
        buzzer.freq(1000)
        buzzer.duty(100)
        buzzer_active = True
        print("🔊 Buzzer ON")

    elif hour == 12 and minute == 58 and second == 0 and buzzer_active:
        buzzer.duty(0)
        buzzer.deinit()
        buzzer_active = False
        print("🔇 Buzzer OFF")

    accel = mpu.read_accel_data(g=False)
    total = (accel["x"]**2 + accel["y"]**2 + accel["z"]**2) ** 0.5
    print("📈 Accel:", round(total, 2), "m/s²")

    now_sec = time.time()
    if total > fall_threshold and now_sec - last_fall_sent > fall_cooldown:
        print("⚠️ Fall detected – sending alert")
        try:
            urequests.get(f"http://{receiver_ip}/fall")
        except:
            print("❌ Failed to send alert")
        last_fall_sent = now_sec

    time.sleep(1)