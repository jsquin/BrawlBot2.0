import cv2
from PIL import ImageGrab
import pyautogui as mouse
import PIL.Image, PIL.ImageTk
from tkinter import *
import random
import numpy as np

########### Misc File Functions ###########
def getlists():
    # Returns all lists
    return ReadList("legendwhitelist"), ReadList("legendblacklist"), ReadList("weaponwhitelist"), ReadList("weaponblacklist")

def ReadLegends():
    # Returns dict of legends
    legends = dict()
    with open("legends.txt", "r") as f:
        legendlist = f.readlines() 
        for legend in legendlist:
            temp = legend.split("|")
            temp[len(temp)-1] = temp[len(temp)-1][:-1]
            # TODO: Implement Default Loc
            legends[temp[0]] = Legend(temp[0], [int(temp[1]), int(temp[2]), int(temp[3]), int(temp[4])], [temp[5], temp[6]])
    return legends 

def WriteLegends(legends):
    # If legend stat is updated, writes to file 
    with open("legends.txt", "w") as f:
        for legend in legends:
            L = legends[legend]
            f.write(f"{L.name}|{L.attack}|{L.dexterity}|{L.defense}|{L.speed}|{L.weapons[0]}|{L.weapons[1]}\n")

def ReadList(path):
    # Reads a filter list text doc and returns list 
    with open(f"{path}.txt", "r") as f:
        line = f.readlines()
        if len(line) == 0:
            return [] 
        else:
            line = line[0]
        vals = line.split("|")
        vals = vals[:-1]
        return vals 
    
def WriteList(path, vals):
    # Writes a filter list to path
    with open(f"{path}.txt", "w") as f:
        for val in vals:
            f.write(f"{val}|")


########### Glorified List ########### 
class Legend:
    def __init__(self, name, stats, weapons, default_loc = None):
        if default_loc is None:
            default_loc = [0,0]
        self.name, self.weapons, self.default_loc = name, weapons, default_loc
        self.attack, self.dexterity, self.defense, self.speed = stats[0], stats[1], stats[2], stats[3] 


########### Global Variables ###########
current_legend = "random"
minimize = False
legendwhitelist, legendblacklist, weaponwhitelist, weaponblacklist = getlists()
legends = ReadLegends()
LWL, LBL, WWL, WBL, WWL_OR, WBL_OR = None, None, None, None, None, None
allweapons = {x.weapons[0] for x in legends.values()}.union({x.weapons[1] for x in legends.values()})
alllegends = [x.name for x in legends.values()]

########### Legend Selection Functions ###########
def SelectLegend(custom_filter):
    # Uses mouse to select random legend given filters.
    global current_legend, legends
    if minimize:
        win.state(newstate = "iconic")
    
    # Filter Legend Names 
    newkeys = []
    for legend in list(legends.values()):
        if custom_filter(legend):
            newkeys.append(legend.name)
    
    # Update GUI
    current_legend = random.choice(newkeys)
    update_image()

    # Select Legend
    findLegendImage()

def update_image():
    # Update GUI with current_legend
    global current_legend, label

    # Load Image 
    image = PIL.Image.open(f"icons/{current_legend}.png")

    # Resize Image to be close to 150x150
    min_ratio = min(150 / image.size[0], 150 / image.size[1])
    tempimage = image.resize((int(image.size[0] * min_ratio), int(image.size[1] * min_ratio)))

    # Load Image into PhotoImage object IDK why
    TEMP = PIL.ImageTk.PhotoImage(tempimage)

    # Update label
    label.configure(image = TEMP)
    label.image = TEMP

def SelectStat(stats, above, below):
    # TODO
    # all args should be lists
    # Selects random legend given stat requirement.
    if minimize:
        win.state(newstate = "iconic")

def EditLegend(name, stat, statval):
    # TODO
    # Edits stat of legend
    return None
    
def command_generator():
    # Returns a legend filter
    global LWL, LBL, WWL, WBL, WWL_OR, WBL_OR, legendwhitelist, legendblacklist, weaponwhitelist, weaponblacklist

    # Default Filters
    filter1, filter2, filter3, filter4 = lambda L: True, lambda L: True, lambda L: True, lambda L: True,

    # If checkbox, update filter
    if LWL.get() == 1:
        filter1 = lambda L: L.name in legendwhitelist 
    if LBL.get() == 1:
        filter2 = lambda L: L.name not in legendblacklist
    if WWL.get() == 1 and WWL_OR.get() == 1:
        filter3 = lambda L: L.weapons[0] in weaponwhitelist or L.weapons[1] in weaponwhitelist
    elif WWL.get() == 1 and WWL_OR.get() == 0:
        filter3 = lambda L: L.weapons[0] in weaponwhitelist and L.weapons[1] in weaponwhitelist
    if WBL.get() == 1 and WBL_OR.get() == 1:
        filter4 = lambda L: L.weapons[0] not in weaponblacklist or L.weapons[1] not in weaponblacklist
    elif WBL.get() == 1 and WBL_OR.get() == 0:
        filter4 = lambda L: L.weapons[0] not in weaponblacklist and L.weapons[1] not in weaponblacklist
    return lambda L: filter1(L) and filter2(L) and filter3(L) and filter4(L)

