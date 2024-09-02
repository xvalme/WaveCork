from machine import Pin, ADC, I2C
from time import sleep, localtime
import os
import gc
import micropython
import math

log_file = "log.txt"
running_file = "running.txt"
sweep_file = "sweep.csv"

temperature_led = Pin(3, Pin.OUT)
system_led  = Pin(2, Pin.OUT)
running_led = Pin(14 , Pin.OUT)
power_out = ADC(27)
temperature_adc  =ADC(26)

switch_1 = Pin(24, Pin.OUT)
switch_2 = Pin(25, Pin.OUT)

i2c_ports = {"scl" : Pin(9), "sda" : Pin(8), "freq" : 100000}

log_types = ["INFO", "WARNING", "ERROR", "DEBUG"]
reference_power = 0

LOG_SHUTDOWN = True

def create_files():
    found_running = 0

    try:
        # Try to open the file in read mode
        with open(log_file, 'r') as file:
            # If the file exists, print its contents
            print_and_log("INFO","Log file found...")

        with open(running_file, 'r') as file:
            found_running = 1

    except:
        # If the file does not exist, create it
        with open(log_file, 'w') as file:
            print_and_log("INFO","Creating log file...")

    if found_running:
        #Delete the running file
        os.remove(running_file)

        with open(running_file, 'w') as file:
            print_and_log("INFO","Creating running file...")

def toggle_temperture():
    if temperature_led.value() == 1:
        print_and_log("INFO", "Toggling temperature off...")
        temperature_led.value(0)
    else:
        print_and_log("INFO","Toggling temperature on...")
        temperature_led.value(1)

def print_and_log(type, message):
    log_message(type, message)

    if (LOG_SHUTDOWN == False):
        return

    if type == "INFO":
        print("\033[1;34m" + message + "\033[0m")
    elif type == "WARNING":
        print("\033[1;33m" + message + "\033[0m")
    elif type == "ERROR":
        print("\033[1;31m" + message + "\033[0m")
    elif type == "DEBUG":
        print("\033[1;34m" + message + "\033[0m")
    else:
        print(message)

def log_message(type, message):
    message  = str(message)
    year, month, day, hour, minute, second, weekday, yearday = localtime()
    date = "{0}-{1}-{2} {3}:{4}:{5}".format(year, month, day, hour, minute, second)
    if type not in log_types:
        print_and_log("ERROR","Invalid log type.")
        return
    with open(log_file, 'a') as file:
        file.write("[" + str(type) + "]" + str(date) + "|" + message + "\n")

def print_log():
    with open(log_file, 'r') as file:
        print(file.read())

def get_rf_power():
    reading = power_out.read_u16() / (2**16) * 3.3 - reference_power
    #print("RF Power: ", reading)
    log_message("INFO", "RF Power measured: " + str(reading))
    return reading

