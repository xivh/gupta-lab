# contains function definitions used elsewhere
# I wanted the main program to be simple
# the oscilloscope is defined as 'tek' because I used the tektronix tds784a for testing
import pathlib
from pathlib import Path as P
import sys
import visa as v
from decimal import Decimal

def automatic_setup():
    try:
        tek = v.ResourceManager().open_resource(v.ResourceManager().list_resources()[0])
        print(tek.query("*IDN?")) # should print tektronix and some other info
        print("Is this the right instrument?")
        correct = input("Press enter for yes or enter anything for no: ")
        if correct != "":
            raise ValueError("The wrong instrument connected!")
        return tek
    except:
        print("Automatic setup failed")
        print("Trying manual setup...")
        manual_setup()

def manual_setup():
    print("Listing resources...")
    print(v.ResourceManager().list_resources())
    instrument = input("Enter the full name of the desired instrument or press enter to exit: ")
    if not instrument:
        sys.exit()
    else:
        tek = v.ResourceManager().open_resource(instrument)
        return tek

def capture_waveform(tek, channel, destination):
    P.mkdir(P.cwd().joinpath("captures"), parents=True, exist_ok=True)
    if destination == "":
        destination = P.cwd().joinpath("captures", channel + ".csv")
    else:
        destination = P.cwd().joinpath("captures", destination + ".csv")
    tek.write("SELECT:" + channel + " ON")
    tek.write("DATA:SOURCE " + channel)
    tek.write("DATA:WIDTH 2")
    tek.write("DATA:START 1")
    tek.write("DATA:STOP 500000") # max length, won't cut off any waveforms
    waveform = tek.query_binary_values("CURVE?", datatype="h", is_big_endian=True)
    scaled_waveform = scale_waveform(tek, channel, waveform)
    tek.write("SELECT:" + channel + " OFF")
    with destination.open(mode="w") as output:
        for i in scaled_waveform:
            output.write(str(i[0]) + "," + str(i[1]) + "\n")

def scale_waveform(tek, channel, waveform): # returns the scaled y of the waveform as well as the x axis
    x_values = scale_x(tek, channel)
    y_values = scale_y(tek, channel, waveform)
    points = [[x_values[i], y_values[i]] for i in range(len(x_values))] # x, y points in a list
    return points

def scale_x(tek, channel):
    xincr = Decimal(tek.query("WFMPRE:" + channel + ":XINCR?").split()[1])
    pt_off = int(tek.query("WFMPRE:" + channel + ":PT_OFF?").split()[1])
    nr_pt = int(tek.query("WFMPRE:" + channel + ":NR_PT?").split()[1])
    scaled_x = [xincr * (i - pt_off) for i in range(nr_pt)]
    return scaled_x

def scale_y(tek, channel, waveform):
    ymult = Decimal(tek.query("WFMPRE:" + channel + ":YMULT?").split()[1])
    yoff = Decimal(tek.query("WFMPRE:" + channel + ":YOFF?").split()[1])
    yzero = Decimal(tek.query("WFMPRE:" + channel + ":YZERO?").split()[1])
    scaled_y = [yzero + ymult * (i - yoff) for i in waveform]
    return scaled_y
    
    
    
    
