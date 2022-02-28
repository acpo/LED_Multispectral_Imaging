# Original code from Pineda, D., Pérez, J.C., Gaviria, D., Ospino-Villalba, K.S. and Camargo, O., 2022. MEDUSA: An open-source and webcam based multispectral imaging system. HardwareX, p.e00282.
# -*- coding: utf-8 -*-
"""
Medusa control program
Author: Daniel Mauricio Pineda
Last modification: 13042021
Code version: 1.91
Description: Software for controlling the multispectral camera, Medusa on PC
"""

# Required libraries
import numpy as np
import time, serial, cv2
import tkinter as tk
from functools import partial

# Creating the main window 
window = tk.Tk()
window.title("MEDUSA G V1.91 (BETA) - Plantopía, UNAL")
window.resizable(0, 0)
window.geometry("470x195")


########################################################################
###################### Global important variables ##################
# Camera resolution
resX = 1280
resY = 720
# Port number
availablePorts = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14]
# Available band names. Can be changed according to the specific setup
wavelengthStr = ["419nm", "446nm", "470nm", "502nm", "533nm", "592nm",\
		"632nm", "660nm", "723nm", "769nm", "858nm", "880nm",\
                   "950nm", "NOT", "WHT"]
                   
# These are the specific bands as variables
L419 = tk.IntVar()
L446 = tk.IntVar()
L470 = tk.IntVar()
L502 = tk.IntVar()
L533 = tk.IntVar()
L592 = tk.IntVar()
L632 = tk.IntVar()
L660 = tk.IntVar()
L723 = tk.IntVar()
L769 = tk.IntVar()
L858 = tk.IntVar()
L880 = tk.IntVar()
L950 = tk.IntVar()
LNOT = tk.IntVar()
LBLA = tk.IntVar()

# It is convenient to have them on an array
wavelength = [L419, L446, L470, L502, L533, L592, L632, L660, L723, L769,\
                    L858, L880, L950, LNOT, LBLA]
                    
# The white LED is assigned to port 14, however, this also depends on the specific setup
white = 14

# ser will later store the serial port configuration. It is set to 0 termporarily
ser = 0
im_shape = (resY, resX)
dummyImg = np.zeros((im_shape[0], im_shape[1]))

# Time variables
activated = tk.IntVar()
Hi = tk.IntVar() # Initial Hour
Mi = tk.IntVar() # Initial Miute
Hf = tk.IntVar() # Final Hour
Mf = tk.IntVar() # Final Minute

########################################################################

########################################################################
############################### Functions ##############################

# Function to turn on or off specific LED #######################
def switchLED(LED, option, always):
    if always == False:
        if option == 1:
            ser.write(str.encode(str(LED) + 'H' + "\r\n"))
        elif option == 2:
            ser.write(str.encode(str(LED) + 'L' + "\r\n"))
        else:
            ser.write(str.encode("100L" + "\r\n"))
    else:
        if option == 1:
            ser.write(str.encode(str(LED) + 'I' + "\r\n"))
        elif option == 2:
            ser.write(str.encode(str(LED) + 'L' + "\r\n"))
        else:
            ser.write(str.encode("100L" + "\r\n"))
            
########################################################################

# Function to link/unlink serial device ##################
def Link(CON, COM, STAT):
    global ser
    if CON.get() == "Connect":
        ser = serial.Serial(COM.get(), 9600, timeout=0)
        STAT.set("Arduino connected")
        CON.set("Disconnect")
    elif CON.get() == "Disconnect":
        ser.close()
        STAT.set("Arduino disconnected")
        CON.set("Connect")
########################################################################
       