def get_temperature():
    reading = temperature_adc.read_u16() / 65535 * 3.3

    r = -100000 * reading / (reading - 1)

    temperature = [-40, -39, -38, -37, -36, -35, -34, -33, -32, -31, -30, -29, -28, -27, -26, -25, -24, -23, -22, -21, -20, -19, -18, -17, -16, -15, -14, -13, -12, -11, -10, -9, -8, -7, -6, -5, -4, -3, -2, -1, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40]
    resistance = [65839, 66264, 66692, 67122, 67556, 67993, 68432, 68874, 69319, 69767, 70218, 70672, 71128, 71588, 72050, 72515, 72983, 73454, 73928, 74405, 74885, 75367, 75853, 76341, 76833, 77327, 77824, 78324, 78827, 79333, 79842, 80353, 80868, 81385, 81906, 82429, 82956, 83485, 84017, 84552, 85090, 85631, 86175, 86722, 87272, 87825, 88380, 88939, 89501, 90065, 90633, 91203, 91777, 92354, 92933, 93515, 94101, 94689, 95281, 95875, 96472, 97073, 97676, 98282, 98892, 99504, 100119, 100738, 101359, 101984, 102611, 103241, 103875, 104511, 105151, 105793, 106439, 107087, 107739, 108393, 109051, 109712, 110376, 111042, 111712, 112385, 113061, 113740, 114422, 115107, 115796, 116487, 117181, 117879, 118579, 119283, 119990, 120699, 121412, 122128, 122847, 123570, 124295, 125023, 125755, 126489, 127227, 127968, 128712, 129459, 130209, 130962, 131719, 132478, 133241, 134007, 134776, 135548, 136324, 137102, 137884, 138668, 139456, 140248, 141042, 141839, 142640, 143444, 144251, 145061, 145874, 146691, 147511, 148334, 149160, 149989, 150822, 151657, 152496, 153339, 154184, 155033, 155885, 156740, 157598, 158460, 159324, 160192, 161064, 161938, 162816, 163697, 164582, 165469, 166360, 167254, 168151, 169052, 169956, 170863, 171774, 172688, 173605, 174525, 175449, 176376, 177306, 178240, 179177, 180117, 181061, 182008, 182958, 183912, 184869, 185829, 186792, 187759, 188730, 189703, 190680, 191661, 192645, 193632, 194622, 195616, 196613, 197614, 198618, 199625, 200636]
    temp_meas = 0

    #Try to find the nearest resistance

    for i in range(0, len(resistance)):
        if resistance[i] > r:
            if i == 0:
                r = temperature[0]
            else:
                r = temperature[i - 1]
                temp_meas = temperature[i-1]
            break

    print_and_log("INFO", "Temperature measured at startup: " + str(temp_meas))

def get_reference_power():
    res = get_rf_power()

    return res

def switch(way):
    if way == 1:
        print_and_log("INFO", "Switching to the PORT 1...")
        switch_1.value(1)
        switch_2.value(0)
    elif way == 2:
        print_and_log("INFO", "Switching to the PORT 2...")
        switch_1.value(0)
        switch_2.value(1)
    else:
        print_and_log("ERROR", "Invalid switch way.")

def i2c_setup(i2c):
    devices = i2c.scan()
    print_and_log("INFO", "I2C devices found: " + str(devices))

    #Should be 10011000 or 10010000 -> 152 or 144
    return devices[0]

