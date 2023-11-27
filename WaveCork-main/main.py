#Script to test circuit with many voltages/frequencies
import pyvisa
import time 
import agilent_visa_control.agilent as ag
import matplotlib.pyplot as plt
import numpy as np

#Global variables
b2902a = "TCPIP0::192.168.217.9::inst0::INSTR"
n9030a = "TCPIP0::169.254.52.33::hislip0::INSTR"

n_points = 1000

def main():
    print("[Starting connections]")
    
    rm = pyvisa.ResourceManager()
    res = rm.list_resources()

    for i in res:
        if i == b2902a:
            b2902a_inst = rm.open_resource(i)
            print("Found B2902A")
        if i == n9030a:
            n9030a_inst = rm.open_resource(i)
            print("Found N9030A")

    if not(b2902a_inst and n9030a_inst):
        raise Exception("Could not connect to devices")
    
    #Setup of arrays
    v_in_raw = [i for i in range(0,n_points,1)]
    v_in_prod = []
    v_out = []
    freq = []

    print("[Beginning program]")

    #Setting up B2902A
    b2902a_inst.write(":SYST:BEEP:STAT ON")
    b2902a_inst.write(":SYST:BEEP 200,1")
    b2902a_inst.write(":DISP:ENAB ON")
    b2902a_inst.write(":SENS:CURR:PROT 0.1") 

    #Using a for 
    b2902a_inst.write(":SOUR:FUNC:ALL")
    b2902a_inst.write(":SENS:FUNC VOLT (@1)")

    b2902a_inst.write(":SOUR:FUNC:MODE CURR (@2)")
    b2902a_inst.write(":SOUR:CURR 0 (@2)")

    b2902a_inst.write(":OUTP ON (@1)")
    b2902a_inst.write(":OUTP ON (@2)")

    #Setting up N9030A
    agilent = ag.Agilent(n9030a)
    agilent.open()
    agilent.set_sa()
    

    center_freq = ag.Frequency(2400, ag.FreqUnit(ag.FreqUnit.MHz))
    span = ag.Frequency(300, ag.FreqUnit(ag.FreqUnit.MHz))
    agilent.set_x(center_freq, span)

    for x in v_in_raw:
        b2902a_inst.write(str(":SOUR:VOLT " + str(x/100)))
        v_in_prod.append(b2902a_inst.query_ascii_values(":MEAS:VOLT? (@1)")[0])
        v_out.append(b2902a_inst.query_ascii_values(":MEAS:VOLT? (@2)")[0])
        
        trace = agilent.get_trace(1)
        max_db = max(trace)
        sa_points = agilent.get_points()[0]
        max_freq_pos = (trace.index(max_db))
        step_freq = 300 * 10**6 / sa_points
        max_freq = max_freq_pos * step_freq + 2100*10**6
        freq.append(max_freq)

        time.sleep(0.01)

        
    """
    #Sweep
    b2902a_inst.write(":SOUR:VOLT:MODE SWE")
    b2902a_inst.write(":SOUR:VOLT:START 1")
    b2902a_inst.write(":SOUR:VOLT:STOP 10")
    b2902a_inst.write(":SOUR:VOLT:POIN 100")

    #Sense
    b2902a_inst.write(":SENS:FUNC VOLT")

    #Triggers
    b2902a_inst.write(":TRIG:SOUR AINT")
    b2902a_inst.write(":TRIG:COUN 100")

    #Start
    b2902a_inst.write(":OUTP ON")
    b2902a_inst.write(":INIT (@1)")

    #Fetching data
    time.sleep(3)
    v_in_raw = (b2902a_inst.query_ascii_values(":FETC:ARR:VOLT? (@1)"))
    v_out = (b2902a_inst.query_ascii_values(":FETC:ARR:VOLT? (@2)"))
    print(v_in_raw)
    print(v_out)

    """

    b2902a_inst.write(":OUTP OFF")
    b2902a_inst.write(":SYST:BEEP 500,1")
    b2902a_inst.close()
    n9030a_inst.close()
    agilent.close()

    plt.plot(freq[20:-20], v_out[20:-20])
    plt.show()

    data = np.array((freq, v_out, v_in_raw, v_in_prod)).transpose()
    np.savetxt("data.csv", data, delimiter=";")

    print("[Program completed]")

if __name__ == "__main__":
    main()