# Camera preview function: #####################
# The preview state is ended by pressing the ESC key
def Preview(STAT):
    STAT.set("Preview in process...")
    switchLED(0, 0, False) # This turns off all LEDs
    switchLED(white, 1, False) # This turns on the white LED
    time.sleep(0.5)
    
    # Use this instead if you encounter a very slow access to the camera
    # however, it does not work on all systems. Must change on lines 160 and 195
    #cap = cv2.VideoCapture(int(CAM.get()),cv2.CAP_DSHOW)
    cap = cv2.VideoCapture(int(CAM.get()))
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, resX)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, resY)
    counter = 0
    while(True):              
        retval, frame = cap.read()
        cv2.imshow("MEDUSA", frame)
        # In case the camera is not working then close the program
        if not retval:
            break
        k = cv2.waitKey(1)

        if k%256 == 27:
            STATUS.set("Preview terminated.")
            break
        elif k%256 == 32:                    
            STATUS.set(str("Image " + str(counter) + " captured"))
            cv2.imwrite("Test" + str(counter) + ".jpg", frame)
            counter += 1
            time.sleep(1)
    switchLED(0, 0, False) # Apago todos los LEDs
    cap.release()
    cv2.destroyAllWindows()
########################################################################

# Function to check/uncheck the available bands for image capture
def checkUncheckAll(bands, include):
    if include == True:
        for i in bands:
            i.set(1)
    else:
        for i in bands:
            i.set(0)
########################################################################

# Function for taking pictures: ############################################
def takePhoto(CAM, name, number, color, imRef):
    # Activating the camera
    # Use this instead if you encounter a very slow access to the camera
    # however, it does not work on all systems
    #cap = cv2.VideoCapture(int(CAM.get()),cv2.CAP_DSHOW)
    cap = cv2.VideoCapture(int(CAM.get()))
    # Adjusting resolution
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, resX)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, resY)
    # Taking several frames first (warming up the sensor)
    nc = 0
    while(nc < 10):
        nc = nc + 1
        retval, frame = cap.read()
        time.sleep(0.1)
    cap.release()
    if color == False:
        # Converting color images to grayscale
        grisRef = cv2.cvtColor(imRef, cv2.COLOR_BGR2GRAY)
        gris = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        # Here we substract the dark reference image from the lightened image
        im = cv2.subtract(gris, grisRef)
        global dummyImg
        dummyImg = im
        cv2.imwrite(str(number) + '_' + str(name) + ".png", im)
    elif color == True:
        imCol = cv2.subtract(frame, imRef)
        cv2.imwrite(str(number) + '_' + str(name) + ".png", imCol)
       
    cv2.destroyAllWindows()
########################################################################

# Combined function for light switching and photo capture: #######################
def lightAndShoot(LED, CAM, name, number, color):
    # First, all LEDs are turned off
    switchLED(0, 0, False)
    # Then a picture is taken in dark conditions
    # Use this instead if you encounter a very slow access to the camera
    # however, it does not work on all systems
    #cap = cv2.VideoCapture(int(CAM.get()),cv2.CAP_DSHOW)
    cap = cv2.VideoCapture(int(CAM.get()))
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, resX)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, resY)
    nc = 0
    while(nc < 10):
        nc = nc + 1
        retval, imRef = cap.read()
        time.sleep(0.1)
    cap.release()

    # Now, the lights are turned on
    switchLED(LED, 1, False)
    # Then the image is captured and the dark image is passed as argument
    # for substraction
    takePhoto(CAM, name, number, color, imRef)
    # Finally the LEDs are turned off
    switchLED(0, 0, False)
########################################################################

