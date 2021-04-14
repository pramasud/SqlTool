from tkinter import *
from CommonParams import *
from tkinter.ttk import Notebook
from tkinter.ttk import Style
from tkinter.ttk import Combobox
from tkinter.filedialog import askopenfilename
from tkinter.messagebox import showerror
from tkinter.filedialog import askdirectory
from FileWriter import log, log_initialize, out, out_initialize, deepLog
import os
import cx_Oracle
#import re
import os.path
import sqlLite
import queue

# fileOrDir = 1  # File=0, Dir=1

keyValue = {}
settingsDb = CommonParams.settingsDb

skipFileValidations = 0
osUser = ""

class SqltoolGui:
    # global fileOrDir
    global keyValue
    global settingsDb
    # bg = "grey19"
    # fg = "azure"
    # objBg = "grey24"
    # txtBg = "grey17"
    
    bg = "LightBlue3"
    fg = "grey7"
    objBg = "grey97"
    txtBg = "grey99"
    initialdir = r"C:\\"

    def __init__(self, master, text_queue, status_queue, endApplication, initiateWorker):
        # Base Window
        self.lg("In __init__")
        global settingsDb
        settingsDb = CommonParams.settingsDb
        self.text_queue = text_queue
        self.status_queue = status_queue
        self.initiateWorker = initiateWorker
        self.end = endApplication
        self.lockScreen = 0
        self.command = ""
        self.filename = ""
        self.root = master
        master.title("File Processor")
        master.configure(background=self.bg)
        # Uppermost Frame
        # Contains 2 Frames, LeftFrame and RightFrame
        upperFrame = Frame(master)
        upperFrame.configure(background=self.bg, highlightbackground="gray60", highlightcolor="gray60",
                             highlightthickness=2, bd=0)
        upperFrame.pack(side=TOP, anchor='w', fill=X)
        # LeftFrame, contains 1 Button and One Label
        leftFrame = Frame(upperFrame, background=self.bg)
        leftFrame.pack(side=LEFT)
        # RightFrame, contains 1 Button and One Text Area
        rightFrame = Frame(upperFrame, background=self.bg)
        rightFrame.pack(side=LEFT, fill=X, expand=YES)
        # Frame below the Upper Frame, contains 3 Button for Main Functionality
        mainFuncFrame = Frame(master, background=self.bg)
        mainFuncFrame.pack(side=TOP, anchor='w', fill=X)
        # Frame below the mainFunc Frame, contains 3 Button for Additional Features
        addnlFuncFrame = Frame(master, background=self.bg)
        addnlFuncFrame.pack(side=TOP, anchor='w', fill=X)
        # Frame below the addnlFunc Frame, contains a text area to show processing
        # It also contains a Vertical Scrollbar
        textDispFrame = Frame(master, background=self.bg)
        textDispFrame.configure(highlightbackground="gray60", highlightcolor="gray60", highlightthickness=2, bd=0)
        textDispFrame.pack(side=TOP, anchor='w', fill=BOTH, expand=YES)
        # Frame below the textDisp Frame, contains a horizontal scroll bar for text area
        horzScrollFrame = Frame(master, background=self.bg)
        horzScrollFrame.pack(side=TOP, anchor='w', fill=X)
        # Frame below the horzScroll Frame, contains the status bar of the Application
        statusBarFrame = Frame(master, background=self.bg)
        statusBarFrame.pack(side=TOP, anchor='w', fill=BOTH)
        # Adding Frames Completed.

        # Add menu bar to Master Frame
        menu = Menu(master)
        master.config(menu=menu)

        # First Menu Option, File
        fileMenu = Menu(menu, tearoff=False)
        menu.add_cascade(label="File", menu=fileMenu)
        # Menu options in file - Open, Save and Save As
        fileMenu.add_command(label="Open Dir", command=self.load_dir)
        fileMenu.add_command(label="Open File", command=self.load_file)
        fileMenu.add_command(label="Clear Console", command=self.clearConsole)

        # To be Done ### This Section will be Implemented Later
        # fileMenu.add_command(label="Save As", command=self.launchFileProcessor)
        # Option to give submenu, will be needed later
        # fileSubMenu = Menu(fileMenu, tearoff=False)
        # fileMenu.add_cascade(label="Something", menu=fileSubMenu)
        # fileSubMenu.add_command(label="Something", command=self.launchFileProcessor)

        # Menu options in file - Exit
        fileMenu.add_separator()
        fileMenu.add_command(label="Exit", command=self.quit)

        # Second Menu Option, Edit
        editMenu = Menu(menu, tearoff=False)
        menu.add_cascade(label="Edit", menu=editMenu)
        # Menu options in Edit - Copy All to Clipboard, Settings
        editMenu.add_command(label="Copy All to Clipboard", command=self.copy_clp_brd)
        # To be Done ## In Progress
        editMenu.add_command(label="Settings", command=self.dispSettings)
        
        # Third Menu Option, Help
        helpMenu = Menu(menu, tearoff=False)
        menu.add_cascade(label="Help", menu=helpMenu)
        # Menu options in Help - About
        helpMenu.add_command(label="About", command=self.dispAbout)

        # Upper Frame Widgets
        button_open_dir = Button(leftFrame, text="Open Dir", command=self.load_dir, width=20, bg="darkorange1")
        self.selctionTypeLbl = Label(leftFrame, text="Dir", width=20, borderwidth=2, relief="groove", bg=self.objBg,
                                     fg=self.fg)
        button_open_file = Button(rightFrame, text="Open File", command=self.load_file, width=20, bg=self.objBg,
                                  fg=self.fg)
        self.targetName = Text(rightFrame, height=1, width=50, relief="sunken", bg=self.txtBg, fg=self.fg)
        self.targetName.bind("<Key>", lambda e: self.txtEvent(e))

        # mainFunc Frame Widgets
        # Variable for Radio Button
        self.showFullPath = IntVar()
        # Defaulting it to show full path
        self.showFullPath.set(1)
        # Check Button definition
        full_path = Checkbutton(mainFuncFrame, text="Show Full Path", variable=self.showFullPath, width=17,
                                bg=self.objBg,
                                fg=self.fg, activebackground=self.objBg, activeforeground=self.fg, bd=2,
                                selectcolor=self.objBg)
        self.lg("self.showFullPath = " + str(self.showFullPath.get()))
        # Button to Process Files
        button_prc = Button(mainFuncFrame, text="Process", command=self.process, width=20, bg=self.objBg,
                            fg=self.fg)
        ## button_file_lst = Button(mainFuncFrame, text="List Files", command=self.list_files, width=20, bg=self.objBg,
        ##                          fg=self.fg)
        button_file_lst = Button(mainFuncFrame, text="List Files", command=self.listFiles, width=20, bg=self.objBg,
                                 fg=self.fg)
        button_exec_db = Button(mainFuncFrame, text="Execute in Oracle", command=self.processInOracle, width=20,
                                bg=self.objBg,
                                fg=self.fg)
        button_js_uixml = Button(mainFuncFrame, text="Deploy JS UIXML", command=self.deployUiFiles, width=20,
                                 bg=self.objBg,
                                 fg=self.fg)

        # addnlFunc Frame Widgets
        button_3 = Button(addnlFuncFrame, text="Copy All To ClipBoard", command=self.copy_clp_brd, width=20,
                          bg=self.objBg,
                          fg=self.fg)
        button_4 = Button(addnlFuncFrame, text="Open Output Dir", command=self.openOutDir, width=20, bg=self.objBg,
                          fg=self.fg)
        button_5 = Button(addnlFuncFrame, text="Open Log Dir", command=self.openLogDir, width=20, bg=self.objBg,
                          fg=self.fg)

        default_db_name = sqlLite.getParamValue("DATABASE", "default_db_conn", settingsDb)
        if default_db_name == "Not_Found":
            default_db_name = "Select A Connection"

        self.comboVariable = StringVar(addnlFuncFrame)
        self.comboVariable.set(default_db_name)  # default value
        self.comboValues = sqlLite.getParamValueList("DB_USER_CONN", settingsDb)

        self.listOfConn = Combobox(addnlFuncFrame, textvariable=self.comboVariable, values=self.comboValues, state="readonly",
                              width=20)
        # self.listOfConn.current(1)
        self.lg("self.comboVariable.get() = " + self.comboVariable.get())

        default_server = sqlLite.getParamValue("JSUIXML", "default_server", settingsDb)
        if default_server == "Not_Found":
            default_server = "Select A Server"

        self.comboUiVariable = StringVar(addnlFuncFrame)
        self.comboUiVariable.set(default_server)  # default value
        self.comboUiValues = sqlLite.getParamValueList("JSUIXMLSERVER", settingsDb)

        self.listOfServers = Combobox(addnlFuncFrame, textvariable=self.comboUiVariable, values=self.comboUiValues,
                                 state="readonly", width=21)
        # self.listOfConn.current(1)

        self.status = Label(statusBarFrame, text="Ready...", bd=2, borderwidth=2, relief="sunken", anchor=W)

        # textVar = "Some Text"
        self.text = Text(textDispFrame, height=10, width=61, relief=SUNKEN, wrap="none", bg=self.txtBg, fg=self.fg)

        yScroll = Scrollbar(textDispFrame, orient=VERTICAL, background=self.bg, troughcolor=self.objBg)
        yScroll.pack(side=RIGHT, fill=Y)
        yScroll.config(command=self.text.yview, bg="black", activebackground="#313131")
        self.text.configure(yscrollcommand=yScroll.set)

        xScroll = Scrollbar(horzScrollFrame, orient=HORIZONTAL, background=self.bg, troughcolor=self.objBg)
        xScroll.pack(side=BOTTOM, fill=BOTH, anchor=S, expand=FALSE)
        xScroll.config(command=self.text.xview, bg="black", activebackground="#313131")
        self.text.configure(xscrollcommand=xScroll.set)

        # self.text.insert(END, textVar + "\n")
        self.text.bind("<Key>", lambda e: self.txtEvent(e))

        button_open_dir.pack(side=TOP, padx=5, pady=(15, 5), anchor=W)
        self.selctionTypeLbl.pack(side=TOP, padx=5, pady=(5, 15), anchor=W)

        button_open_file.pack(side=TOP, padx=5, pady=(15, 5), anchor=W)
        # self.l2.pack(side=TOP, padx=5, pady=5, anchor=W, fill=X, expand=YES)
        self.targetName.pack(side=TOP, padx=5, pady=(5, 15), anchor=W, fill=X, expand=YES)

        self.text.pack(side=TOP, fill=BOTH, padx=5, pady=5, expand=YES)

        button_prc.pack(side=LEFT, padx=5, pady=15)
        button_file_lst.pack(side=LEFT, padx=15, pady=15)
        full_path.pack(side=LEFT, padx=15, pady=15)
        button_exec_db.pack(side=LEFT, padx=15, pady=15)
        button_js_uixml.pack(side=LEFT, padx=15, pady=15)

        button_3.pack(side=LEFT, padx=5, pady=10)
        button_4.pack(side=LEFT, padx=15, pady=10)
        button_5.pack(side=LEFT, padx=15, pady=10)
        self.listOfConn.pack(side=LEFT, padx=16, pady=10)
        self.listOfServers.pack(side=LEFT, padx=15, pady=10)

        self.status.pack(side=BOTTOM, fill=X)

        # Setting Variables
        self.dirname = sqlLite.getParamValue("ALL", "DIR", settingsDb)
        if self.dirname == "Not_Found":
            self.dirname = " "
        self.targetName.delete('1.0', END)
        self.targetName.insert(END, self.dirname)
        self.text.delete('1.0', END)
        
    # Clears the Text Area
    def clearConsole(self):
        self.text.delete('1.0', END)

    # Makes the Text Boxes Readonly
    def txtEvent(self, event):
        if (event.state == 12 and event.keysym == 'c'):
            return
        else:
            return "break"

    def dispStatus(self, text):
        self.status.config(text=text)

    # Quits the Application
    def quit(self):
        self.end()
        self.root.destroy()

    # Calls Methods to close the Settings Window
    def sw_quit(self):
        self.sw.destroy()
        
    # Calls Methods to close the About Window
    def about_quit(self):
        self.about.destroy()

    def copy_clp_brd(self):
        self.lg("In copy_clp_brd...")
        inputValue = self.text.get("1.0", "end-1c")
        #self.lg(inputValue)
        # root.withdraw()
        self.root.clipboard_clear()
        self.root.clipboard_append(inputValue)
        self.root.update()
        
    # Sets the Text in the Console
    def setText(self, textValue):
        self.text.insert(END, textValue + "\n")
        self.text.see(END)

    # Calls Methods to open Console for Selecting a Single File
    def load_file(self):
        # global fileOrDir
        self.lg("In load_file...")
        CommonParams.fileOrDir = 0
        isError = 0
        self.dispStatus("Processing...")
        self.selctionTypeLbl.config(text="File")
        lastDir = sqlLite.getParamValue("ALL", "DIR", settingsDb)
        self.lg("lastDir = " + lastDir)
        if lastDir != "Not_Found":
            self.initialdir = lastDir
        validDir = self.dirname
        self.filename = askopenfilename(initialdir=self.initialdir, filetypes=(("All files", "*.*")
                                                                               , ("SPC files", "*.spc")
                                                                               , ("SQL Files", "*.sql")
                                                                               , ("DDL Files", "*.ddl")
                                                                               , ("INC Files", "*.inc")))
        if self.filename:
            self.targetName.delete('1.0', END)
            self.targetName.insert(END, self.filename)
            self.text.delete('1.0', END)
            fileDirectory = os.path.dirname(self.filename)
            sqlLite.setParamValue("ALL", "DIR", fileDirectory, settingsDb)
            self.lg("fileDirectory = " + fileDirectory)
        else:
            self.dirname = validDir

    def load_dir(self):
        # global fileOrDir
        global settingsDb
        self.lg("In load_dir...")
        self.lg("self.comboVariable = " + self.comboVariable.get())
        CommonParams.fileOrDir = 1
        self.selctionTypeLbl.config(text="Dir")
        lastDir = sqlLite.getParamValue("ALL", "DIR", settingsDb)
        self.lg("lastDir = " + lastDir)
        if lastDir != "Not_Found":
            self.initialdir = lastDir
        validDir = self.dirname
        self.dirname = askdirectory(initialdir=self.initialdir)
        if self.dirname:
            self.targetName.delete('1.0', END)
            self.targetName.insert(END, self.dirname)
            self.text.delete('1.0', END)
            sqlLite.setParamValue("ALL", "DIR", self.dirname, settingsDb)
            self.lg("self.dirname = " + self.dirname)
        else:
            self.dirname = validDir

    def openOutDir(self):
        self.lg("In openOutDir...")
        # global outFileLoc
        self.lg("outFileLoc = " + CommonParams.outFileLoc)
        if CommonParams.outFileLoc == "":
            self.lg("Out Directory Not Found")
        else:
            fileExists = str(os.path.exists(CommonParams.outFileLoc))
            if fileExists == "True":
                os.startfile(CommonParams.outFileLoc)
            else:
                self.lg("Out Directory Does Not Exist : " + CommonParams.outFileLoc)
                self.dispStatus("Out Directory Does Not Exist : " + CommonParams.outFileLoc)
                
    def openLogDir(self):
        self.lg("In openLogDir...")
        # global logFileLoc
        self.lg("logFileLoc = " + CommonParams.logFileLoc)
        if CommonParams.logFileLoc == "":
            self.lg("Out Directory Not Found")
        else:
            fileExists = str(os.path.exists(CommonParams.logFileLoc))
            if fileExists == "True":
                os.startfile(CommonParams.logFileLoc)
            else:
                self.lg("Out Directory Does Not Exist : " + CommonParams.logFileLoc)
                self.dispStatus("Out Directory Does Not Exist : " + CommonParams.logFileLoc)
                
    def getDir(self):
        return self.dirname
        
    def get_filename(self):
        return self.filename
        
    def getCommand(self):
        return self.command
        
    def listFiles(self):
        if self.lockScreen == 0:
            self.command = "LIST_FILES"
            self.initiateWorker()
            
    def processInOracle(self):
        if self.lockScreen == 0:
            self.command = "EXEC_ORACLE"
            self.initiateWorker()
            
    def deployUiFiles(self):
        if self.lockScreen == 0:
            self.command = "DEPLOY_UI_FILES"
            self.initiateWorker()
        
    def process(self):
        if self.lockScreen == 0:
            self.command = "PROCESS"
            self.initiateWorker()
        
    def lg(self, text):
        global logFile
        startLogs = 0
        if startLogs == 1:
            log(text, logFile)
            
    def dlg(self, text):
        global detailedLogs
        global logFile
        startLogs = 0
        #print(str(detailedLogs))
        if str(detailedLogs) == "1" and startLogs == 1:
            deepLog(text, logFile)
        
    def processIncoming(self):
        """Handle all messages currently in the text_queue, if any."""
        while self.text_queue.qsize( ):
            try:
                msg = self.text_queue.get(0)
                # Check contents of message and do whatever is needed. As a
                # simple test, print it (in real life, you would
                # suitably update the GUI's display in a richer fashion).
                #print(msg)
                if msg == "~~~Empty~Text~Area~~~":
                    self.clearConsole()
                else:
                    self.setText(msg)
            except text_queue.Empty:
                # just on general principles, although we don't
                # expect this branch to be taken in this case
                pass
                
    def processIncomingStatus(self):
        while self.status_queue.qsize( ):
            try:
                msg = self.status_queue.get(0)
                self.dispStatus(msg)
            except status_queue.Empty:
                # just on general principles, although we don't
                # expect this branch to be taken in this case
                pass

    def jsUiServerSelected(self, *args):
        self.lg("In jsUiServerSelected...")
        serverName = self.deployJsUiSerevrVar.get()
        self.lg("serverName = " + serverName)
        jsPath = sqlLite.getParamValue("JSPATH", serverName, settingsDb)
        uiXmlPath = sqlLite.getParamValue("UIXMLPATH", serverName, settingsDb)
        if jsPath != "Not_Found":
            self.deployJsPathVar.set(jsPath)
        if uiXmlPath != "Not_Found":
            self.deployUiPathVar.set(uiXmlPath)

    def addDbServerSelected(self, *args):
        self.lg("In addDbServerSelected...")
        serverSid = self.addDbServerVar.get()
        self.lg("serverSid = " + serverSid)
        dbHost = sqlLite.getParamValue("HOST", serverSid, settingsDb)
        dbPort = sqlLite.getParamValue("PORT", serverSid, settingsDb)
        if dbHost != "Not_Found":
            self.dbHostVar.set(dbHost)
        if dbPort != "Not_Found":
            self.dbPortVar.set(dbPort)

    def addDbUserConnSelected(self, *args):
        global osUser
        self.lg("In addDbUserConnSelected...")
        connName = self.addDbUserConnVar.get()
        self.lg("connName = " + connName)
        dbSid = sqlLite.getParamValue("DB_CONN_SID", connName, settingsDb)
        userName = sqlLite.getParamValue("DB_USER_NAME", connName, settingsDb)
        dbPassword = sqlLite.getPassword(osUser, dbSid, userName, settingsDb)
        #self.lg("dbPassword = " + dbPassword)
        if dbSid != "Not_Found":
            self.dbSidConnVar.set(dbSid)
        if userName != "Not_Found":
            self.dbUserConnVar.set(userName)

    def testDbConn(self):
        global osUser
        self.lg("In testDbConn...")
        allDetailsAvailable = 1
        connName = self.addDbUserConnVar.get()
        self.lg("connName = " + connName)
        if connName != "":
            dbSid = self.dbSidConnVar.get()
            self.lg("dbSid = " + dbSid)
            if dbSid == "":
                allDetailsAvailable = 0
            dbUser = self.dbUserConnVar.get()
            self.lg("dbUser = " + dbUser)
            if dbUser == "":
                allDetailsAvailable = 0
            dbPassword = self.dbConnPasswordVar.get()
            if dbPassword == "":
                dbPassword = sqlLite.getPassword(osUser, dbSid, dbUser, settingsDb)
            #self.lg("dbPassword = " + dbPassword)
            if dbPassword == "Not_Found":
                allDetailsAvailable = 0
                status = "Password Not Available"
            dbHost = sqlLite.getParamValue("HOST", dbSid, settingsDb)
            self.lg("dbHost = " + dbHost)
            if dbHost == "Not_Found":
                allDetailsAvailable = 0
                status = "DB Host Not Available"
            dbPort = sqlLite.getParamValue("PORT", dbSid, settingsDb)
            self.lg("dbPort = " + dbPort)
            if dbHost == "Not_Found":
                allDetailsAvailable = 0
                status = "DB Port Not Available"
            
            if allDetailsAvailable == 1:
                connectString = dbUser + "/" + dbPassword + "@" + dbHost + ":" + dbPort + "/" + dbSid
                self.lg("connectString = " + dbUser + "/*****@" + dbHost + ":" + dbPort + "/" + dbSid)
                try:
                    con = cx_Oracle.connect(connectString)
                    self.lg("Oracle Version = " + con.version)
                    self.testStatus.delete('1.0', END)
                    self.testStatus.insert(END, "Connection Successful")
                    con.close()
                except Exception as e:
                    self.testStatus.delete('1.0', END)
                    self.testStatus.insert(END, str(e))
                    self.lg("Error While Connecting to DB : " + str(e))
            else:
                self.testStatus.delete('1.0', END)
                self.testStatus.insert(END, status)
        else:
            self.testStatus.delete('1.0', END)
            self.testStatus.insert(END, "Select a Valid Connection.")
        
    def getLogDir(self):
        self.lg("In getLogDir...")
        logDir = self.logFileLocVar.get()
        self.lg("logDir = " + logDir)
        directory = askdirectory(initialdir=logDir)
        self.sw.lift()
        if directory != "":
            self.logFileLocVar.set(directory)
        
    def getOutDir(self):
        self.lg("In getOutDir...")
        outDir = self.outFileLocVar.get()
        self.lg("outDir = " + outDir)
        directory = askdirectory(initialdir=outDir)
        self.sw.lift()
        if directory != "":
            self.outFileLocVar.set(directory)
            
    #Displays the About Menu
    def dispAbout(self):
        self.lg("In dispAbout...")
        x = self.root.winfo_x()
        y = self.root.winfo_y()
        dx = 40
        dy = 20
        self.about = Toplevel(self.root, bg=self.bg)
        #self.sw.attributes('-topmost', 'true')
        w = self.about.winfo_width()
        h = self.about.winfo_height()
        self.about.geometry("%dx%d+%d+%d" % (300, 200, x + dx, y + dy))
        self.about.title("About SQLTool")
        self.about.resizable(width=False, height=False)
        #aboutUpperFrame = Frame(self.about)
        #aboutUpperFrame.configure(background=self.bg, highlightbackground="gray60", highlightcolor="gray60",
        #                       highlightthickness=0, bd=0)
        #
        #aboutLowerFrame = Frame(self.about)
        #aboutLowerFrame.configure(background=self.bg, highlightbackground="gray60", highlightcolor="gray60",
        #                       highlightthickness=0, bd=0)
        
        
        aboutAuthor = Label(self.about, text="Author : Sudeep", width=20, borderwidth=2, relief="groove",
                                     bg=self.objBg,
                                     fg=self.fg)
        self.aboutInfo = Text(self.about, height=3, width=30, relief="sunken", bg=self.txtBg, fg=self.fg)
        #self.testStatus.bind("<Key>", lambda e: self.txtEvent(e))
        self.aboutInfo.delete('1.0', END)
        self.aboutInfo.insert(END, "Application : SQL Tool \nReport Bugs to: \nSudeep.pramanick@gmail.com")
        aboutButtonOk = Button(self.about, text="Ok", command=self.about_quit, width=20,
                                bg=self.objBg,
                                fg=self.fg, padx=10)
        aboutAuthor.pack(pady=(20,10))
        self.aboutInfo.pack(pady=10)
        aboutButtonOk.pack(pady=10)
        
    

    # Calls Methods Apply the Changes
    def sw_apply_settings(self):
        global osUser
        global logFileLoc
        # global outFileLoc
        self.lg("In sw_apply_settings...")
        logDir = self.logFileLocVar.get()
        if logDir == "":
            logDir = logFileLoc
            self.logFileLocVar.set(logDir)
        sqlLite.setParamValue("APPLICATION", "log_location", logDir, settingsDb)
        if not os.path.exists(logDir):
            self.lg("Creating Log Directory : " + logDir)
            try:
                os.makedirs(logDir)
            except Exception as e:
                self.lg("Error While Creating Log Directory : " + str(e))
        
        outDir = self.outFileLocVar.get()
        if outDir == "":
            outDir = CommonParams.outFileLoc
            self.outFileLocVar.set(outDir)
        sqlLite.setParamValue("APPLICATION", "out_location", outDir, settingsDb)
        if not os.path.exists(outDir):
            self.lg("Creating Out Directory : " + outDir)
            try:
                os.makedirs(outDir)
            except Exception as e:
                self.lg("Error While Creating Out Directory : " + str(e))
        
        merge_output = self.consolidateOutVar.get()
        sqlLite.setParamValue("APPLICATION", "consolidate_out", merge_output, settingsDb)
        
        deep_log = self.deepLog.get()
        print("deep_log = " + str(deep_log) + settingsDb)
        sqlLite.setParamValue("APPLICATION", "deep_log", deep_log, settingsDb)

        inc_patterns = self.processPatternVar.get()
        self.lg("Process Apply Settings : inc_patterns = " + inc_patterns)
        if inc_patterns == "":
            self.lg("Deleting Rec")
            sqlLite.delParamRec("PROCESS", "inc_patterns", settingsDb)
        else:
            sqlLite.setParamValue("PROCESS", "inc_patterns", inc_patterns, settingsDb)

        exc_patterns = self.processExclVar.get()
        self.lg("Apply Settings : exc_patterns = " + exc_patterns)
        if exc_patterns == "":
            sqlLite.delParamRec("PROCESS", "exc_patterns", settingsDb)
        else:
            sqlLite.setParamValue("PROCESS", "exc_patterns", exc_patterns, settingsDb)

        skipFileValidations = self.skipFileValVar.get()
        self.lg("Apply Settings : skipFileValidations = " + str(skipFileValidations))
        if skipFileValidations == "":
            sqlLite.delParamRec("PROCESS", "skip_file_validations", settingsDb)
        else:
            sqlLite.setParamValue("PROCESS", "skip_file_validations", skipFileValidations, settingsDb)

        inc_patterns = self.listFilesPatternVar.get()
        self.lg("List Files Apply Settings : inc_patterns = " + inc_patterns)
        if inc_patterns == "":
            self.lg("Deleting Rec")
            sqlLite.delParamRec("LIST_FILES", "inc_patterns", settingsDb)
        else:
            sqlLite.setParamValue("LIST_FILES", "inc_patterns", inc_patterns, settingsDb)

        exc_patterns = self.listFilesExclVar.get()
        self.lg("Apply Settings : exc_patterns = " + exc_patterns)
        if exc_patterns == "":
            sqlLite.delParamRec("LIST_FILES", "exc_patterns", settingsDb)
        else:
            sqlLite.setParamValue("LIST_FILES", "exc_patterns", exc_patterns, settingsDb)

        inc_patterns = self.execOrclPatternVar.get()
        self.lg("Exec Oracle Apply Settings : inc_patterns = " + inc_patterns)
        if inc_patterns == "":
            self.lg("Deleting Rec")
            sqlLite.delParamRec("DATABASE", "inc_patterns", settingsDb)
        else:
            sqlLite.setParamValue("DATABASE", "inc_patterns", inc_patterns, settingsDb)

        exc_patterns = self.execOrclExclVar.get()
        self.lg("Apply Settings : exc_patterns = " + exc_patterns)
        if exc_patterns == "":
            sqlLite.delParamRec("DATABASE", "exc_patterns", settingsDb)
        else:
            sqlLite.setParamValue("DATABASE", "exc_patterns", exc_patterns, settingsDb)

        inc_patterns = self.deployUiPatternVar.get()
        self.lg("Apply Deploy JS Ui Settings : inc_patterns = " + inc_patterns)
        if inc_patterns == "":
            self.lg("Deleting Rec")
            sqlLite.delParamRec("UIXMLPATTERN", "inc_patterns", settingsDb)
        else:
            sqlLite.setParamValue("UIXMLPATTERN", "inc_patterns", inc_patterns, settingsDb)

        exc_patterns = self.deployUiExclVar.get()
        self.lg("Apply Settings : exc_patterns = " + exc_patterns)
        if exc_patterns == "":
            sqlLite.delParamRec("UIXMLPATTERN", "exc_patterns", settingsDb)
        else:
            sqlLite.setParamValue("UIXMLPATTERN", "exc_patterns", exc_patterns, settingsDb)

        inc_patterns = self.deployJsPatternVar.get()
        self.lg("Apply Deploy JS Ui Settings : inc_patterns = " + inc_patterns)
        if inc_patterns == "":
            self.lg("Deleting Rec")
            sqlLite.delParamRec("JSPATTERN", "inc_patterns", settingsDb)
        else:
            sqlLite.setParamValue("JSPATTERN", "inc_patterns", inc_patterns, settingsDb)

        exc_patterns = self.deployJsExclVar.get()
        self.lg("Apply Settings : exc_patterns = " + exc_patterns)
        if exc_patterns == "":
            sqlLite.delParamRec("JSPATTERN", "exc_patterns", settingsDb)
        else:
            sqlLite.setParamValue("JSPATTERN", "exc_patterns", exc_patterns, settingsDb)

        serverName = self.deployJsUiSerevrVar.get()
        serverName = serverName.upper()
        deleteServer = self.delJsUiSerevrVar.get()
        jsPath = self.deployJsPathVar.get()
        uiXmlPath = self.deployUiPathVar.get()
        self.lg("Apply Settings Server Name : serverName = " + serverName)
        self.lg("Apply Settings jsPath = " + jsPath)
        self.lg("Apply Settings uiXmlPath = " + uiXmlPath)
        if serverName != "":
            if deleteServer == 1:
                sqlLite.delParamRec("JSUIXMLSERVER", serverName, settingsDb)
                sqlLite.delParamRec("JSPATH", serverName, settingsDb)
                sqlLite.delParamRec("UIXMLPATH", serverName, settingsDb)
                self.delJsUiSerevrVar.set(0)
                self.deployJsUiSerevrVar.set("")
                self.deployJsPathVar.set("")
                self.deployUiPathVar.set("")
                self.comboUiValues = sqlLite.getParamValueList("JSUIXMLSERVER", settingsDb)
                self.listOfServers.config(values=self.comboUiValues)
                self.deployJsUiServerValues.config(values=self.comboUiValues)
            else:
                sqlLite.setParamValue("JSUIXMLSERVER", serverName, serverName, settingsDb)
                sqlLite.setParamValue("JSPATH", serverName, jsPath, settingsDb)
                sqlLite.setParamValue("UIXMLPATH", serverName, uiXmlPath, settingsDb)
                self.comboUiValues = sqlLite.getParamValueList("JSUIXMLSERVER", settingsDb)
                self.listOfServers.config(values=self.comboUiValues)
                self.deployJsUiServerValues.config(values=self.comboUiValues)

        dbServerSid = self.addDbServerVar.get()
        dbServerSid = dbServerSid.upper()
        deleteDbServer = self.delDBServerVar.get()
        dbHost = self.dbHostVar.get()
        dbPort = self.dbPortVar.get()
        self.lg("Apply Settings DB Server Name : dbServerSid = " + dbServerSid)
        self.lg("Apply Settings dbHost = " + dbHost)
        self.lg("Apply Settings dbPort = " + dbPort)
        if dbServerSid != "":
            if deleteDbServer == 1:
                sqlLite.delParamRec("DATABASESERVER", dbServerSid, settingsDb)
                sqlLite.delParamRec("HOST", dbServerSid, settingsDb)
                sqlLite.delParamRec("PORT", dbServerSid, settingsDb)
                self.delDBServerVar.set(0)
                self.addDbServerVar.set("")
                self.dbHostVar.set("")
                self.dbPortVar.set("")
                comboDbSidValues = sqlLite.getParamValueList("DATABASESERVER", settingsDb)
                self.dbSidValues.config(values=comboDbSidValues)
                self.addDbServerValues.config(values=comboDbSidValues)
            else:
                sqlLite.setParamValue("DATABASESERVER", dbServerSid, dbServerSid, settingsDb)
                sqlLite.setParamValue("HOST", dbServerSid, dbHost, settingsDb)
                sqlLite.setParamValue("PORT", dbServerSid, dbPort, settingsDb)
                comboDbSidValues = sqlLite.getParamValueList("DATABASESERVER", settingsDb)
                self.dbSidValues.config(values=comboDbSidValues)
                self.addDbServerValues.config(values=comboDbSidValues)
                
        dbUserConnection = self.addDbUserConnVar.get()
        dbUserConnection = dbUserConnection.upper()
        deleteDbServerCon = self.delDbUserConnVar.get()
        dbConnSid = self.dbSidConnVar.get()
        dbConnUser = self.dbUserConnVar.get()
        dbConnUserPwd = self.dbConnPasswordVar.get()
        self.lg("Apply Settings Connection Name : dbUserConnection = " + dbUserConnection)
        self.lg("Apply Settings dbConnSid = " + dbConnSid)
        self.lg("Apply Settings dbConnUser = " + dbConnUser)
        self.lg("Apply Settings dbConnUserPwd = " + dbConnUserPwd)
        if dbUserConnection != "":
            if deleteDbServerCon == 1:
                sqlLite.delParamRec("DB_USER_CONN", dbUserConnection, settingsDb)
                sqlLite.delParamRec("DB_CONN_SID", dbUserConnection, settingsDb)
                sqlLite.delParamRec("DB_USER_NAME", dbUserConnection, settingsDb)
                sqlLite.delPassword(osUser, dbConnSid, dbConnUser, settingsDb)
                self.delDbUserConnVar.set(0)
                self.addDbUserConnVar.set("")
                self.dbSidConnVar.set("")
                self.dbUserConnVar.set("")
                self.dbConnPasswordVar.set("")
                self.testStatus.delete('1.0', END)
                self.comboValues = sqlLite.getParamValueList("DB_USER_CONN", settingsDb)
                self.listOfConn.config(values=self.comboValues)
                self.addDbUserConnValues.config(values=self.comboValues)
            else:
                sqlLite.setParamValue("DB_USER_CONN", dbUserConnection, dbUserConnection, settingsDb)
                sqlLite.setParamValue("DB_CONN_SID", dbUserConnection, dbConnSid, settingsDb)
                sqlLite.setParamValue("DB_USER_NAME", dbUserConnection, dbConnUser, settingsDb)
                if dbConnUserPwd != "":
                    sqlLite.setPassword(osUser, dbConnSid, dbConnUser, dbConnUserPwd, settingsDb)
                    self.dbConnPasswordVar.set("")
                self.comboValues = sqlLite.getParamValueList("DB_USER_CONN", settingsDb)
                self.listOfConn.config(values=self.comboValues)
                self.addDbUserConnValues.config(values=self.comboValues)

    # Calls Methods to Deploy the Settings Window
    def dispSettings(self):
        global logFileLoc
        # global outFileLoc
        self.lg("In dispSettings...")
        x = self.root.winfo_x()
        y = self.root.winfo_y()
        dx = 20
        dy = 20
        self.sw = Toplevel(self.root, bg=self.bg)
        #self.sw.attributes('-topmost', 'true')
        w = self.sw.winfo_width()
        h = self.sw.winfo_height()
        self.sw.geometry("%dx%d+%d+%d" % (550, 540, x + dx, y + dy))
        self.sw.title("SQLTool Settings")
        self.sw.resizable(width=False, height=False)
        # self.sw.overrideredirect(1)

        swUpperFrame = Frame(self.sw)
        swUpperFrame.configure(background=self.bg, highlightbackground="gray60", highlightcolor="gray60",
                               highlightthickness=0, bd=0)

        swLowerFrame = Frame(self.sw)
        swLowerFrame.configure(background=self.bg, highlightbackground="gray60", highlightcolor="gray60",
                               highlightthickness=0, bd=0)

        # Notebook Style
        noteStyler = Style()
        # noteStyler.configure("TNotebook", background="green", borderwidth=0, padx=5, pady=5)
        # noteStyler.configure("TNotebook.Tab", background="blue", foreground=COLOR_3, lightcolor=COLOR_6, borderwidth=0, padx=5, pady=5)

        noteStyler.configure("TFrame", tabposition='wn', background=self.bg, foreground=self.fg, borderwidth=0)

        settingsBase = Notebook(swUpperFrame, style='TFrame', width=530, height=500)

        f1 = Frame(settingsBase, bg=self.bg, borderwidth=0, highlightthickness=0, relief='flat')
        f2 = Frame(settingsBase, bg=self.bg, borderwidth=0, highlightthickness=0, relief='flat')
        f3 = Frame(settingsBase, bg=self.bg, borderwidth=0, highlightthickness=0, relief='flat')
        
        settingsBase.add(f1, text='General Settings   ')
        settingsBase.add(f2, text='Database Settings ')
        settingsBase.add(f3, text='JS/XML Settings    ')
        
        self.logFileLocVar = StringVar()
        log_location = sqlLite.getParamValue("APPLICATION", "log_location", settingsDb)
        self.lg("Settings : log_location = " + log_location)
        if log_location == "Not_Found":
            log_location = CommonParams.logFileLoc
        self.logFileLocVar.set(log_location)
        
        self.outFileLocVar = StringVar()
        out_location = sqlLite.getParamValue("APPLICATION", "out_location", settingsDb)
        self.lg("Settings : out_location = " + out_location)
        if out_location == "Not_Found":
            out_location = CommonParams.outFileLoc
        self.outFileLocVar.set(out_location)
        
        self.deepLog = IntVar()
        deep_log = sqlLite.getParamValue("APPLICATION", "deep_log", settingsDb)
        self.lg("Settings : deep_log = " + deep_log)
        if deep_log == "Not_Found":
            deep_log = "0"
        self.deepLog.set(deep_log)
        
        self.consolidateOutVar = IntVar()
        consolidate_out = sqlLite.getParamValue("APPLICATION", "consolidate_out", settingsDb)
        self.lg("Settings : consolidate_out = " + consolidate_out)
        if consolidate_out == "Not_Found":
            consolidate_out = "1"
        self.consolidateOutVar.set(consolidate_out)

        self.processPatternVar = StringVar()
        inc_patterns = sqlLite.getParamValue("PROCESS", "inc_patterns", settingsDb)
        self.lg("Settings : inc_patterns = " + inc_patterns)
        if inc_patterns == "Not_Found":
            inc_patterns = "*.sql"
        self.processPatternVar.set(inc_patterns)

        self.processExclVar = StringVar()
        exc_patterns = sqlLite.getParamValue("PROCESS", "exc_patterns", settingsDb)
        self.lg("Settings : exc_patterns = " + exc_patterns)
        if exc_patterns != "Not_Found":
            self.processExclVar.set(exc_patterns)

        self.skipFileValVar = IntVar()
        skipFileValidations = sqlLite.getParamValue("PROCESS", "skip_file_validations", settingsDb)
        self.lg("Settings : skipFileValidations = " + skipFileValidations)
        if skipFileValidations == "Not_Found":
            skipFileValidations = "0"
        self.skipFileValVar.set(skipFileValidations)
        
        appSettingsFrame = Frame(f1, bg=self.bg, borderwidth=1, highlightthickness=1, relief='groove')

        appSettingsLabel = Label(appSettingsFrame, text="Application", width=12, borderwidth=2,
                              relief="flat", bg=self.bg,
                              fg=self.fg)
        appSettingsFrameUpper = Frame(appSettingsFrame, bg=self.bg, borderwidth=0, highlightthickness=0, relief='flat')
        appSettingsFrameBelow = Frame(appSettingsFrame, bg=self.bg, borderwidth=0, highlightthickness=0, relief='flat')
        appSettingsFrameLowest = Frame(appSettingsFrame, bg=self.bg, borderwidth=0, highlightthickness=0, relief='flat')
        appSettingsFrameLeft = Frame(appSettingsFrameUpper, bg=self.bg, borderwidth=0, highlightthickness=0, relief='flat')
        appSettingsFrameMiddle = Frame(appSettingsFrameUpper, bg=self.bg, borderwidth=0, highlightthickness=0, relief='flat')
        appSettingsFrameRight = Frame(appSettingsFrameUpper, bg=self.bg, borderwidth=0, highlightthickness=0, relief='flat')
        
        logFileLocation = Label(appSettingsFrameLeft, text="Log Location", width=12, borderwidth=2, relief="groove",
                                     bg=self.objBg,
                                     fg=self.fg)
        logLocationValues = Entry(appSettingsFrameMiddle, width=43, borderwidth=2, relief="groove",
                                    bg=self.objBg, textvariable=self.logFileLocVar,
                                    fg=self.fg)
        selectLogDir = Button(appSettingsFrameRight, text="Browse", command=self.getLogDir, width=5, height=1, bg=self.objBg,
                          borderwidth=0, fg=self.fg)
        outFileLocation = Label(appSettingsFrameLeft, text="Out Location", width=12, borderwidth=2, relief="groove",
                                     bg=self.objBg,
                                     fg=self.fg)
        outLocationValues = Entry(appSettingsFrameMiddle, width=43, borderwidth=2, relief="groove",
                                    bg=self.objBg, textvariable=self.outFileLocVar,
                                    fg=self.fg)
        selectOutDir = Button(appSettingsFrameRight, text="Browse", command=self.getOutDir, width=5, height=1, bg=self.objBg,
                          borderwidth=0, fg=self.fg)
        
        enableDeepLog = Label(appSettingsFrameBelow, text="Deep Log", width=12, borderwidth=2, relief="groove",
                                     bg=self.objBg,
                                     fg=self.fg)
        enableDeepLogValue = Checkbutton(appSettingsFrameBelow, text="Enable Detailed Logs", variable=self.deepLog,
                                       bg=self.objBg,
                                       fg=self.fg, activebackground=self.objBg, activeforeground=self.fg, bd=2,
                                       selectcolor=self.objBg)
                          
        oneOutputFile = Label(appSettingsFrameLowest, text="Consolidate", width=12, borderwidth=2, relief="groove",
                                     bg=self.objBg,
                                     fg=self.fg)
        consolidate_output = Checkbutton(appSettingsFrameLowest, text="Consolidate Output Files", variable=self.consolidateOutVar,
                                       bg=self.objBg,
                                       fg=self.fg, activebackground=self.objBg, activeforeground=self.fg, bd=2,
                                       selectcolor=self.objBg)
        

        processFrame = Frame(f1, bg=self.bg, borderwidth=1, highlightthickness=1, relief='groove')

        processLaabel = Label(processFrame, text="Process", width=12, borderwidth=2,
                              relief="flat", bg=self.bg,
                              fg=self.fg)
        processFrameUpper = Frame(processFrame, bg=self.bg, borderwidth=0, highlightthickness=0, relief='flat')
        processFrameBelow = Frame(processFrame, bg=self.bg, borderwidth=0, highlightthickness=0, relief='flat')
        processFrameLeft = Frame(processFrameUpper, bg=self.bg, borderwidth=0, highlightthickness=0, relief='flat')
        processFrameRight = Frame(processFrameUpper, bg=self.bg, borderwidth=0, highlightthickness=0, relief='flat')

        processFilterPattern = Label(processFrameLeft, text="Filter Pattern", width=12, borderwidth=2, relief="groove",
                                     bg=self.objBg,
                                     fg=self.fg)
        ProcessFilterValues = Entry(processFrameRight, width=50, borderwidth=2, relief="groove",
                                    bg=self.objBg, textvariable=self.processPatternVar,
                                    fg=self.fg)

        processExcludePattern = Label(processFrameLeft, text="Exclude Pattern", width=12, borderwidth=2,
                                      relief="groove", bg=self.objBg,
                                      fg=self.fg)
        ProcessExcludeValues = Entry(processFrameRight, width=50, borderwidth=2, relief="groove", bg=self.objBg,
                                     textvariable=self.processExclVar,
                                     fg=self.fg)

        file_validations = Checkbutton(processFrameBelow, text="Skip File Validations", variable=self.skipFileValVar,
                                       bg=self.objBg,
                                       fg=self.fg, activebackground=self.objBg, activeforeground=self.fg, bd=2,
                                       selectcolor=self.objBg)

        self.listFilesPatternVar = StringVar()
        inc_patterns = sqlLite.getParamValue("LIST_FILES", "inc_patterns", settingsDb)
        self.lg("Settings : inc_patterns = " + inc_patterns)
        if inc_patterns == "Not_Found":
            inc_patterns = "*.*"
        self.listFilesPatternVar.set(inc_patterns)

        self.listFilesExclVar = StringVar()
        exc_patterns = sqlLite.getParamValue("LIST_FILES", "exc_patterns", settingsDb)
        self.lg("Settings : exc_patterns = " + exc_patterns)
        if exc_patterns != "Not_Found":
            self.listFilesExclVar.set(exc_patterns)

        listFilesFrame = Frame(f1, bg=self.bg, borderwidth=1, highlightthickness=1, relief='groove')

        listFilesLaabel = Label(listFilesFrame, text="list Files", width=12, borderwidth=2,
                                relief="flat", bg=self.bg,
                                fg=self.fg)

        listFilesFrameLeft = Frame(listFilesFrame, bg=self.bg, borderwidth=0, highlightthickness=0, relief='flat')
        listFilesFrameRight = Frame(listFilesFrame, bg=self.bg, borderwidth=0, highlightthickness=0, relief='flat')

        listFilesFilterPattern = Label(listFilesFrameLeft, text="Filter Pattern", width=12, borderwidth=2,
                                       relief="groove",
                                       bg=self.objBg,
                                       fg=self.fg)
        listFilesFilterValues = Entry(listFilesFrameRight, width=50, borderwidth=2, relief="groove",
                                      bg=self.objBg, textvariable=self.listFilesPatternVar,
                                      fg=self.fg)

        listFilesExcludePattern = Label(listFilesFrameLeft, text="Exclude Pattern", width=12, borderwidth=2,
                                        relief="groove", bg=self.objBg,
                                        fg=self.fg)
        listFilesExcludeValues = Entry(listFilesFrameRight, width=50, borderwidth=2, relief="groove", bg=self.objBg,
                                       textvariable=self.listFilesExclVar,
                                       fg=self.fg)

        swButtonCancel = Button(swLowerFrame, text="Cancel", command=self.sw_quit, width=20,
                                bg=self.objBg,
                                fg=self.fg, padx=10)
        swButtonApply = Button(swLowerFrame, text="Apply", command=self.sw_apply_settings, width=20,
                               bg=self.objBg,
                               fg=self.fg, padx=10)

        self.execOrclPatternVar = StringVar()
        inc_patterns = sqlLite.getParamValue("DATABASE", "inc_patterns", settingsDb)
        self.lg("Settings : inc_patterns = " + inc_patterns)
        if inc_patterns == "Not_Found":
            inc_patterns = "*.ddl;*.inc;*.spc;*.sql"
        self.execOrclPatternVar.set(inc_patterns)

        self.execOrclExclVar = StringVar()
        exc_patterns = sqlLite.getParamValue("DATABASE", "exc_patterns", settingsDb)
        self.lg("Settings : exc_patterns = " + exc_patterns)
        if exc_patterns != "Not_Found":
            self.execOrclExclVar.set(exc_patterns)

        execOrclFrame = Frame(f1, bg=self.bg, borderwidth=1, highlightthickness=1, relief='groove')

        execOrclLaabel = Label(execOrclFrame, text="Execute In Oracle", width=15, borderwidth=2,
                               relief="flat", bg=self.bg,
                               fg=self.fg)

        execOrclFrameLeft = Frame(execOrclFrame, bg=self.bg, borderwidth=0, highlightthickness=0, relief='flat')
        execOrclFrameRight = Frame(execOrclFrame, bg=self.bg, borderwidth=0, highlightthickness=0, relief='flat')

        execOrclFilterPattern = Label(execOrclFrameLeft, text="Filter Pattern", width=12, borderwidth=2,
                                      relief="groove",
                                      bg=self.objBg,
                                      fg=self.fg)
        execOrclFilterValues = Entry(execOrclFrameRight, width=50, borderwidth=2, relief="groove",
                                     bg=self.objBg, textvariable=self.execOrclPatternVar,
                                     fg=self.fg)

        execOrclExcludePattern = Label(execOrclFrameLeft, text="Exclude Pattern", width=12, borderwidth=2,
                                       relief="groove", bg=self.objBg,
                                       fg=self.fg)
        execOrclExcludeValues = Entry(execOrclFrameRight, width=50, borderwidth=2, relief="groove", bg=self.objBg,
                                      textvariable=self.execOrclExclVar,
                                      fg=self.fg)

        swUpperFrame.pack(side=TOP, anchor='w', fill=X)
        swLowerFrame.pack(side=TOP, anchor='w', fill=X)
        settingsBase.pack()
        appSettingsFrame.pack(padx=2, pady=2)
        appSettingsLabel.pack()
        appSettingsFrameUpper.pack(anchor="w")
        appSettingsFrameBelow.pack(anchor="w")
        appSettingsFrameLowest.pack(anchor="w")
        appSettingsFrameLeft.pack(side="left", padx=10)
        appSettingsFrameMiddle.pack(side="left", padx=(10,1))
        appSettingsFrameRight.pack(side="right")
        logFileLocation.pack(pady=(5,5))
        logLocationValues.pack(pady=(5,5))
        selectLogDir.pack(padx=(1,10),pady=5)
        outFileLocation.pack(pady=(5,5))
        outLocationValues.pack(pady=(5,5))
        selectOutDir.pack(padx=(1,10),pady=5)
        enableDeepLog.pack(side="left",anchor="w",pady=5,padx=10)
        enableDeepLogValue.pack(side="left",pady=5,padx=10)
        oneOutputFile.pack(side="left",anchor="w",pady=5,padx=10)
        consolidate_output.pack(side="left",pady=5,padx=10)
        
        processFrame.pack(padx=2, pady=2)
        processLaabel.pack()
        processFrameUpper.pack()
        processFrameBelow.pack()
        processFrameLeft.pack(side="left", padx=10)
        processFrameRight.pack(side="left", padx=10)
        processFilterPattern.pack(pady=(5,5))
        ProcessFilterValues.pack(pady=(5,5))
        processExcludePattern.pack(pady=5)
        ProcessExcludeValues.pack(pady=5)
        file_validations.pack(pady=5)
        listFilesFrame.pack(padx=2, pady=2)
        listFilesLaabel.pack()
        listFilesFrameLeft.pack(side="left", padx=10)
        listFilesFrameRight.pack(side="left", padx=10)
        listFilesFilterPattern.pack(pady=(5, 5))
        listFilesFilterValues.pack(pady=(5, 5))
        listFilesExcludePattern.pack(pady=5)
        listFilesExcludeValues.pack(pady=5)
        execOrclFrame.pack(padx=2, pady=2)
        execOrclLaabel.pack()
        execOrclFrameLeft.pack(side="left", padx=10)
        execOrclFrameRight.pack(side="left", padx=10)
        execOrclFilterPattern.pack(pady=(5, 5))
        execOrclFilterValues.pack(pady=(5, 5))
        execOrclExcludePattern.pack(pady=5)
        execOrclExcludeValues.pack(pady=5)
        
        self.deployUiPatternVar = StringVar()
        inc_patterns = sqlLite.getParamValue("UIXMLPATTERN", "inc_patterns", settingsDb)
        self.lg("Settings JS UIXML: inc_patterns = " + inc_patterns)
        if inc_patterns == "Not_Found":
            inc_patterns = "*.xml"
        self.deployUiPatternVar.set(inc_patterns)

        self.deployUiExclVar = StringVar()
        exc_patterns = sqlLite.getParamValue("UIXMLPATTERN", "exc_patterns", settingsDb)
        self.lg("Settings : exc_patterns = " + exc_patterns)
        if exc_patterns != "Not_Found":
            self.deployUiExclVar.set(exc_patterns)

        self.deployJsPatternVar = StringVar()
        inc_patterns = sqlLite.getParamValue("JSPATTERN", "inc_patterns", settingsDb)
        self.lg("Settings : inc_patterns = " + inc_patterns)
        if inc_patterns == "Not_Found":
            inc_patterns = "*.js"
        self.deployJsPatternVar.set(inc_patterns)

        self.deployJsExclVar = StringVar()
        exc_patterns = sqlLite.getParamValue("JSPATTERN", "exc_patterns", settingsDb)
        self.lg("Settings : exc_patterns = " + exc_patterns)
        if exc_patterns != "Not_Found":
            self.deployJsExclVar.set(exc_patterns)

        self.deployJsUiSerevrVar = StringVar()
        self.delJsUiSerevrVar = IntVar()
        self.delJsUiSerevrVar.set(0)
        self.deployJsPathVar = StringVar()
        self.deployUiPathVar = StringVar()

        comboJsUiValues = sqlLite.getParamValueList("JSUIXMLSERVER", settingsDb)

        deployJsUiFrame = Frame(f3, bg=self.bg, borderwidth=1, highlightthickness=1, relief='groove')

        deployJsUiLaabel = Label(deployJsUiFrame, text="Deploy JS & UIXML", width=15, borderwidth=2,
                                 relief="flat", bg=self.bg,
                                 fg=self.fg)

        deployJsUiFrameLeft = Frame(deployJsUiFrame, bg=self.bg, borderwidth=0, highlightthickness=0, relief='flat')
        deployJsUiFrameRight = Frame(deployJsUiFrame, bg=self.bg, borderwidth=0, highlightthickness=0, relief='flat')

        deployJsFilterPattern = Label(deployJsUiFrameLeft, text="JS File Pattern", width=12, borderwidth=2,
                                      relief="groove",
                                      bg=self.objBg,
                                      fg=self.fg)
        deployJsFilterValues = Entry(deployJsUiFrameRight, width=50, borderwidth=2, relief="groove",
                                     bg=self.objBg, textvariable=self.deployJsPatternVar,
                                     fg=self.fg)

        deployJsExcludePattern = Label(deployJsUiFrameLeft, text="JS Excl Pattern", width=12, borderwidth=2,
                                       relief="groove", bg=self.objBg,
                                       fg=self.fg)
        deployJsExcludeValues = Entry(deployJsUiFrameRight, width=50, borderwidth=2, relief="groove", bg=self.objBg,
                                      textvariable=self.deployJsExclVar,
                                      fg=self.fg)

        deployJsUiServer = Label(deployJsUiFrameLeft, text="Server Name", width=12, borderwidth=2,
                             relief="groove", bg=self.objBg,
                             fg=self.fg)

        self.deployJsUiServerValues = Combobox(deployJsUiFrameRight, textvariable=self.deployJsUiSerevrVar, values=comboJsUiValues, width=47)

        self.deployJsUiServerValues.bind("<<ComboboxSelected>>", self.jsUiServerSelected)

        deployJsPath = Label(deployJsUiFrameLeft, text="JS Deploy Path", width=12, borderwidth=2,
                                       relief="groove", bg=self.objBg,
                                       fg=self.fg)
        deployJsPathValues = Entry(deployJsUiFrameRight, width=50, borderwidth=2, relief="groove", bg=self.objBg,
                                      textvariable=self.deployJsPathVar,
                                      fg=self.fg)

        deployUiFilterPattern = Label(deployJsUiFrameLeft, text="UI File Pattern", width=12, borderwidth=2,
                                      relief="groove",
                                      bg=self.objBg,
                                      fg=self.fg)
        deployUiFilterValues = Entry(deployJsUiFrameRight, width=50, borderwidth=2, relief="groove",
                                     bg=self.objBg, textvariable=self.deployUiPatternVar,
                                     fg=self.fg)

        deployUiExcludePattern = Label(deployJsUiFrameLeft, text="UI Excl Pattern", width=12, borderwidth=2,
                                       relief="groove", bg=self.objBg,
                                       fg=self.fg)
        deployUiExcludeValues = Entry(deployJsUiFrameRight, width=50, borderwidth=2, relief="groove", bg=self.objBg,
                                      textvariable=self.deployUiExclVar,
                                      fg=self.fg)

        deployUiPath = Label(deployJsUiFrameLeft, text="UI Deploy Path", width=12, borderwidth=2,
                                       relief="groove", bg=self.objBg,
                                       fg=self.fg)
        deployUiPathValues = Entry(deployJsUiFrameRight, width=50, borderwidth=2, relief="groove", bg=self.objBg,
                                      textvariable=self.deployUiPathVar,
                                      fg=self.fg)

        deleteJsUiServer = Label(deployJsUiFrameLeft, text="Delete Server", width=12, borderwidth=2,
                             relief="groove", bg=self.objBg,
                             fg=self.fg)
        deleteJsUiServerValue = Checkbutton(deployJsUiFrameRight, text="Check to Delete Server", variable=self.delJsUiSerevrVar,
                                bg=self.objBg,
                                fg=self.fg, activebackground=self.objBg, activeforeground=self.fg, bd=2,
                                selectcolor=self.objBg)
                                
        deployJsUiFrame.pack(padx=2, pady=2)
        deployJsUiLaabel.pack()
        deployJsUiFrameLeft.pack(side="left", padx=10)
        deployJsUiFrameRight.pack(side="left", padx=10)
        deployJsFilterPattern.pack(pady=(5, 5))
        deployJsFilterValues.pack(pady=(5, 5))
        deployJsExcludePattern.pack(pady=5)
        deployJsExcludeValues.pack(pady=5)
        deployUiFilterPattern.pack(pady=(5, 5))
        deployUiFilterValues.pack(pady=(5, 5))
        deployUiExcludePattern.pack(pady=5)
        deployUiExcludeValues.pack(pady=5)
        deployJsUiServer.pack(pady=(15,5))
        self.deployJsUiServerValues.pack(pady=(15,5), anchor="w")
        deployJsPath.pack(pady=5)
        deployJsPathValues.pack(pady=5)
        deployUiPath.pack(pady=5)
        deployUiPathValues.pack(pady=5)
        deleteJsUiServer.pack(pady=5)
        deleteJsUiServerValue.pack(pady=5, anchor="w")

        swButtonCancel.pack(side="left", padx=(120,10), pady=2)
        swButtonApply.pack(side="right", padx=20, pady=2)

        self.addDbServerVar = StringVar()
        self.dbHostVar = StringVar()
        self.dbPortVar = StringVar()
        self.delDBServerVar = IntVar()

        addDBFrame = Frame(f2, bg=self.bg, borderwidth=1, highlightthickness=1, relief='groove')

        comboDbValues = sqlLite.getParamValueList("DATABASESERVER", settingsDb)

        addDbLaabel = Label(addDBFrame, text="Database", width=15, borderwidth=2,
                            relief="flat", bg=self.bg,
                            fg=self.fg)

        addDbFrameLeft = Frame(addDBFrame, bg=self.bg, borderwidth=0, highlightthickness=0, relief='flat')
        addDbFrameRight = Frame(addDBFrame, bg=self.bg, borderwidth=0, highlightthickness=0, relief='flat')

        addDbServer = Label(addDbFrameLeft, text="Database SID", width=12, borderwidth=2,
                            relief="groove", bg=self.objBg,
                            fg=self.fg)

        self.addDbServerValues = Combobox(addDbFrameRight, textvariable=self.addDbServerVar, values=comboDbValues, width=47)

        self.addDbServerValues.bind("<<ComboboxSelected>>", self.addDbServerSelected)

        dbHost = Label(addDbFrameLeft, text="Host", width=12, borderwidth=2,
                       relief="groove", bg=self.objBg,
                       fg=self.fg)
        dbHostValues = Entry(addDbFrameRight, width=50, borderwidth=2, relief="groove", bg=self.objBg,
                             textvariable=self.dbHostVar,
                             fg=self.fg)

        dbPort = Label(addDbFrameLeft, text="Port", width=12, borderwidth=2,
                       relief="groove", bg=self.objBg,
                       fg=self.fg)
        dbPortValues = Entry(addDbFrameRight, width=50, borderwidth=2, relief="groove", bg=self.objBg,
                             textvariable=self.dbPortVar,
                             fg=self.fg)

        deleteDbSid = Label(addDbFrameLeft, text="Delete Database", width=12, borderwidth=2,
                            relief="groove", bg=self.objBg,
                            fg=self.fg)
        deleteDbSidValue = Checkbutton(addDbFrameRight, text="Check to Delete DB Server", variable=self.delDBServerVar,
                                       bg=self.objBg,
                                       fg=self.fg, activebackground=self.objBg, activeforeground=self.fg, bd=2,
                                       selectcolor=self.objBg)

        self.addDbUserConnVar = StringVar()
        self.dbSidConnVar = StringVar()
        self.dbUserConnVar = StringVar()
        self.dbConnPasswordVar = StringVar()
        self.delDbUserConnVar = IntVar()

        addDbUserFrame = Frame(f2, bg=self.bg, borderwidth=1, highlightthickness=1, relief='groove')

        comboDbValues = sqlLite.getParamValueList("DB_USER_CONN", settingsDb)

        comboDbSidValues = sqlLite.getParamValueList("DATABASESERVER", settingsDb)

        comboDbUserValues = sqlLite.getParamValueList("DBUSERS", settingsDb)

        addDbUserLaabel = Label(addDbUserFrame, text="Database User", width=15, borderwidth=2,
                                relief="flat", bg=self.bg,
                                fg=self.fg)

        addDbUserFrameLeft = Frame(addDbUserFrame, bg=self.bg, borderwidth=0, highlightthickness=0, relief='flat')
        addDbUserFrameRight = Frame(addDbUserFrame, bg=self.bg, borderwidth=0, highlightthickness=0, relief='flat')

        addDbUserConn = Label(addDbUserFrameLeft, text="Conn Name", width=12, borderwidth=2,
                              relief="groove", bg=self.objBg,
                              fg=self.fg)

        self.addDbUserConnValues = Combobox(addDbUserFrameRight, textvariable=self.addDbUserConnVar, values=comboDbValues,
                                       width=47)

        self.addDbUserConnValues.bind("<<ComboboxSelected>>", self.addDbUserConnSelected)

        dbSid = Label(addDbUserFrameLeft, text="Database SID", width=12, borderwidth=2,
                      relief="groove", bg=self.objBg,
                      fg=self.fg)
        self.dbSidValues = Combobox(addDbUserFrameRight, textvariable=self.dbSidConnVar, values=comboDbSidValues, width=47)

        dbUser = Label(addDbUserFrameLeft, text="DB User Name", width=12, borderwidth=2,
                       relief="groove", bg=self.objBg,
                       fg=self.fg)

        dbUserValues = Combobox(addDbUserFrameRight, textvariable=self.dbUserConnVar, values=comboDbUserValues,
                                width=47)

        dbPassword = Label(addDbUserFrameLeft, text="Password", width=12, borderwidth=2,
                           relief="groove", bg=self.objBg,
                           fg=self.fg)
        dbPasswordValues = Entry(addDbUserFrameRight, width=50, borderwidth=2, relief="groove", bg=self.objBg,
                                 textvariable=self.dbConnPasswordVar,
                                 fg=self.fg)

        deleteDbUser = Label(addDbUserFrameLeft, text="Delete Conn", width=12, borderwidth=2,
                             relief="groove", bg=self.objBg,
                             fg=self.fg)

        deleteDbUserValue = Checkbutton(addDbUserFrameRight, text="Check to Delete DB Conn",
                                        variable=self.delDbUserConnVar,
                                        bg=self.objBg,
                                        fg=self.fg, activebackground=self.objBg, activeforeground=self.fg, bd=2,
                                        selectcolor=self.objBg)

        testDbConnButton = Button(addDbUserFrameLeft, text="Test Conn", command=self.testDbConn, width=11,
                                  bg=self.objBg,
                                  fg=self.fg)

        self.testStatus = Text(addDbUserFrameRight, height=1, width=38, relief="sunken", bg=self.txtBg, fg=self.fg)
        self.testStatus.bind("<Key>", lambda e: self.txtEvent(e))

        addDBFrame.pack(padx=2, pady=2)
        addDbLaabel.pack()
        addDbFrameLeft.pack(side="left", padx=10)
        addDbFrameRight.pack(side="left", padx=10)
        addDbServer.pack(pady=(15, 5))
        self.addDbServerValues.pack(pady=(15, 5), anchor="w")
        dbHost.pack(pady=5)
        dbHostValues.pack(pady=5)
        dbPort.pack(pady=5)
        dbPortValues.pack(pady=5)
        deleteDbSid.pack(pady=5)
        deleteDbSidValue.pack(pady=5, anchor="w")

        addDbUserFrame.pack(padx=2, pady=2)
        addDbUserLaabel.pack()
        addDbUserFrameLeft.pack(side="left", padx=10)
        addDbUserFrameRight.pack(side="left", padx=10)
        addDbUserConn.pack(pady=(15, 5))
        self.addDbUserConnValues.pack(pady=(15, 5), anchor="w")
        dbSid.pack(pady=5)
        self.dbSidValues.pack(pady=5, anchor="w")
        dbUser.pack(pady=5)
        dbUserValues.pack(pady=5, anchor="w")
        dbPassword.pack(pady=5)
        dbPasswordValues.pack(pady=5, anchor="w")
        testDbConnButton.pack(pady=5)
        self.testStatus.pack(pady=5, anchor="w")
        deleteDbUser.pack(pady=5)
        deleteDbUserValue.pack(pady=5, anchor="w")