def set_oscilator_frequency(i2c, device, frequency):

    #First make the conversion from frequency to voltage

    #TODO This is just a hotfix.

    '''freq = [
        2306193806, 2145554446, 2332567433, 2379320679, 2365534466, 2141958042, 
        2173126873, 2100599401, 2102397602, 2111988012, 2120979021, 2127572428, 
        2100000000, 2103896104, 2110489510, 2117382617, 2123376623, 2129670330, 
        2135964036, 2141958042, 2147652348, 2153346653, 2159340659, 2165034965, 
        2170429570, 2176123876, 2181518482, 2186913087, 2191708292, 2196803197, 
        2201598402, 2206393606, 2211188811, 2215984016, 2220479520, 2224975025, 
        2229170829, 2233666334, 2237862138, 2242057942, 2246253746, 2250149850, 
        2254045954, 2257942058, 2261838162, 2265734266, 2269630370, 2273226773, 
        2277122877, 2280719281, 2284615385, 2288211788, 2291808192, 2295404595, 
        2299300699, 2302597403, 2306193806, 2309790210, 2313386613, 2316683317, 
        2320279720, 2323576424, 2326873127, 2330169830, 2333766234, 2336763237, 
        2340059940, 2343056943, 2346353646, 2349350649, 2352347652, 2355644356, 
        2358641359, 2361338661, 2364335664, 2367332667, 2370329670, 2373326673, 
        2376023976, 2378721279, 2381718282, 2384415584, 2387112887, 2389810190, 
        2392507493, 2395204795, 2397602398, 2399700300, 2399700300, 2367332667, 
        2368531469, 2370929071, 2375724276, 2375724276, 2379320679, 2382317682, 
        2382917083, 2385914086, 2388311688, 2391908092
    ]

    vin = [
        0.0000165, 0.0999979, 0.1999996, 0.300001, 0.399998, 0.5, 
        0.600002, 0.700002, 0.799999, 0.899997, 1.000001, 1.1, 
        1.200001, 1.300002, 1.4, 1.500001, 1.6, 1.699998, 
        1.800001, 1.900001, 2, 2.1, 2.2, 2.3, 
        2.4, 2.5, 2.6, 2.7, 2.8, 2.9, 
        3, 3.1, 3.2, 3.3, 3.4, 3.5, 
        3.6, 3.7, 3.8, 3.9, 4, 4.1, 
        4.2, 4.29999, 4.4, 4.5, 4.6, 4.7, 
        4.8, 4.9, 5, 5.1, 5.2, 5.3, 
        5.4, 5.5, 5.6, 5.7, 5.8, 5.9, 
        6, 6.1, 6.2, 6.3, 6.4, 6.5, 
        6.6, 6.7, 6.8, 6.9, 7, 7.1, 
        7.2, 7.3, 7.4, 7.5, 7.6, 7.7, 
        7.8, 7.9, 8, 8.1, 8.2, 8.3, 
        8.4, 8.5, 8.6, 8.7, 8.8, 8.9, 
        9, 9.1, 9.2, 9.3, 9.39999, 9.5, 
        9.6, 9.7, 9.8, 9.9
    ]

    #First we try to find the closest frequency in freques to frequency

    #PRint min and max frequency available

    print_and_log("INFO", "Min frequency available: " + str(min(freq)/10**9) + "Hz.")
    print_and_log("INFO", "Max frequency available: " + str(max(freq)/10**9) + "Hz.")

    min_ = []

    for i in range(0, len(freq)):
        min_.append(abs(frequency - freq[i]))

    z = min_.index(min(min_))

    voltage = vin[z]
    '''

    if frequency < 2.11*10**9:
        print_and_log("ERROR", "Invalid frequency. Frequency must be between 2.11GHz and 2.55GHz.")
        return
    
    if frequency > 2.54*10**9:   
        print_and_log("ERROR", "Invalid frequency. Frequency must be between 2.11GHz and 2.55GHz.")
        return

    voltage = (- 0.0786 + math.sqrt(0.0786**2+4*0.0036*(2.118-frequency/10**9))) / (2*(-0.0036))
    #r^2 = 0.9945 with this 2nd order approximation

    v_ = voltage

    voltage = int((voltage) / 3.3 / 3 * 255)

    voltage = voltage & 0xFF

    # Split the voltage value into two nibbles
    X = voltage >> 4  # Higher nibble

    Y = voltage & 0x0F  # Lower nibble

    # Form the two bytes with the nibbles
    byte1 = X & 0x0F  
    byte2 = (Y << 4) | 0x0F  # 0x0C is the control byte for the DAC

    # Form the bytes array
    bytes_array = bytes([byte1, byte2])

    i = i2c.writeto(device, bytes_array)

    if (i != 2):
        print_and_log("ERROR", "Error setting the oscilator frequency. The DAC did not respond with sucess.")

    #print_and_log("INFO", "Voltage of RF generator set to: " + str(v_) + "V.") 

def set_oscillator_v (i2c, device, voltage):

    voltage = int((voltage) / 3.3 / 3 * 255)

    voltage = voltage & 0xFF

    # Split the voltage value into two nibbles
    X = voltage >> 4  # Higher nibble

    Y = voltage & 0x0F  # Lower nibble

    # Form the two bytes with the nibbles
    byte1 = X & 0x0F  
    byte2 = (Y << 4) | 0x0F  # 0x0C is the control byte for the DAC

    # Form the bytes array
    bytes_array = bytes([byte1, byte2])

    i = i2c.writeto(device, bytes_array)

    if (i != 2):
        print_and_log("ERROR", "Error setting the oscilator frequency. The DAC did not respond with sucess.")

