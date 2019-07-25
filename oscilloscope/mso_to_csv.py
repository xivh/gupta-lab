# this works on the tektronix mso3014
import oscilloscope_backend_mso as ob # function definitions
print("Trying automatic setup...")
print("The oscilloscope should be the only connected device")
input("Press enter to continue")
tek = ob.automatic_setup()

while True:
    channel = input("Choose a channel or press enter for options: ")
    if not channel: # any option will work but channels and references are the most useful
        print("""Channels: CH1, CH2, CH3, CH4
                References: REF1, REF2, REF3, REF4
                Case doesn't matter
                Enter 'exit' to stop collecting""")
    elif channel == "exit":
        break
    else:
        destination = input("Choose a file destination or press enter for default: ")
        if not destination:
            ob.capture_waveform(tek, channel)

input("Press enter to close the program!")


