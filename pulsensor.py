from machine import ADC, Pin
import time

adc = ADC(Pin(34))
adc.atten(ADC.ATTN_11DB)

threshold = 2222
last_beat_time = 0
bpm_list = []

print("Place finger on sensor...")

while True:
    value = adc.read()
    now = time.ticks_ms()

    if value > threshold and (now - last_beat_time) > 300:
        beat_interval = (now - last_beat_time) / 1000 
        bpm = 60 / beat_interval
        bpm_list.append(bpm)

        if len(bpm_list) > 10:
            bpm_list.pop(0)

        avg_bpm = sum(bpm_list) / len(bpm_list)
        print("BPM:", round(avg_bpm, 1))

        last_beat_time = now

    time.sleep(0.01)


