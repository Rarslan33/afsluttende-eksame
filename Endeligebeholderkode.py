from machine import Pin, ADC, PWM, SoftI2C
import dht
import ssd1306
import time

# Pin-konfiguration
dht_sensor = dht.DHT11(Pin(4))  # DHT11 tilsluttet GPIO4
IN1 = PWM(Pin(16), freq=1000)   # H-bro IN1 på GPIO16
IN2 = PWM(Pin(17), freq=1000)   # H-bro IN2 på GPIO17

# OLED-konfiguration
i2c = SoftI2C(scl=Pin(22), sda=Pin(21))  # I2C på GPIO22 og GPIO21
oled = ssd1306.SSD1306_I2C(128, 64, i2c)

# Funktioner til Peltier-styring
def køl():
    IN1.duty(1023)  # Maksimal køling
    IN2.duty(0)

def varm():
    IN1.duty(0)     # Maksimal opvarmning
    IN2.duty(1023)

def stop():
    IN1.duty(0)     # Stop Peltier
    IN2.duty(0)

# Temperaturgrænser
min_temp = 25  # Minimum temperatur
max_temp = 30 # Maksimum temperatur

# Hovedprogram
while True:
    try:
        # Mål temperatur med DHT11
        dht_sensor.measure()
        temp = dht_sensor.temperature()

        # Tjek temperatur og styr Peltier-element
        if temp < min_temp:
            varm()
        elif temp > max_temp:
            køl()
        else:
            stop()

        # Opdater OLED-skærm
        oled.fill(0)  # Ryd skærmen
        oled.text("Temp: {}C".format(temp), 0, 0)
        if temp < min_temp:
            oled.text("Opvarmning...", 0, 20)
        elif temp > max_temp:
            oled.text("Koeler...", 0, 20)
        else:
            oled.text("Stabil.", 0, 20)
        oled.show()

        time.sleep(1)  # Opdatering hvert sekund

    except Exception as e:
        print("Fejl: ", e)
        oled.fill(0)
        oled.text("Fejl: {}".format(str(e)), 0, 0)
        oled.show()
        time.sleep(5)