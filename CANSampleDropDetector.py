from ast import excepthandler
import tkinter
from tkinter import Label, Text, Toplevel, filedialog
from tkinter.constants import END
from tkinter.ttk import Progressbar
from tkinter import ttk
import time
import datetime


# main launch window
mainWindow = tkinter.Tk()

# rows and columns configuration
mainWindow.columnconfigure(0, weight=10)
mainWindow.columnconfigure(1, weight=10)
mainWindow.columnconfigure(2, weight=1)
mainWindow.columnconfigure(3, weight=10)
mainWindow.columnconfigure(4, weight=10)
mainWindow.rowconfigure(0, weight=1)
mainWindow.rowconfigure(1, weight=1)
mainWindow.rowconfigure(2, weight=0)
mainWindow.rowconfigure(3, weight=200)
mainWindow.rowconfigure(4, weight=1)

# File type selection title
optionFrame = tkinter.LabelFrame(mainWindow, text="File type")
optionFrame.grid(row=3, column=0, sticky='nw')

# Radio button default to position 1 (asc)
rbValue = tkinter.IntVar()
rbValue.set(1)

# asc and trc radio button creation and configuration
asc_button = tkinter.Radiobutton(optionFrame, text="ASC file", value=1, variable=rbValue )
trc_button_v1 = tkinter.Radiobutton(optionFrame, text="TRC file (V1.1)", value=2, variable=rbValue)
asc_button.grid(row=0, column=0, sticky='nw')
trc_button_v1.grid(row=1, column=0, sticky='nw')
# trc_button_v2 = tkinter.Radiobutton(optionFrame, text="TRC file (V2.0)", value=3, variable=rbValue)
# trc_button_v2.grid(row=2, column=0, sticky='nw')

# Main window title annd geometry
mainWindow.title("CAN sample drop Detector")
mainWindow.geometry("720x340+600+300")
mainWindow['padx'] = 8

# Results title and configuration
rightLabel = tkinter.Label(mainWindow, text="Results")
rightLabel.grid(row=0, column=2, sticky='s')

# File input title and configuration
fileInputTitle = tkinter.Label(mainWindow, text="File input")
fileInputTitle.grid(row=0, column=0, sticky='sw')

def path():
    """
    Once `Browse` is pressed, the radio button value will be retrieved.
    With this, the entry widget will have its contents deleted and a search directory will pop up.
    This will show files that end in the file extension selected via the radio buttons.
    When the file is selected, it will diplay the directory in the Entry widget.
    """
    selection = rbValue.get()
    if selection == 1:
        fileInputName.delete(0, END)
        directory_path = filedialog.askopenfilename(
            title="Browse", filetypes=(("ASC", "*.asc"), ("text files", "*.txt"), ("all files", "*.*")))
        tkinter.Entry.insert(fileInputName, 0, directory_path)
    elif selection == 2:
        fileInputName.delete(0, END)
        directory_path = filedialog.askopenfilename(
            title="Browse", filetypes=(("TRC", "*.trc"), ("text files", "*.txt"), ("all files", "*.*")))
        tkinter.Entry.insert(fileInputName, 0, directory_path)
    # elif selection == 3:
    #     fileInputName.delete(0, END)
    #     directory_path = filedialog.askopenfilename(
    #         title="Search", filetypes=(("TRC", "*.trc"), ("text files", "*.txt"), ("all files", "*.*")))
    #     tkinter.Entry.insert(fileInputName, 0, directory_path)

# Search button configuration
browseButton = tkinter.Button(mainWindow, text="Browse", command=path)
browseButton.grid(row=1, column=1, sticky='nw')

# Entry widget configuration
fileInputName = tkinter.Entry(mainWindow, textvariable=path)
fileInputName.grid(row=1, column=0, sticky='ew')


