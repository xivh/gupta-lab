# wfmpre:<wfm>:<field>? -> wfmoutpre:<field>?
# doesn't require channel data and returns single value
import pathlib
from pathlib import Path as P
import sys
import visa as v

def automatic_setup():
    try:
        tek = v.ResourceManager().open_resource(v.ResourceManager().list_resources()[0])
        print(tek.query("*IDN?")) # should print tektronix and some other info
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

def capture_waveform(tek, channel, destination=None):
    if destination == None:
        destination = P.cwd().joinpath(channel + ".csv")
    else:
        destination = P.cwd().joinpath(destination + ".csv")
    tek.write("SELECT:" + channel + " ON")
    tek.write("DATA:SOURCE " + channel)
    tek.write("DATA:WIDTH 2")
    tek.write("DATA:START 1")
    tek.write("DATA:STOP 500000") # max length, won't cut off any waveforms
    waveform = tek.query_binary_values("CURVE?", datatype="h", is_big_endian=True)
    scaled_waveform = scale_waveform(tek, channel, waveform)
    with destination.open(mode="w") as output:
        for i in scaled_waveform:
            output.write(str(i[0]) + "," + str(i[1]) + "\n")

def scale_waveform(tek, channel, waveform): # returns the scaled y of the waveform as well as the x axis
    x_values = scale_x(tek)
    y_values = scale_y(tek, waveform)
    points = [[x_values[i], y_values[i]] for i in range(len(x_values))] # x, y points in a list
    return points

def scale_x(tek):
    xincr = float(tek.query("WFMOUTPRE:XINCR?"))
    pt_off = int(tek.query("WFMOUTPRE:PT_OFF?"))
    nr_pt = int(tek.query("WFMOUTPRE:NR_PT?"))
    scaled_x = [float(format(xincr * (i - pt_off), ".6g")) for i in range(nr_pt)] # cuts to 4 sig figs
    return scaled_x

def scale_y(tek, waveform):
    ymult = float(tek.query("WFMOUTPRE:YMULT?"))
    yoff = float(tek.query("WFMOUTPRE:YOFF?"))
    yzero = float(tek.query("WFMOUTPRE:YZERO?"))
    scaled_y = [float(format(yzero + ymult * (i - yoff), ".6g")) for i in waveform]
    return scaled_y
    
    
    
    