def findLegendImage():
    # Selects legend icon on screen
    # TODO: Fail case (default loc)
    #       Maybe check if max_val is too low
    #       Maybe check that mouse position is somewhere in proper box?
    # TODO: What if images are slightly different sized?
    global current_legend

    # Snapshot of screen and convert to grayscale
    screen = np.array(ImageGrab.grab())
    screen = cv2.cvtColor(src=screen, code=cv2.COLOR_BGR2GRAY)

    # Load current_legend icon as grayscale
    template = cv2.imread(f"icons/{current_legend}.PNG", 0)

    # Find match on screen of icon
    result = cv2.matchTemplate(screen, template, cv2.TM_CCOEFF)
    _, max_val, _, max_loc= cv2.minMaxLoc(result)

    # Reshape data
    height, width= template.shape[:2]
    top_left= max_loc
    bottom_right= (top_left[0] + width, top_left[1] + height)
    cv2.rectangle(screen, top_left, bottom_right, (0,0,255),5)

    # Position mouse and select legend
    mouse.moveTo((top_left[0] + bottom_right[0]) // 2, (top_left[1] + bottom_right[1])//2)
    mouse.click()
    mouse.click()

def MasterListEditor(input, output, edit_list, edit_type, add):
    # Edits (add / remove) master lists and displays on a label.
    # TODO: Surely there's a more elegant solution to this
    global alllegends, allweapons, legendwhitelist, legendblacklist, weaponwhitelist, weaponblacklist

    # Read from textbox
    input_val = input.get('1.0', 'end-1c').lower()

    # Determine which filter list to edit, then edits if possible
    if edit_type.get() == 0:
        if input_val not in alllegends:
            output.config(text = f"{input_val} is not a valid legend")
            return
        elif edit_list.get() == 0:
            if add and input_val not in legendwhitelist:
                legendwhitelist.append(input_val)
            if not add and input_val in legendwhitelist:
                legendwhitelist.remove(input_val)
            WriteList("legendwhitelist", legendwhitelist)
        else:
            if add and input_val not in legendblacklist:
                legendblacklist.append(input_val)
            if not add and input_val in legendblacklist:
                legendblacklist.remove(input_val)
            WriteList("legendblacklist", legendblacklist)
    else:
        if input_val not in allweapons:
            output.config(text = f"{input_val} is not a valid weapon")
            return
        elif edit_list.get() == 0:
            if add and input_val not in weaponwhitelist:
                weaponwhitelist.append(input_val)
            if not add and input_val in weaponwhitelist:
                weaponwhitelist.remove(input_val)
            WriteList("weaponwhitelist", weaponwhitelist)
        else:
            if add and input_val not in weaponblacklist:
                weaponblacklist.append(input_val)
            if not add and input_val in weaponblacklist:
                weaponblacklist.remove(input_val)
            WriteList("weaponblacklist", weaponblacklist)

    DisplayList(edit_list, edit_type, output)
    

def DisplayList(edit_list, edit_type, output):
    # Displays relevant filter list on some output label
    global legendwhitelist, legendblacklist, weaponwhitelist, weaponblacklist

    count = 0
    string = ""
    N = 60

    # Determine which filter list to use
    if edit_list.get() == 0: 
        if edit_type.get() == 0:
            vals = legendwhitelist
        else:
            vals = weaponwhitelist
    else:
        if edit_type.get() == 0:
            vals = legendblacklist
        else:
            vals = weaponblacklist

    # Make sure display string isn't off the screen
    for val in vals:
        string += f"| {val} |"
        count += len(val) + 5
        if count > N:
            count = 0
            string += "\n"

    output.config(text = string)


def EditWindow():
    # Opens temporary window to edit filter lists

    # New Tkinter window as 400 x 300 with slightly offset padding
    win2 = Tk() 
    win2.geometry("400x300+580+590")
    win2.title("Filter Editor")

    # Initialize Toggleables after Tk() declaration
    edit_list, edit_type = IntVar(win2), IntVar(win2)

    # Text Box for any displays
    labelmain = Label(win2, text = "", font=("Arial", 12))
    labelmain.place(relx = 0.5, rely = 0.12, anchor = CENTER)

    # Input Text Box for changing filters
    textBox = Text(win2,height=1,width=40)
    textBox.place(relx = 0.1, rely = 0.69) # Nice

    # Radiobuttons for selecting Lists
    R2 = Radiobutton(win2, text = "Blacklist", variable = edit_list, value = 1)
    R2.place(relx = 0.33, rely = 0.49, anchor = CENTER)
    R1 = Radiobutton(win2, text = "Whitelist", variable = edit_list, value = 0)
    R1.place(relx = 0.33, rely = 0.42, anchor = CENTER)

    # Radiobuttons for selecting weapon/legend 
    R4 = Radiobutton(win2, text = "Weapon", variable = edit_type, value = 1)
    R4.place(relx = 0.66, rely = 0.49, anchor = CENTER) 
    R3 = Radiobutton(win2, text = "Legend", variable = edit_type, value = 0)
    R3.place(relx = 0.66, rely = 0.42, anchor = CENTER)

    # Button to display current list
    B0 = Button(win2, text = "Display", command = lambda: DisplayList(edit_list, edit_type, labelmain))
    B0.place(relx = 0.5, rely = 0.6, anchor = CENTER)

    # Add and Remove buttons
    B1 = Button(win2, text = "Add", command = lambda: MasterListEditor(textBox, labelmain, edit_list, edit_type, True))
    B1.place(relx = 0.4, rely = 0.8, anchor = CENTER)
    B2 = Button(win2, text = " Remove ", command = lambda: MasterListEditor(textBox, labelmain, edit_list, edit_type, False))
    B2.place(relx = 0.6, rely = 0.8, anchor = CENTER)

    win2.mainloop()


########### MAIN ###########
    # TODO: Remove from "main()" function after testing completed
    # TODO: On init, take a screenshot of the menu and index all legends? 
    #       That way, no need to use cv2 for every search?
    #       But How many times would you even use in a single session?
    #       Alternatively: Every time a legend is searched, add location to a dict if successful.
    # TODO: Add checking that relevant files exist
    # TODO: Implement default location.
    # Known Bugs:
    #           Jaeyun doesn't work
    #           Different image sizes don't work (offline)
if __name__ == "__main__":

    # Initialize Tkinter window as 400x300 with padding of 600x600
    win = Tk()
    win.geometry("400x300+600+600")
    win.title("Brawl Randomizer")

    # Have to initialize all togglables after Tk() declaration.
    LWL, LBL, WWL, WBL, WWL_OR, WBL_OR = IntVar(), IntVar(), IntVar(), IntVar(), IntVar(), IntVar()

    # Initialize frame for icon display
    frame = Frame(win, width = 200, height = 200)
    frame.place(anchor = "center", relx = 0.5, rely = 0.6)

    # Checkboxes for filter toggles
    c1 = Checkbutton(win, text = "Whitelist Legends", variable = LWL, onvalue = 1, offvalue = 0)
    c1.place(relx = 0.15, rely = 0.05, anchor = CENTER)
    c2 = Checkbutton(win, text = "Blacklist Legends", variable = LBL, onvalue = 1, offvalue = 0)
    c2.place(relx = 0.15, rely = 0.15, anchor = CENTER)
    c3 = Checkbutton(win, text = "Whitelist Weapons", variable = WWL, onvalue = 1, offvalue = 0)
    c3.place(relx = 0.45, rely = 0.05, anchor = CENTER)
    c4 = Checkbutton(win, text = "Blacklist Weapons", variable = WBL, onvalue = 1, offvalue = 0)
    c4.place(relx = 0.45, rely = 0.15, anchor = CENTER)
    c5 = Checkbutton(win, text = "Whitelist Weapons OR", variable = WWL_OR, onvalue = 1, offvalue = 0)
    c5.place(relx = 0.8, rely = 0.05, anchor = CENTER)
    c6 = Checkbutton(win, text = "Blacklist Weapons OR", variable = WBL_OR, onvalue = 1, offvalue = 0)
    c6.place(relx = 0.8, rely = 0.15, anchor = CENTER)

    # Select Button
    B = Button(win, text = "Select", command = lambda: SelectLegend(command_generator()))
    B.place(relx = 0.5, rely = 0.3, anchor = CENTER)

    # Edit Files Button
    B2 = Button(win, text = "Edit", command = EditWindow)
    B2.place(relx = 0.5, rely = 0.9, anchor = CENTER)
    
    # Initilze Icon Image into frame. Default is random
    image = PIL.Image.open("icons/random.png")
    min_ratio = min(150 / image.size[0], 150 / image.size[1])
    image = image.resize((int(image.size[0] * min_ratio), int(image.size[1] * min_ratio)))
    img = PIL.ImageTk.PhotoImage(image)

    label = Label(frame, image = img) 
    label.pack() 

    win.mainloop()