# Process when inserting .asc files
def asc_can():
    """
    Processes of looking through a .asc file to determine the number of missing samples, 
    duplicate samples, missing CAN messages, duplicate CAN messages, and time jumps.
    """
    # Pop up progess bar window configuration
    teams = range(10)
    popup = tkinter.Toplevel()
    popup.geometry("+960+470")
    tkinter.Label(popup, text="Loading, please wait").grid(row=0, column=0)
    # Pop up progress bar configuration
    progress = 0
    progress_var = tkinter.DoubleVar()
    progress_bar = ttk.Progressbar(popup, variable=progress_var, maximum=10)
    progress_bar.grid(row=1, column=0)
    popup.pack_slaves()
    # Progress bar animation
    progress_step = float(10.0/len(teams))
    for team in teams:
        popup.update()
        time.sleep(1)
        progress += progress_step
        progress_var.set(progress)
    # Retrieves directory from the Entry Widget
    file = tkinter.Entry.get(fileInputName)
    # Global variables
    missing_lines = []
    duplicates = []
    bit_ID = []
    keys = []
    results_list = []
    backwards_jump = []
    missingUTC = []
    duplicateUTC = []
    first_bit_count = 0
    key = 1
    key_count = 1
    line_num = 0
    last_second = 0
    UTC_Sample_count = 0
    start_time = 0
    # Opens the entire file
    with open(file, 'r') as f:
        lines = f.readlines() # TODO change to readline to make it quicker
    # Iterate over each line to determine each unique CAN ID until they all have been appended.
    for i in lines:
        if "Rx   d 8" in i:
            if i[15:18] not in bit_ID:
                bit_ID.append(i[15:18])
            else:
                break
    # For the length of CAN ID's create a value starting at 1. Append to a list.
    while key < (len(bit_ID) + 1):
        keys.append(key)
        key += 1
    # creation of a dictionary using the CAN ID's and key values. 
    bit_ID_dict = dict(zip(keys, bit_ID))
    # using the first CAN ID, find the sample rate
    for j in lines:
        if j[15:18] == bit_ID_dict.get(1):
            first_bit_count += 1
            if 0.99980 < float(j[3:11]) < 1.000200:
                sample_rate = f"Sample rate: {first_bit_count - 1}Hz"
                results_list.append(sample_rate)
                break
    # Main code to check for missing/duplicate data. 
    for line in lines:
        # line count
        line_num += 1
        # check for invalid lines
        if "Rx" not in line:
            continue
        # reset key count for CAN ID's when the last value is reached
        if key_count == len(bit_ID) + 1:
            key_count = 1
        if "Rx" in line:
            # Check if relevant CAN ID is in the line, if yes, add 1 to key count
            if bit_ID_dict.get(key_count) in line[13:31].upper():
                key_count += 1
                # Check if the CAN ID is a value of 301
                if "Rx" in line and "301 " in line[11:31]:
                    # sample count
                    UTC_Sample_count += 1
                    # retrieving and converting the seconds to UTC bits
                    allBits = line[:39:-1]
                    allBits_slice = allBits[13:21]
                    UTC_Bits = allBits_slice[::-1]
                    bitsJoin = UTC_Bits.replace(" ", "")
                    UTCSeconds = int(bitsJoin, 16)
                    if line[39:37:-1] == '00':
                        continue
                    # if it is the first UTC value, use it as the start time
                    if last_second == 0 and line[39:37:-1] != '00':
                        last_second = UTCSeconds
                        start_time = datetime.timedelta(seconds=(last_second*0.01))
                    # check for a duplicate
                    elif UTCSeconds == last_second:
                        duplicateUTC.append(line_num)
                    # check for time jumps
                    elif UTCSeconds < last_second:
                        backwards_jump.append(line_num)
                        last_second = UTCSeconds
                    # check to see if time has incremented correctly
                    elif UTCSeconds == last_second + 1:
                        last_second = UTCSeconds
                    else:
                        # missing time sample
                        missingUTC.append(line_num)
                        # using the current key value append the missing CAN channels
                        UTC_missing = [line_num] * (len(bit_ID) - key_count)
                        for num in UTC_missing:
                            missing_lines.append(num)
                        UTC_missing = []
                        last_second += 2
                        # True loop to check if checked UTC matches the next value
                        while True:
                            if UTCSeconds == last_second:
                                last_second = UTCSeconds
                                break
                            if "Rx   d 8" not in line:
                                line_num += 1
                                continue
                            else:
                                missingUTC.append(line_num)
                                UTC_missing = [line_num] * len(bit_ID)
                                for num in UTC_missing:
                                    missing_lines.append(num)
                                UTC_missing = []
                                last_second += 1
            # Check if the CAN ID is a duplicate
            elif key_count - 1 == 0:
                dup2 = line
                if bit_ID_dict.get(len(bit_ID)) in line[13:31]:
                    if dup1 == dup2:
                        duplicates.append(line_num)
                        line_num += 1
                    else:
                        line_num += 1
            elif bit_ID_dict.get(key_count - 1) in line[13:31].upper():
                dup2 = line
                if dup1 == dup2:
                    duplicates.append(line_num)
                    line_num += 1
                else:
                    line_num += 1
            else:
                # Append missing CAN ID
                missing_lines.append(line_num)
                key_count += 1
                if key_count == len(bit_ID) + 1:
                    key_count = 1
                # Check if next CAN ID is correct
                while True:
                    if key_count == len(bit_ID) + 1:
                        key_count = 1
                    if "Rx   d 8" not in line:
                        line_num += 1
                        continue
                    if bit_ID_dict.get(key_count) in line[13:31]:
                        key_count += 1
                        break
                    else:
                        missing_lines.append(line_num)
                        key_count += 1
        dup1 = line
    # last 301 ID is used for end time
    end_time = datetime.timedelta(seconds=(last_second*0.01))

    # Number of different replies that will be appended to the results list to be printed
    results_list = []
    results_list.append(f"Start time: {start_time}")
    results_list.append(f"End time: {end_time}")
    results_list.append(f"Duration: {end_time - start_time}")
    results_list.append(sample_rate)
    total_lines = len(lines) - 4
    r1 = "\nTotal number of sent messages: {:,}".format(total_lines)
    results_list.append(r1)
    r2 = "Number of samples: {:,}".format(UTC_Sample_count)
    results_list.append(r2)

    if not missingUTC:
        r3 = "\nThere are no missing samples"
        results_list.append(r3)
    else:
        if len(missingUTC) == 1:
            r4 = f"\nThere is 1 sample missing, {round((1/UTC_Sample_count), 3)}% of all the samples"
            results_list.append(r4)
            r5 = "The sample is missing between the following lines:"
            results_list.append(r5)
        else:
            r6 = "\nThere are {:,} samples missing, {}% of all the samples".format(
                (len(missingUTC)), round((len(missingUTC)/UTC_Sample_count) * 100, 3))
            results_list.append(r6)
            r7 = "Samples are missing are between the following lines:"
            results_list.append(r7)
        for UTCdata in sorted(set(missingUTC)):
            r8 = "{:,} - {:,}".format(UTCdata, (UTCdata - len(bit_ID)))
            results_list.append(r8)

    if not duplicateUTC:
        r9 = "\nThere are no duplicate samples"
        results_list.append(r9)
    else:
        if len(duplicateUTC) == 1:
            r10 = f"\nThere is 1 duplicate sample, {round((1/UTC_Sample_count), 3)}% of all the samples"
            results_list.append(r10)
            r11 = "The sample is duplicated on the following line:"
            results_list.append(r11)
        else:
            r12 = "\nThere are {:,} duplicate samples, {}% of all the samples".format(
                len(duplicateUTC), round((len(duplicateUTC)/UTC_Sample_count) * 100, 3))
            results_list.append(r12)
            r13 = "The duplicate samples are on the following lines:"
            results_list.append(r13)
        for value in sorted(set(duplicateUTC)):
            r14 = "{:,}".format(value)
            results_list.append(r14)

    if backwards_jump:
        for back in backwards_jump:
            r15 = "\nTime went back on line {:,}".format(back)
        results_list.append(r15)

    if not missing_lines:
        r16 = "\nThere are no missing CAN messages"
        results_list.append(r16)
    else:
        if len(missing_lines) == 1:
            r17 = f"\nThere is 1 sample CAN message, {round((1/UTC_Sample_count), 3)}% of all messages"
            results_list.append(r17)
            r18 = "The missing CAN message is on following line:"
            results_list.append(r18)
        else:
            r19 = "\nThere are {:,} CAN messages missing, {}% of all messages".format(
                len(missing_lines), round((len(missing_lines)/(len(lines) - 4)) * 100, 3))
            results_list.append(r19)
            r20 = "CAN messages are missing are between the following lines:"
            results_list.append(r20)
        for line_data in sorted(set(missing_lines)):
            r21 = "{:,}".format(line_data)
            results_list.append(r21)

    if not duplicates:
        r22 = "\nThere are no duplicate CAN message"
        results_list.append(r22)
    else:
        if len(duplicates) == 1:
            r23 = f"\nThere is 1 duplicate CAN message, {round((1/UTC_Sample_count), 3)}% of all messages"
            results_list.append(r23)
            r24 = "The CAN message is duplicated on the following line:"
            results_list.append(r24)
        else:
            r25 = "\nThere are {:,} duplicate CAN messages, {}% of all messages".format
            (len(duplicates), round((len(duplicates)/(len(lines) - 4)) * 100, 3))
            results_list.append(r25)
            r26 = "The duplicate CAN messages are on the following lines:"
            results_list.append(r26)
        for duplicate_data in sorted(set(duplicates)):
            r27 = "{:,}".format(duplicate_data)
            results_list.append(r27)

    # Configuration for the text box that will have all the relevant replies printed.
    results = tkinter.Text(mainWindow, height=18, width=60)
    results.grid(row=1, column=2, sticky='ne', rowspan=3)
    results.config(border=2, relief='sunken')
    # Scroll back configuration
    resultsScroll = tkinter.Scrollbar(mainWindow, orient=tkinter.VERTICAL, command=results.yview)
    resultsScroll.grid(row=1, column=3, sticky='nsw', rowspan=3)
    results['yscrollcommand'] = resultsScroll.set
    # printing the results list to the text box
    for i in results_list:
        results.insert(END, i + '\n')
    # when printed destroy the loading bar
    tkinter.Toplevel.destroy(popup)


