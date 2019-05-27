# pbse intensity plotter
# some error handling
# paths should work on windows and linux
# variables are defined at the top of the program
# manual x scaling, automatic y scaling
import matplotlib.pyplot as plt
from numpy import genfromtxt, amin, amax, std
from pathlib import Path as P # wrap all paths with P for cross-compatability
import sys


### variables
# set image type
filetype = "png"

# set x range
xlim = True # False for full range
xmin = 0.24
xmax = 0.40

# set y range
ylim = True # False for automatic range
ymargin = 0.5 # margin = standard deviation * ymargin

###

# functions to format chart appearance

def process_filename(filename): # better names for legend
    if filename[filename.find("_") - 1] == "b":
        return "background"
    elif "Subtraction" in filename:
        return "subtraction result"
    else:
        return "sample"

def plot_line(x, y, label): # make sure colors are consistent
    color = ""
    if label == "background":
        color = "tab:gray"
    elif label == "subtraction result":
        color = "tab:red"
    else:
        color = "tab:orange"
    plt.plot(x, y, color = color, label = label, linewidth = 0.5)

# read in directories
root = input("Enter the root directory (default current): ")
savedir = input("Enter the directory to save to (default root/" + filetype + "s):" ) or filetype + "s"
directories = [i for i in P(root).iterdir() if i.is_dir()]

try:
    P(root + "/" + savedir).mkdir()
except:
    if P(root + "/" + savedir).is_dir():
        print("save directory already exists\n")
    else:
        print(P(root + "/" + savedir))
        print("error, exiting\n")
        exit()

for directory in directories: # iterate through directories
    files = [i for i in P(directory).iterdir() if i.suffix == ".CSV"]
    if xlim: # set x range
        plt.xlim(xmin, xmax)
    if ylim: # initialize y range
        ymax = -sys.maxsize
        ymin = sys.maxsize
        ystd = 0
    for filename in files: # iterate through files
        # read in data
        data = genfromtxt(P(filename), delimiter = ",")

        # create x and y
        x = []
        y = []
        for line in data:
            x.append(line[0] * 0.000124) # convert to eV
            y.append(line[1])

        # add line
        # plt.plot(x, y, label.split(".")[0])
        plot_line(x, y, process_filename(filename.name))
        if ylim & xlim: # only need to rescale if xlim was set
            visible_y = []
            for index, item in enumerate(y):
                if xmin <= x[index] <= xmax:
                    visible_y.append(item)
                if len(visible_y):
                    local_ymin = amin(visible_y)
                    local_ymax = amax(visible_y)
                    local_ystd = std(visible_y)
                    if local_ymin < ymin:
                        ymin = local_ymin
                    if local_ymax > ymax:
                        ymax = local_ymax
                    if local_ystd > ystd:
                        ystd = local_ystd
    if ylim & xlim: # rescale y if necessary
        ystd *= ymargin
        plt.ylim(ymin - ystd, ymax + ystd)

    # export plot
    if files: # ignore directory with no csvs
        plt.title(directory.name)
        plt.xlabel("energy (eV)")
        plt.ylabel("intensity (au)")
        plt.legend(loc = "upper right")
        #plt.tight_layout()
        plt.savefig(P(root + "/" + savedir + "/" + directory.name + "." + filetype), format = filetype, bbox_inches = "tight", dpi = 200)
        plt.clf()