# Function to capture sets of images: #######################
def takeSets(CAM, NSET, TSET, INIT, STAT, activated):
    if INIT.get() == "BEGIN":
        STAT.set("Capturing image sets...")
        # Updating the name of the button
        INIT.set("STOP")
        window.update()
        time.sleep(1.5)
        # All of the LEDs must be off
        switchLED(0, 0, False)
        # Arrays for the ports and names
        Ports = []
        picNames = []
        for i, j, k in zip(wavelength, wavelengthStr, availablePorts):
            if i.get() == 1:
                picNames.append(j)
                Ports.append(k)
	
        totalDelay = int(TSET.get())
        totalSets = int(NSET.get())
        delay = 0
        step = 0.25
        for n in range(totalSets):
            STAT.set("Capturing images, please wait.")
            window.update()
            switchLED(0, 0, False)
            bd = 0
            for u in Ports:
                if u != white:
                    bd = bd + 1
            lenPorts = len(Ports)
            IMGs = np.zeros((im_shape[0], im_shape[1], bd))
            for p, nomb, j, num in zip(Ports, picNames, range(bd+1), range(lenPorts)):
                STAT.set("Capturing images, please wait: " + wavelengthStr[p] + " (" + str(num+1) + " of " + str(lenPorts) + ")")
                window.update()
                if p == white:
                    lightAndShoot(p, CAM, nomb, n, True)
                else:
                    lightAndShoot(p, CAM, nomb, n, False)
                    IMGs[:,:,j] = dummyImg
            if(TIMELAPSEPCA.get() == 1):
                ################# PCA calculation ############################
                # Keep in mind that you need at least 4 bands to compute the PCA
                STAT.set("Processing images for PCA...")
                window.update()
                time.sleep(1)
                IMG_matrix = np.zeros((IMGs[:,:,0].size, bd))
                for i in range(bd):
                    IMG_array = IMGs[:,:,i].flatten()  # covertimos 2d a 1d
                    IMG_arrayStd = (IMG_array - IMG_array.mean()) / IMG_array.std()
                    IMG_matrix[:,i] = IMG_arrayStd
                IMG_matrix.shape;
                
                np.set_printoptions(precision=3)
                cov = np.cov(IMG_matrix.transpose()) # Eigen Values
                EigVal,EigVec = np.linalg.eig(cov)
                # Arranging eigen values and eigen vectors
                order = EigVal.argsort()[::-1]
                EigVal = EigVal[order]
                EigVec = EigVec[:,order]
                PC = np.matmul(IMG_matrix, EigVec)
                
                # Resizing the PCA image
                PC_2d = np.zeros((im_shape[0],im_shape[1],bd))
                for i in range(bd):
                    PC_2d[:,:,i] = PC[:,i].reshape(-1, im_shape[1]) # Normalizing from 0 to 255
                PC_2d_Norm = np.zeros((im_shape[0], im_shape[1], bd))
                for i in range(bd):
                    PC_2d_Norm[:,:,i] = cv2.normalize(PC_2d[:,:,i],
                                    np.zeros(im_shape),0,255 ,cv2.NORM_MINMAX)
                   
                cv2.imwrite(str(n) + "_PC1.png", PC_2d_Norm[:,:,0])
                cv2.imwrite(str(n) + "_PC2.png", PC_2d_Norm[:,:,1])
                cv2.imwrite(str(n) + "_PC3.png", PC_2d_Norm[:,:,2])
                   
                STAT.set("PCA finished successfully!")
                    ##########################################################
                pass
           
           	
            while delay < totalDelay:
                if n >= totalSets - 1:
                    break
                elif INIT.get() == "BEGIN":
                    n = totalSets
                    switchLED(0, 0, False)
                    break
                time.sleep(step)
                delay = delay + step      
                porc = 100 * (n+1) / totalSets
                STAT.set("Progress: " + str(n+1) + " of " + NSET.get() + " sets -> " + str(porc) + "%" )
                window.update()
            delay = 0
            if INIT.get() == "BEGIN":
                n = totalSets
                switchLED(0, 0, False)
                break

        # Once the cycle is complete, turn off everything
        switchLED(0, 0, False)
        # The button name must be updated too
        INIT.set("BEGIN")
        STAT.set("Sets have been captured successfully!")
    else:
        INIT.set("BEGIN")
########################################################################

############################# End functions ############################
########################################################################

########################################################################
##################### Window configuration ######################
########################################################################

# Here 2 main frames are created which are used for camera and port configuration
# and for image capture setting.
frConf = tk.Frame(window,
                  highlightbackground="black",
                  highlightcolor="black",
                  highlightthickness=1,
                  bd=5
                  )
frCap = tk.Frame(window,
                 highlightbackground="black",
                 highlightcolor="black",
                 highlightthickness=1,
                 bd=5)

# This is to update the status bar
STATUS = tk.StringVar()
frStat = tk.Frame(window)

###################################################################
###################################################################

############################# frConf ##############################
# Widgets for camera and port configuration (frConf)
CAM = tk.StringVar()
COM = tk.StringVar()
CON = tk.StringVar()

