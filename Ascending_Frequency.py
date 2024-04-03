## Ascending Frequency 2.1

## Author: Patrick Kontopidis ©2024

import time
import numpy as np
import pyaudio
import matplotlib.pyplot as plt

import csv

# Parallelization
import concurrent.futures

# Arduino
import pyfirmata2

# Mouse click
import pyautogui

def play(output_bytes, p, fs):
    #Synchro mit Arduino
    #time.sleep(5)
    stream_play = p.open(format=pyaudio.paFloat32,
                    channels=1,
                    rate=fs,
                    output_device_index=0,
                    output=True)
    
    stream_play.write(output_bytes)

    stream_play.stop_stream()
    stream_play.close()

def rec(p, duration, fs):
    #Synchro mit Arduino
    #time.sleep(5)
    Recordframes = []

    stream_rec = p.open(format=pyaudio.paInt16,
                channels=1,
                rate=fs,
                input=True,
                input_device_index=1,
                frames_per_buffer=512)
    
    for k in range(0, int(fs / 512 * (duration-2.0))):
        input_data = stream_rec.read(512, exception_on_overflow=False)
        input_array = np.frombuffer(input_data, dtype=np.int16)
        Recordframes.append(input_array)

    stream_rec.stop_stream()
    stream_rec.close()

    return Recordframes

def motor(i, pin_d_3_step, pin_d_2_dir): 

    steps_1 = 500
    steps_2 = 125
    g = 0
    j = 0

    dauer = steps_1 -35#+ 50

    #delay = 1/steps_1

    if i%2 ==0: 
        pin_d_2_dir.write(0)
    else:
        pin_d_2_dir.write(1)

    for k in range(dauer): 
        # Ramp Start: 

        if j <= steps_1-steps_2: 
            delay = 1/(steps_2+j)
            j = j + 5

        # Ramp Stop: 
        elif g <= steps_1-steps_2 and k>= dauer-75: 
            delay = 1/(steps_1-g)
            g = g + 5
        else:
            delay = 1/(steps_1)

        pin_d_3_step.write(1)
        time.sleep(delay)
        pin_d_3_step.write(0)
        time.sleep(delay)

def measure(arduino_port, saveto, **kwargs):
    
    p = pyaudio.PyAudio()

    fs = kwargs.get('fs', 44100)

    volume = kwargs.get('volume', 0.5)
    
    duration = kwargs.get('duration', 5.7)

    Hz_steps = kwargs.get('hz_steps', 5)

    upper_f = kwargs.get('upper_f', 2000)

    lower_f = kwargs.get('lower_f', 250)

    runs = kwargs.get('runs', 5)

    discrete = np.arange(fs * (duration-2.0)) / fs

    board = pyfirmata2.Arduino(arduino_port)

    pin_d_3_step = board.get_pin('d:5:o')
    pin_d_2_dir = board.get_pin('d:4:o')

    total_measurements = int((upper_f-lower_f)/Hz_steps)

    for k in range(1, runs+1):
        all_data = []
        for i in range(total_measurements): 

            f = lower_f + (i*Hz_steps)

            sin = np.sin(2*np.pi*f*discrete)

            samples = sin.astype(np.float32)

            output_bytes = (volume * samples).tobytes()

            with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
                # Submit each function to run concurrently
                future1 = executor.submit(play, output_bytes, p, fs)
                future2 = executor.submit(rec, p, duration, fs)
                future3 = executor.submit(motor, i, pin_d_3_step, pin_d_2_dir)

                # Wait for both futures to complete
                concurrent.futures.wait([future1, future2, future3])

                # Get the results
                #result1 = future1.result()
                Recordframes = future2.result()

                all_data.append(np.array(Recordframes).flatten())
            
            #play(output_bytes)

            #Recordframes = rec()

            print(str(f)+" Hz")

            # Mouse click
            if(i%20==0): 
                x, y = pyautogui.position()
                pyautogui.click(x, y)

        csv_path = saveto+str(k)+'.csv'

        # Save csv Data
        with open(csv_path, 'w', newline='') as csvfile:
            csv_writer = csv.writer(csvfile)
            
            csv_writer.writerows(all_data)

    p.terminate()

    return all_data

def drive_cable(arduino_port, **kwargs): 
    
    board = pyfirmata2.Arduino(arduino_port)

    pin_d_3_step = board.get_pin('d:5:o')
    pin_d_2_dir = board.get_pin('d:4:o')

    steps = kwargs.get('steps', 200)
    delay = kwargs.get('delay', 1/200)

    if dir == 0 or dir == 1: 
        dir = kwargs.get('direction', 1)
    else: 
        raise ValueError('direction must be 0 or 1')

    try: 
        # andere Richtung: 0 
        # Impedanzrohr: 1 = hoch, 0 = runter
        pin_d_2_dir.write(dir)
        for i in range(40):
            for _ in range(steps): 
                pin_d_3_step.write(1)
                time.sleep(delay)
                pin_d_3_step.write(0)
                time.sleep(delay)

    except KeyboardInterrupt:

        board.exit()

def check_audio_devices(): 
    if __name__ == "__main__":
        p = pyaudio.PyAudio()
        device_count = p.get_device_count()

        print("List of audio devices:")
        for i in range(device_count):
            device_info = p.get_device_info_by_index(i)
            device_name = device_info['name']
            print(f"Device {i}: {device_name}")

        p.terminate()