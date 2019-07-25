# pbse intensity plotter
# some error handling
# paths should work on windows and linux
# variables are defined at the top of the program
# manual x scaling, automatic y scaling
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
from numpy import genfromtxt, amin, amax, std
from pathlib import Path as P # wrap all paths with P for cross-compatability
import sys


### variables
# set image type
filetype = "png"

# set x range
xlim = True # False for full range
xmin = 0.26
xmax = 0.40

# set y range
auto_ylim = True # False for scaling based on full x range
ymargin = 0.5 # margin = standard deviation * ymargin, ignored if manual_ylim

# set these for manual y range (maybe after checking with auto_ylim = True?)
manual_ylim = False # don't forget to set auto_ylim = False if this is true
# ymin =
# ymax =

# set y axis precision
ytick = "%.2f"

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
    linewidth = 0.5
    alpha = 0.5
    if label == "background":
        color = "xkcd:greyish purple"
    elif label == "subtraction result":
        color = "xkcd:light orange"
        linewidth = 1.0
        alpha = 1.0
    else:
        color = "xkcd:cornflower blue"
    plt.plot(x, y, color = color, label = label, linewidth = linewidth, alpha = alpha)

# read in directories
root = P(input("Enter the root directory (default current): ")) or P.cwd()
savedir = input("Enter the directory to save to (default root/" + filetype + "s):" ) or filetype + "s"
savepath = root/savedir
directories = [i for i in P(root).iterdir() if i.is_dir()]

try:
    savepath.mkdir()
except:
    if savepath.is_dir():
        print(str(savepath.absolute()) + " already exists\n")
    else:
        print("error, exiting\n")
        input("")
        exit()

for directory in directories: # iterate through directories
    files = [i for i in P(directory).iterdir() if i.suffix.upper() == ".CSV"]
    if xlim: # set x range
        plt.xlim(xmin, xmax)
    if auto_ylim: # initialize y range
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
        # plt.plot(x, y, label = filename.name.split(".")[0])
        plot_line(x, y, process_filename(filename.name))
        if auto_ylim & xlim: # only need to rescale if xlim was set
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
    if auto_ylim & xlim: # rescale y if necessary
        ystd *= ymargin
        plt.ylim(ymin - ystd, ymax + ystd)

    if manual_ylim:
        plt.ylim(ymin, ymax)

    # export plot
    if files: # ignore directory with no csvs
        plt.gca().yaxis.set_major_formatter(mtick.FormatStrFormatter(ytick))
        plt.title(directory.name)
        plt.xlabel("energy (eV)")
        plt.ylabel("intensity (au)")
        plt.legend(loc = "upper right")
        #plt.tight_layout()
        #plt.savefig(P(str(savepath/directory.name) + "." + filetype), format = filetype, bbox_inches = "tight", dpi = 200)
        plt.savefig(str(savepath/directory.name) + "." + filetype, format = filetype, bbox_inches = "tight", dpi = 200) # python 3.4 + matplotlib path fix
        plt.clf()

input("Finished, press enter to exit!")