lbCamera = tk.Label(frConf, text="Cam. Port: ").pack(side="left")
txtCamera = tk.Entry(frConf, width=8, textvariable=CAM).pack(side="left")
lbPort = tk.Label(frConf, text=" Ardu. Port: ").pack(side="left")
txtPort = tk.Entry(frConf, width=8, textvariable=COM).pack(side="left")
tk.Label(frConf, text=" ").pack(side="left")
btnLink = tk.Button(frConf,
                        textvariable=CON,
                        bg="blue",
                        fg="white",
                        command=partial(Link, CON, COM, STATUS)
                        ).pack(side="left")
tk.Label(frConf, text=" -->").pack(side="left")
btnPrev = tk.Button(frConf,
                    text="Preview",
                    bg="green",
                    fg="white",
                    command=partial(Preview, STATUS)
                    ).pack(side="left")
tk.Label(frConf, text="<-- ").pack(side="left")
# Default values
CAM.set("0")
COM.set("COM0")
CON.set("Connect")
# Adding all elements to the frame
frConf.pack()
###################################################################

############################# frCap ###############################
# Widgets para configuración de cámara y Port (frCap)
# Here we have several subframes
frCap_1 = tk.Frame(frCap)
frCap_2 = tk.Frame(frCap)
frCap_3 = tk.Frame(frCap)
# And several widgets for each frame

btnSelect = tk.Button(frCap_1, text="Check all", command=partial(checkUncheckAll, wavelength, True)).pack(side="left")
tk.Label(frCap_1, text="   ").pack(side="left")
btnDeselect = tk.Button(frCap_1, text="Uncheck all", command=partial(checkUncheckAll, wavelength, False)).pack(side="left")
TIMELAPSEPCA = tk.IntVar()
TIMELAPSEPCA.set(0)
tk.Label(frCap_1, text=" ---- ").pack(side="left")
chkTimelapsePCA = tk.Checkbutton(frCap_1, text="Do a PCA per set?", variable=TIMELAPSEPCA).pack(side="left")

# Checking elements:
for i in range(5):
    tk.Checkbutton(frCap_2,
                   text=wavelengthStr[i],
                   variable=wavelength[i]
                   ).grid(row=1, column=i)
for i in range(5):
    tk.Checkbutton(frCap_2,
                   text=wavelengthStr[i+5],
                   variable=wavelength[i+5]
                   ).grid(row=2, column=i)
for i in range(5):
    tk.Checkbutton(frCap_2,
                   text=wavelengthStr[i+5+5],
                   variable=wavelength[i+5+5]
                   ).grid(row=3, column=i)

# Number of sets and time between sets
NSET = tk.StringVar()
TSET = tk.StringVar()
INIT = tk.StringVar()
lbNSET = tk.Label(frCap_3, text="No. of sets ").pack(side="left")
txtNSET = tk.Entry(frCap_3, textvariable=NSET, width=6).pack(side="left")
lbTSET = tk.Label(frCap_3, text="Interval (s) ").pack(side="left")
txtTSET = tk.Entry(frCap_3, textvariable=TSET, width=6).pack(side="left")
tk.Label(frCap_3, text=" ------->").pack(side="left")
btnIniciar = tk.Button(frCap_3,
                       textvariable=INIT,
                       command=partial(takeSets, CAM, NSET, TSET, INIT, STATUS, activated),
                       bg="red",
                       fg="white").pack(side="left")
tk.Label(frCap_3, text="<-------").pack(side="left")

# Some default values
NSET.set("1")
TSET.set("0")
INIT.set("BEGIN")

# Adding all elements to the subframes and main frame
frCap_1.pack()
frCap_2.pack()
frCap_3.pack()
frCap.pack()
###################################################################

############################# frStat ##############################
# Widget to show the status bar
lbStat = tk.Label(frStat,
                  textvariable=STATUS,
                  bg="grey",
                  width=350).pack(side="left")

# A default initial value
STATUS.set("WARNING: Arduino not connected")

# Adding this to the main frame
frStat.pack(side="left")
###################################################################

# Init the program
window.mainloop()
