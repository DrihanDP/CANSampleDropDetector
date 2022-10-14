import tkinter
import datetime
from tkinter import END, filedialog

mainWindow = tkinter.Tk()

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

mainWindow.title("CAN sample drop Detector")
mainWindow.geometry("720x340+600+300")
mainWindow['padx'] = 8

rightLabel = tkinter.Label(mainWindow, text="Results")
rightLabel.grid(row=0, column=2, sticky='s')

fileInputTitle = tkinter.Label(mainWindow, text="File input")
fileInputTitle.grid(row=0, column=0, sticky='sw')

def path():
    fileInputName.delete(0, tkinter.END)
    directory_path = filedialog.askopenfilename(
        title="Search", filetypes=(("ASC", "*.asc"), ("TRC", "*.trc"),("text files", "*.txt"), ("all files", "*.*")))
    tkinter.Entry.insert(fileInputName, 0, directory_path)

browseButton = tkinter.Button(mainWindow, text="Browse", command=path)
browseButton.grid(row=1, column=1, sticky='nw')

fileInputName = tkinter.Entry(mainWindow, textvariable=path)
fileInputName.grid(row=1, column=0, sticky='ew')


def main():
    top = tkinter.Toplevel(mainWindow)
    top.geometry("+960+470")
    tkinter.Label(top, text="Loading, please wait").grid(row=0, column=0)

    file_input = tkinter.Entry.get(fileInputName)
    data_collection = open(file_input, 'r')
    data_line = data_collection.readline()

    if file_input.endswith(".asc"):
        print("ASC")
    elif file_input.endswith(".trc"):
        print("TRC")
    else:
        pass
    
    class GV():
        bit_ID = []
        keys = []
        backwards_jump = []
        missingUTC = []
        missing_lines = []
        duplicateUTC = []
        duplicateCAN = []
        key = 1
        key_count = 0
        line_num = 0
        UTC_Sample_count = 0
        start_time = 0
        initialList = []
        _301List = []
        firstSat = False
        last_second = 0

    # with open(file_input, 'r') as file: # TODO edit to add
    #     for line in file:

    # Load and open the file
    file = open(file_input, 'r')
    line = file.readline()


    def mising_check():
        if key_count == len(GV.bit_ID):
            key_count = 0
        if "Rx" in line:
            key_count += 1
            if "Rx" and "301" in line[13:31] and line[40:42] == '00':
                pass
            elif "Rx" and "301" in line[11:31]:
                GV.UTC_Sample_count += 1
                timeBits = line[50:42:-1]
                UTC_bits = timeBits[::-1].replace(" ", "")
                UTCSeconds = int(UTC_bits, 16)
                if GV.start_time == 0:
                    GV.start_time = datetime.timedelta(seconds=(UTCSeconds * 0.01))
                    GV.last_second = UTCSeconds
                elif UTCSeconds == GV.last_second:
                    GV.duplicateUTC.append(GV.line_num)
                elif UTCSeconds < GV.last_second:
                    GV.backwards_jump.append(GV.line_num)
                    GV.last_second = UTCSeconds
                elif UTCSeconds == GV.last_second + 1:
                    GV.last_second = UTCSeconds
                else:
                    GV.missingUTC.append(GV.line_num)
                    GV.last_second += 2
                    while True:
                        if UTCSeconds == GV.last_second:
                            GV.last_second = UTCSeconds
                            break
                        if "Rx" not in line:
                            GV.line_num += 1
                        else:
                            GV.missingUTC.append(GV.line_num)
                            GV.last_second += 1
            elif str(bit_ID_dict.get(key_count)) in line[13:31]:
                pass
            elif line == previous_line:
                GV.duplicateCAN.append(GV.line_num)
                key_count -= 1
            else:
                GV.missing_lines.append(GV.line_num)
                while True:
                    key_count += 1
                    if key_count == len(GV.bit_ID) + 1:
                        key_count = 1
                    if "Rx" not in line:
                        GV.line_num += 1
                        continue
                    if str(bit_ID_dict.get(key_count)) in line[13:31]:
                        break
                    else:
                        GV.missing_lines.append(GV.line_num)

        previous_line = line
        # line = file.readline()

    while line:
        # storing the first 11000 lines in order to calculate the sample rate and to create a dict of CAN IDs
        # without having to open and close the file multiple times
        while len(GV.initialList) < 11000:
            GV.initialList.append(line)
            line = file.readline()
        for data_line in GV.initialList:
            if "Rx" in data_line:
                # splitting the line into a list of strings while deleting the blank spaces
                splitLine = [x for x in data_line.split(" ") if x != ""]
                if splitLine[2] == "301":
                    if splitLine[6] != "00":
                        if len(GV._301List) == 0:
                            GV._301List.append(tuple(splitLine[7:10]))
                            startBit = "".join(splitLine[7:10]) 
                            firstDeci = int(startBit, 16)
                        elif len(GV._301List) < 100:
                            GV._301List.append(tuple(splitLine[7:10]))
                        elif len(GV._301List) == 100:
                            lastBit = "".join(splitLine[7:10])
                            lastDeci = int(lastBit, 16)
                            break
                        else:
                            continue
            if "Rx" not in line:
                continue
        # determining the sample rate
        UTCDiff = lastDeci - firstDeci
        if UTCDiff == 100:
            sample_rate = "Sample rate: 100Hz"
        elif UTCDiff == 200:
            sample_rate = "Sample rate: 50Hz"
        elif UTCDiff == 500:
            sample_rate = "Sample rate: 20Hz"
        elif UTCDiff == 1000:
            sample_rate = "Sample rate: 10Hz"
        elif UTCDiff == 2000:
            sample_rate = "Sample rate: 5Hz"
        elif UTCDiff == 10000:
            sample_rate = "Sample rate: 1Hz"

        for i in GV.initialList:
            lineList = [x for x in i.split(" ") if x != ""]
            if "Rx" not in lineList:
                continue
            elif lineList[2] not in GV.bit_ID:
                GV.bit_ID.append(lineList[2])
            else:
                break

        while GV.key < len(GV.bit_ID) + 1:
            GV.keys.append(GV.key)
            GV.key += 1

        bit_ID_dict = dict(zip(GV.keys, GV.bit_ID))

        while GV.initialList:
            for data in GV.initialList:
                GV.line_num += 1
                splitLine = [x for x in data.split(" ") if x != ""]
                if splitLine[2] == "301" and firstSat == False:
                    if splitLine[6] == "00" and firstSat == False:
                        continue
                    else: 
                        firstSat = True
                elif splitLine[2] == "301" and firstSat == True:
                    
    
    end_time = datetime.timedelta(seconds=(GV.last_second*0.01))

    results_list = []
    results_list.append(f"Start time: {GV.start_time}")
    results_list.append(f"End time: {GV.end_time}")
    results_list.append(f"Duration: {GV.end_time - GV.start_time}")
    results_list.append(sample_rate)
    total_lines = GV.line_num - 4
    r1 = "\nTotal number of sent messages: {:,}".format(total_lines)
    results_list.append(r1)
    r2 = "Number of samples: {:,}".format(GV.UTC_Sample_count)
    results_list.append(r2)

    if not GV.missingUTC:
        r3 = "\nThere are no missing samples"
        results_list.append(r3)
    else:
        if len(GV.missingUTC) == 1:
            r4 = f"\nThere is 1 sample missing, {round((1/GV.UTC_Sample_count), 3)}% of all the samples"
            results_list.append(r4)
            r5 = "The sample is missing between the following lines:"
            results_list.append(r5)
        else:
            r6 = "\nThere are {:,} samples missing, {}% of all the samples".format(
                (len(GV.missingUTC)), round((len(GV.missingUTC)/GV.UTC_Sample_count) * 100, 3))
            results_list.append(r6)
            r7 = "Samples are missing are between the following lines:"
            results_list.append(r7)
        for UTCdata in sorted(set(GV.missingUTC)):
            r8 = "{:,} - {:,}".format(UTCdata, (UTCdata - len(GV.bit_ID)))
            results_list.append(r8)

    if not GV.duplicateUTC:
        r9 = "\nThere are no duplicate samples"
        results_list.append(r9)
    else:
        if len(GV.duplicateUTC) == 1:
            r10 = f"\nThere is 1 duplicate sample, {round((1/GV.UTC_Sample_count), 3)}% of all the samples"
            results_list.append(r10)
            r11 = "The sample is duplicated on the following line:"
            results_list.append(r11)
        else:
            r12 = "\nThere are {:,} duplicate samples, {}% of all the samples".format(
                len(GV.duplicateUTC), round((len(GV.duplicateUTC)/GV.UTC_Sample_count) * 100, 3))
            results_list.append(r12)
            r13 = "The duplicate samples are on the following lines:"
            results_list.append(r13)
        for value in sorted(set(GV.duplicateUTC)):
            r14 = "{:,}".format(value)
            results_list.append(r14)

    if GV.backwards_jump:
        for back in GV.backwards_jump:
            r15 = "\nTime went back on line {:,}".format(back)
        results_list.append(r15)

    if not GV.missing_lines:
        r16 = "\nThere are no missing CAN messages"
        results_list.append(r16)
    else:
        if len(GV.missing_lines) == 1:
            r17 = f"\nThere is 1 sample CAN message, {round((1/GV.UTC_Sample_count), 3)}% of all messages"
            results_list.append(r17)
            r18 = "The missing CAN message is on following line:"
            results_list.append(r18)
        else:
            r19 = "\nThere are {:,} CAN messages missing, {}% of all messages".format(
                len(GV.missing_lines), round((len(GV.missing_lines)/(len(GV.line_num) - 4)) * 100, 3))
            results_list.append(r19)
            r20 = "CAN messages are missing are between the following lines:"
            results_list.append(r20)
        for line_data in sorted(set(GV.missing_lines)):
            r21 = "{:,}".format(line_data)
            results_list.append(r21)

    if not GV.duplicateCAN:
        r22 = "\nThere are no duplicate CAN message"
        results_list.append(r22)
    else:
        if len(GV.duplicateCAN) == 1:
            r23 = f"\nThere is 1 duplicate CAN message, {round((1/GV.UTC_Sample_count), 3)}% of all messages"
            results_list.append(r23)
            r24 = "The CAN message is duplicated on the following line:"
            results_list.append(r24)
        else:
            r25 = "\nThere are {:,} duplicate CAN messages, {}% of all messages".format
            (len(GV.duplicateCAN), round((len(GV.duplicateCAN)/(GV.line_num - 4)) * 100, 3))
            results_list.append(r25)
            r26 = "The duplicate CAN messages are on the following lines:"
            results_list.append(r26)
        for duplicate_data in sorted(set(GV.duplicateUTC)):
            r27 = "{:,}".format(duplicate_data)
            results_list.append(r27)

    results = tkinter.Text(mainWindow, height=18, width=60)
    results.grid(row=1, column=2, sticky='ne', rowspan=3)
    results.config(border=2, relief='sunken')

    resultsScroll = tkinter.Scrollbar(mainWindow, orient=tkinter.VERTICAL, command=results.yview)
    resultsScroll.grid(row=1, column=3, sticky='nsw', rowspan=3)
    results['yscrollcommand'] = resultsScroll.set

    for i in results_list:
        results.insert(END, i + '\n')

    tkinter.Toplevel.destroy(top)

    file.close()    

results = tkinter.Text(mainWindow, height=18, width=60)
results.grid(row=1, column=2, sticky='ne', rowspan=3)
results.config(border=2, relief='sunken')
resultsScroll = tkinter.Scrollbar(mainWindow, orient=tkinter.VERTICAL, command=results.yview)
resultsScroll.grid(row=1, column=3, sticky='nsw', rowspan=3)
results['yscrollcommand'] = resultsScroll.set
runButton = tkinter.Button(mainWindow, text="Run", command=main)
runButton.grid(row=2, column=0, sticky='nw')
mainWindow.mainloop()



# R:\Dumping ground\DDP\Python\can message\Actual can data.txt
# Z:\Python\can message\Test files\Converted_Log1.asc
# Z:\Python\can message\Test files 3\Converted_Log_merged.asc
# P:\Testing\Projects\VB3iS\Test Files\Omega\Omega recordings\01 Converted_PCAN_USBBUS1_1.trc_19112021-1249_Merge.asc
# P:\Testing\Projects\VB3iS\Test Files\VB3i SD\1.2 b9337 Ken's cupbaord Test 2 with KF\Converted_PCAN_USBBUS1_1.trc_09122021-1537_Merge.asc

# line1 = line.split(" ").remove("")