def sweep(i2c, device, average=1, n_steps=100, verbose=False, start_freq = 2.11*10**9):
    #Clear the sweep file
    with open(sweep_file, 'w') as file:
        file.write("Frequency,Power\n")

    list_ = []

    '''
    440 steps from 2.11GHz to 2.55GHz so 440 steps of 1MHz
    2.55-2.11 = 0.44 GHz
    '''
    print_and_log("INFO", "Starting sweep...")
    print_and_log("INFO", "Bandwidth for each step is " + str(0.44*10**6/n_steps) + "KHz.")

    for i in range(0, n_steps):
        running_led.value(1)
        freq = start_freq + i*0.44*10**9/n_steps
        #freq = 2.25*10**9 + i*0.3*10**9/n_steps
        #freq = 2.38*10**9 + i*1000000
        set_oscilator_frequency(i2c, device, freq)
        #Avreage the power
        x = 0
        for p in range(0, average):
            x += get_rf_power()

        x = x / average

        list_.append(x)

        with open(sweep_file, 'a') as file:
            file.write(str(freq) + "," + str(x) + "\n")

        if verbose:
            print_and_log("INFO", "Average power for freq " + str(freq) + " is: " + str(x))
        running_led.value(0)

        if freq > 2.55*10**9:
            break

    #print max power

    print_and_log("INFO", "Sweep finished.")

def adaptative_sweep(i2c, device, average=1, n_steps=100, verbose=False, start_freq=2.11*10**9, end_freq=2.55*10**9, power_threshold=0.5, min_step=1e6):
    # Clear the sweep file
    with open(sweep_file, 'w') as file:
        file.write("Frequency,Power\n")

    list_ = []

    print_and_log("INFO", "Starting sweep...")

    freq = start_freq
    step_size = (end_freq - start_freq) / n_steps

    while freq <= end_freq:
        running_led.value(1)

        # Set oscillator frequency
        set_oscilator_frequency(i2c, device, freq)

        # Average the power readings
        power_sum = sum(get_rf_power() for _ in range(average))
        avg_power = power_sum / average

        list_.append(avg_power)

        with open(sweep_file, 'a') as file:
            file.write(f"{freq},{avg_power}\n")

        if verbose:
            print_and_log("INFO", f"Average power for freq {freq} is: {avg_power}")

        running_led.value(0)

        # Adjust step size based on the power reading
        if avg_power > power_threshold:
            # Decrease the step size when the signal is strong to get more points
            step_size = max(step_size / 2, min_step)
        elif avg_power < power_threshold:
            # Increase the step size when the signal is weak
            step_size = min(step_size * 2, (end_freq - start_freq) / n_steps)

        # Update frequency for next step
        freq += step_size

    print_and_log("INFO", "Sweep finished.")

'''def sweep(i2c, device, average=5, verbose=True):
    #Clear the sweep file
    with open(sweep_file, 'w') as file:
        file.write("Frequency,Power\n")

    for i in range(0, 100):
        running_led.value(1)

        set_oscillator_v(i2c, device, i/10)
        #Avreage the power
        x = 0
        for p in range(0, average):
            x += get_rf_power()

        x = x / average

        #with open(sweep_file, 'a') as file:
            #file.write(str(i/10) + "," + str(x) + "\n")

        if verbose:
            print("Average power for freq " + str(i/10) + " is: " + str(x))
        running_led.value(0)'''
      
def __main__():
    global reference_power

    #Initialization
    print("\033[1;32;40mDesigner Name: Valentino, 2024\033[0m")
    print("\033[1;32;40mSystem Name: CoHuMe\033[0m")
    print("\033[1;32;40mVersion: 1.0\033[0m")

    print_and_log("INFO" ,"Iniatializing system...")

    system_led.value(1)

    create_files()

    print_and_log("INFO","Oven controlled oscilator starting...")
    toggle_temperture()

    switch(2)

    #reference_power = get_reference_power()

    get_temperature()

    i2c = I2C(0, freq = i2c_ports["freq"], scl = i2c_ports["scl"], sda = i2c_ports["sda"])

    switch(1)
    i2c_device = i2c_setup(i2c)

    #set_oscilator_frequency(i2c, i2c_device, 2.182*10**9)

    #set_oscillator_v(i2c, i2c_device, 9.9)

    print("\033[1;32;40mSystem Initialized.\033[0m")

    sweep(i2c, i2c_device, average=3, n_steps=200, verbose=True)

    #set_oscillator_v(i2c, i2c_device, 3)

    '''while True:
        t = get_rf_power()
        print(t)
        sleep(1)'''

if __name__ == "__main__":
    __main__()