def trc_can_v1():
    """
    Process of looking through a .trc file to deteremine the number of missing samples,
    duplicate samples, missing CAN messages, duplicate CAN messages, and time jumps.
    """
    # Pop up progress bar window configuration
    teams = range(10)
    popup = tkinter.Toplevel()
    popup.geometry("+960+470")
    tkinter.Label(popup, text="Loading, please wait").grid(row=0, column=0)
    # Pop up progress bar configuration
    progress = 0
    progress_var = tkinter.DoubleVar()
    progress_bar = ttk.Progressbar(popup, variable=progress_var, maximum=10)
    progress_bar.grid(row=1, column=0)
    popup.pack_slaves()
    # Progress bar animation
    progress_step = float(10.0/len(teams))
    for team in teams:
        popup.update()
        time.sleep(1)
        progress += progress_step
        progress_var.set(progress)
    # Retrieve directory from the Entry Widget
    file = tkinter.Entry.get(fileInputName)
    # Global variables
    missing_lines = []
    duplicates = []
    bit_ID = []
    keys = []
    results_list = []
    backwards_jump = []
    missingUTC = []
    duplicateUTC = []
    first_bit_count = 0
    key = 1
    key_count = 1
    line_num = 0
    last_second = 0
    UTC_Sample_count = 0
    # Opens the entire file
    with open(file, 'r') as f:
        lines = f.readlines()   # TODO change to readline to make it quicker
    # Iterate over each line to determine each unique CAN ID until they all have been appended
    for k in lines:
        if "Rx" in k:
            if k[32:36] not in bit_ID:
                bit_ID.append(k[32:36])
            else:
                break
    # For the length of CAN ID's create a value starting at 1. Append to a list  
    while key < (len(bit_ID) + 1):
        keys.append(key)
        key += 1
    # creation of a dictionary using the CAN ID's and key values
    bit_ID_dict = dict(zip(keys, bit_ID))
    # using the first CAN ID, find the sample rate
    for j in lines:
        if j[32:36] == bit_ID_dict.get(1):
            first_bit_count += 1
            if 999.5 < float(j[13:19]) < 1000.5:
                sample_rate = f"Sample rate: {first_bit_count - 1}Hz"
                results_list.append(sample_rate)
                break
    # Main code to check for missing/duplicate data
    for line in lines:
        # line count
        line_num += 1
        # check for invalid lines
        if "x " not in line:
            continue
        # reset key count for CAN ID's when the last value is reached
        if key_count == len(bit_ID) + 1:
            key_count = 1
        if "x " in line:
            # Check if relevant CAN ID is in the line, if yes, add 1 to key count
            if bit_ID_dict.get(key_count) in line[23:41]:
                key_count += 1
                # Check if the CAN ID is a value of 301
                if "x " and "0301 " in line:
                    # sample count
                    UTC_Sample_count += 1
                    # retrieving and coverting the UTC bits to seconds
                    allBits = line[:37:-1]
                    allBits_slice = allBits[14:22]
                    UTC_Bits = allBits_slice[::-1]
                    bitsJoin = UTC_Bits.replace(" ", "")
                    UTCSeconds = int(bitsJoin, 16)
                    # if it is the first UTC value, use it as the start time
                    if last_second == 0:
                        last_second = UTCSeconds
                        start_time = datetime.timedelta(seconds=(last_second * 0.01))
                        # check for a duplicate
                    elif UTCSeconds == last_second:
                        duplicates.append(line_num)
                        # check for time jumps
                    elif UTCSeconds < last_second:
                        backwards_jump.append(line_num)
                        last_second = UTCSeconds
                        # check to see if time has incrememted correctly
                    elif UTCSeconds == last_second + 1:
                        last_second = UTCSeconds
                    else:
                        # append missing time sample line number 
                        missingUTC.append(line_num)
                        # using the current key value, append the missing CAN channels
                        UTC_missing = [line_num] * (len(bit_ID) - key_count)
                        for num in UTC_missing:
                            missing_lines.append(num)
                        UTC_missing = []
                        last_second += 2
                        # True loop to check if checked UTC matches the next value
                        while True:
                            if UTCSeconds == last_second:
                                last_second = UTCSeconds
                                break
                            if "x " not in line:
                                line_num += 1
                                continue
                            else:
                                missingUTC.append(line_num)
                                UTC_missing = [line_num] * len(bit_ID)
                                for num in UTC_missing:
                                    missing_lines.append(num)
                                UTC_missing = []
                                last_second += 1
            # Check if the CAN ID is a duplicate
            elif key_count - 1 == 0:
                dup2 = line
                if bit_ID_dict.get(len(bit_ID)) in line[23:41]:
                    if dup1 == dup2:
                        duplicates.append(line_num)
                        line_num += 1
                    else:
                        line_num += 1
            elif bit_ID_dict.get(key_count - 1) in line[23:41]:
                dup2 = line
                if dup1 == dup2:
                    duplicates.append(line_num)
                    line_num += 1
                else:
                    line_num += 1
            else:
                # Append missing CAN ID
                missing_lines.append(line_num)
                key_count += 1
                if key_count == len(bit_ID) + 1:
                    key_count = 1
                # Check if next CAN ID is correct
                while True:
                    if key_count == len(bit_ID) + 1:
                        key_count = 1
                    if "x " not in line:
                        line_num += 1
                        continue
                    if bit_ID_dict.get(key_count) in line[23:41]:
                        key_count += 1
                        break
                    else:
                        missing_lines.append(line_num)
                        key_count += 1
        dup1 = line
    # last 301 ID is used as end time
    end_time = datetime.timedelta(seconds=(last_second*0.01))

    # Number of different replies that will be appended to the results to be printed
    results_list = []
    try:
        results_list.append(f"Start time: {start_time}")
    except:
        pass
    try:
        results_list.append(f"End time: {end_time}")
    except:
        pass
    try:
        results_list.append(f"Duration: {end_time - start_time}")
    except:
        pass
    try:
        results_list.append(sample_rate)
    except:
        pass
    total_lines = len(lines) - 17
    r1 = "\nTotal number of sent messages: {:,}".format(total_lines)
    results_list.append(r1)
    r2 = "Number of samples: {:,}".format(UTC_Sample_count)
    results_list.append(r2)

    if not missingUTC:
        r3 = "\nThere are no missing samples"
        results_list.append(r3)
    else:
        if len(missingUTC) == 1:
            r4 = f"\nThere is 1 sample missing, {round((1/(UTC_Sample_count + len(missingUTC))), 3) * 100}% of all the samples"
            results_list.append(r4)
            r5 = "The sample is missing between the following lines:"
            results_list.append(r5)
        else:
            r6 = "\nThere are {:,} samples missing, {}% of all the samples".format(
                len(missingUTC), round((len(missingUTC)/(UTC_Sample_count + len(missingUTC))), 3) * 100)
            results_list.append(r6)
            r7 = "Samples are missing are between the following lines:"
            results_list.append(r7)
        for UTCdata in sorted(set(missingUTC)):
            r8 = "{:,} - {:,}".format(UTCdata, (UTCdata - len(bit_ID)))
            results_list.append(r8)

    if not duplicateUTC:
        r9 = "\nThere are no duplicate samples"
        results_list.append(r9)
    else:
        if len(duplicateUTC) == 1:
            r10 = f"\nThere is 1 duplicate sample, {round((1/UTC_Sample_count), 3) * 100}% of all the samples"
            results_list.append(r10)
            r11 = "The sample is duplicated on the following line:"
            results_list.append(r11)
        else:
            r12 = "\nThere are {:,} duplicate samples, {}% of all the samples".format(
                len(duplicateUTC), round((len(duplicateUTC)/UTC_Sample_count), 3) * 100)
            results_list.append(r12)
            r13 = "The duplicate samples are on the following lines:"
            results_list.append(r13)
        for value in sorted(set(duplicateUTC)):
            r14 = "{:,}".format(value)
            results_list.append(r14)

    if backwards_jump:
        for back in backwards_jump:
            r15 = "\nTime went back on line {:,}".format(back)
        results_list.append(r15)

    if not missing_lines:
        r16 = "\nThere are no missing CAN messages"
        results_list.append(r16)
    else:
        if len(missing_lines) == 1:
            r17 = f"\nThere is 1 sample CAN message, {round((1/len(lines) - 17), 3) * 100}% of all messages"
            results_list.append(r17)
            r18 = "The missing CAN message is on following line:"
            results_list.append(r18)
        else:
            r19 = "\nThere are {:,} CAN messages missing, {}% of all messages".format(
                len(missing_lines), round((len(missing_lines)/(len(lines) - 17)), 3) * 100)
            results_list.append(r19)
            r20 = "CAN messages are missing are between the following lines:"
            results_list.append(r20)
        for line_data in sorted(set(missing_lines)):
            r21 = "{:,}".format(line_data)
            results_list.append(r21)

    if not duplicates:
        r22 = "\nThere are no duplicate CAN message"
        results_list.append(r22)
    else:
        if len(duplicates) == 1:
            r23 = f"\nThere is 1 duplicate CAN message, {round((1/len(lines) - 17), 3) * 100}% of all messages"
            results_list.append(r23)
            r24 = "The CAN message is duplicated on the following line:"
            results_list.append(r24)
        else:
            r25 = "\nThere are {:,} duplicate CAN messages, {}% of all messages".format(
                len(duplicates), round((len(duplicates)/len(lines) - 17), 3) * 100)
            results_list.append(r25)
            r26 = "The duplicate CAN messages are on the following lines:"
            results_list.append(r26)
        for duplicate_data in sorted(set(duplicates)):
            r27 = "{:,}".format(duplicate_data)
            results_list.append(r27)
    #Configuration for the text box that will have all the relevant replies printed
    results = tkinter.Text(mainWindow, height=18, width=60)
    results.grid(row=1, column=2, sticky='ne', rowspan=3)
    results.config(border=2, relief='sunken')
    # scroll bar configuration
    resultsScroll = tkinter.Scrollbar(mainWindow, orient=tkinter.VERTICAL, command=results.yview)
    resultsScroll.grid(row=1, column=3, sticky='nsw', rowspan=3)
    results['yscrollcommand'] = resultsScroll.set
    # printing the results list to the text box
    for i in results_list:
        results.insert(END, i + '\n')
    # when printed destry the loading bar
    tkinter.Toplevel.destroy(popup)


def can_selection():
    """
    Run the correct function depending on which radio button is pressed
    """
    file_selection = rbValue.get()
    if file_selection == 1:
        asc_can()
    elif file_selection == 2:
        trc_can_v1()


# Text box configuration
results = tkinter.Text(mainWindow, height=18, width=60)
results.grid(row=1, column=2, sticky='ne', rowspan=3)
results.config(border=2, relief='sunken')
#Scroll bar configuration
resultsScroll = tkinter.Scrollbar(mainWindow, orient=tkinter.VERTICAL, command=results.yview)
resultsScroll.grid(row=1, column=3, sticky='nsw', rowspan=3)
results['yscrollcommand'] = resultsScroll.set
# run button configuration
runButton = tkinter.Button(mainWindow, text="Run", command=can_selection)
runButton.grid(row=2, column=0, sticky='nw')
# run main window
mainWindow.mainloop()
