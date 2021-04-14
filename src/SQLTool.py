
from tkinter import *
from tkinter.ttk import Notebook
from tkinter.ttk import Style
from tkinter.ttk import Combobox
from shutil import copyfile
from tkinter.filedialog import askopenfilename
from tkinter.messagebox import showerror
from tkinter.filedialog import askdirectory
from FileWriter import log, log_initialize, out, out_initialize, deepLog
from SqltoolGui import *
from CommonParams import *
import os
import cx_Oracle
import re
import FileHandler
import sys
import subprocess
import os.path
import fnmatch
import sqlLite
import threading
import queue
import time

multiLineComment = 0
insideFunction = 0
targetNameNext = 0
parameterNameNext = 0
parameterTypeNext = 0
parameterDirectionNext = 0
returnTypeNext = 0
functionDeclareNext = 0
functionBodyNext = 0
waitForNextWord = 0
stopReadingParams = 0
insideProcedure = 0
procedureDeclareNext = 0
procedureBodyNext = 0
output = ""
description = ""
singleQuoteStart = 0
checkNoBody = 0
checkEnd = 0
skipNextWord = 0
singleQuoteInLine = 0
prevChar = ""
currChar = ""

logFileLoc = ""
outFileLoc = ""
logFile = ""
outFile = ""
createOneFile = 0
detailedLogs = 0
beginBlockStarted = 0
closeApplication = 0

# fileOrDir = 1  # File=0, Dir=1

keyValue = {}
#settingsDb = ""

skipFileValidations = 0
osUser = ""


        
############################################################
########              Next Class Start             #########
############################################################
            
class ThreadedClient:
    def __init__(self, master):
        """
        Start the GUI and the asynchronous threads. We are in the main
        (original) thread of the application, which will later be used by
        the GUI. We spawn a new thread for the worker.
        """
        self.master = master
        self.running = -1

        # Create the text_queue
        self.text_queue = queue.Queue()
        self.status_queue = queue.Queue()

        # Set up the GUI part
        self.gui = SqltoolGui(master, self.text_queue, self.status_queue, self.endApplication, self.initiateWorker)

        # Start the periodic call in the GUI to check if the text_queue contains
        # anything
        self.periodicCall()
        
    def initiateWorker(self):
        # Set up the thread to do asynchronous I/O
        # More can be made if necessary
        self.running = 1
        self.thread1 = threading.Thread(target=self.workerThread1)
        self.thread1.start()

    def periodicCall(self):
        """
        Check every 10 ms if there is something new in the text_queue.
        """
        self.gui.processIncoming()
        self.gui.processIncomingStatus()
        if not self.running:
            print("Closing...")
            import sys
            sys.exit(1)
        self.master.after(10, self.periodicCall)

    def workerThread1(self):
        command = self.gui.getCommand()
        print(command)
        self.gui.lockScreen = 1
        if command == "LIST_FILES":
            self.listFiles()
        elif command == "EXEC_ORACLE":
            self.execInOracle()
        elif command == "DEPLOY_UI_FILES":
            self.deployJsUixml()
        elif command == "PROCESS":
            self.process()
            
    # calls the Logging Methods.
    def lg(self, text):
        global logFile
        # print(logFile)
        startLogs = 1
        if startLogs == 1:
            log(text, logFile)
            
    def dlg(self, text):
        global detailedLogs
        global logFile
        startLogs = 1
        # print(str(detailedLogs))
        if str(detailedLogs) == "1" and startLogs == 1:
            deepLog(text, logFile)
            
    def listFiles(self):
        # global fileOrDir
        # global outFileLoc
        global outFile
        outFile = CommonParams.outFileLoc + "\\SqlTool_Output.csv"
        out_initialize(outFile)
        dirname = self.gui.getDir()
        fileNamePath = self.gui.get_filename()
        showFullPath = self.gui.showFullPath.get()
        print(dirname + " " + str(showFullPath))
        #self.dispStatus("Processing...")
        self.text_queue.put("~~~Empty~Text~Area~~~")
        self.status_queue.put("Processing List Files...")
        
        inc_patterns = sqlLite.getParamValue("LIST_FILES", "inc_patterns", CommonParams.settingsDb)
        if inc_patterns == "Not_Found":
            inc_patterns = "*.*"
            sqlLite.setParamValue("LIST_FILES", "inc_patterns", inc_patterns, CommonParams.settingsDb)

        patternList = inc_patterns.split(";")

        exc_patterns = sqlLite.getParamValue("LIST_FILES", "exc_patterns", CommonParams.settingsDb)
        if exc_patterns == "Not_Found":
            sqlLite.setParamValue("LIST_FILES", "exc_patterns", exc_patterns, CommonParams.settingsDb)

        if exc_patterns != "Not_Found":
            excPatternList = exc_patterns.split(";")

        if CommonParams.fileOrDir == 1:
            try:
                fileExists = str(os.path.exists(dirname))
                if fileExists == "True":
                    for baseFolder, subFolder, files in os.walk(dirname):
                        if not files:
                            continue
                        for p in patternList:
                            filteredFiles = fnmatch.filter(files, p)
                            for item in filteredFiles:
                                skip_loop = False
                                if exc_patterns != "Not_Found":
                                    for e in excPatternList:
                                        toExclude = fnmatch.fnmatch(item, e)
                                        if toExclude:
                                            skip_loop = True
                                            break
                                if skip_loop == False:
                                    fileNamePath = str(os.path.normpath(os.path.join(baseFolder, item)))
                                    if showFullPath == 0:
                                        dispFileName = os.path.basename(fileNamePath)
                                    else:
                                        dispFileName = fileNamePath
                                    #self.setText(dispFileName)
                                    self.text_queue.put(dispFileName)
                                    out(dispFileName, outFile)
                                    #time.sleep(2)
            except Exception as e:
                print("No Dir exists " + str(e))
        elif CommonParams.fileOrDir == 0:
            if showFullPath == 0:
                dispFileName = os.path.basename(fileNamePath)
            else:
                dispFileName = fileNamePath
            self.text_queue.put(fileNamePath)
            out(dispFileName, outFile)
        print("Done...")
        self.gui.lockScreen = 0

    # Calls Methods to Deploy the JS and UIXML Files
    def deployJsUixml(self):
        isError = 0
        self.lg("In Deploy JS Uixml...")
        self.text_queue.put("~~~Empty~Text~Area~~~")
        self.lg("Console Cleared.")
        self.dirname = self.gui.getDir()
        self.fileNamePath = self.gui.get_filename()
        self.showFullPath = self.gui.showFullPath.get()
        uiServer = self.gui.comboUiVariable.get()
        self.lg("uiServer = " + uiServer)
        self.status_queue.put("Processing...")
        if uiServer == "Select A Server":
            self.lg("Select A Valid Server from List.")
            self.status_queue.put("Select A Valid Server from List.")
            sqlLite.setParamValue("JSUIXML", "default_server", uiServer, CommonParams.settingsDb)
            isError = 1
        else:
            sqlLite.setParamValue("JSUIXML", "default_server", uiServer, CommonParams.settingsDb)
            jsPath = sqlLite.getParamValue("JSPATH", uiServer, CommonParams.settingsDb)
            uiXmlPath = sqlLite.getParamValue("UIXMLPATH", uiServer, CommonParams.settingsDb)
            self.lg("jsPath = " + jsPath)
            self.lg("uiXmlPath = " + uiXmlPath)

            if jsPath == "Not_Found" or uiXmlPath == "Not_Found":
                self.lg("JS/UIXML Paths are Not Available for Selected Server.")
                self.status_queue.put("JS/UIXML Paths are Not Available for Selected Server " + uiServer)
                isError = 1
            else:
                self.lg("Processing for JS files...")
                inc_patterns = sqlLite.getParamValue("JSPATTERN", "inc_patterns", CommonParams.settingsDb)
                self.lg("inc_patterns = " + inc_patterns)
                if inc_patterns == "Not_Found":
                    inc_patterns = "*.js"
                    sqlLite.setParamValue("JSPATTERN", "inc_patterns", inc_patterns, CommonParams.settingsDb)

                jsPatternList = inc_patterns.split(";")

                exc_patterns = sqlLite.getParamValue("JSPATTERN", "exc_patterns", CommonParams.settingsDb)
                self.lg("exc_patterns = " + exc_patterns)
                if exc_patterns == "Not_Found":
                    sqlLite.setParamValue("JSPATTERN", "exc_patterns", exc_patterns, CommonParams.settingsDb)
                if exc_patterns != "Not_Found":
                    jsExcPatternList = exc_patterns.split(";")

                if os.path.exists(jsPath):
                    if CommonParams.fileOrDir == 1:
                        fileExists = str(os.path.exists(self.dirname))
                        if fileExists == "True":
                            for baseFolder, subFolder, files in os.walk(self.dirname):
                                if not files:
                                    continue
                                for p in jsPatternList:
                                    filteredFiles = fnmatch.filter(files, p)
                                    for item in filteredFiles:
                                        skip_loop = False
                                        if exc_patterns != "Not_Found":
                                            for e in jsExcPatternList:
                                                self.lg("File = " + item + ", Ex Filter = " + e)
                                                toExclude = fnmatch.fnmatch(item, e)
                                                if toExclude:
                                                    skip_loop = True
                                                    break
                                        if skip_loop == False:
                                            self.fileNamePath = str(os.path.normpath(os.path.join(baseFolder, item)))
                                            # fileNamePath = str(files)
                                            self.lg("self.fileNamePath = " + self.fileNamePath)
                                            # self.l2.config(text=fileNamePath)
                                            if self.gui.showFullPath.get() == 0:
                                                dispFileName = os.path.basename(self.fileNamePath)
                                            else:
                                                dispFileName = self.fileNamePath
                                            self.text_queue.put("Transferring " + dispFileName + " to " + jsPath)
                                            outFileName = jsPath + "\\" + os.path.basename(self.fileNamePath)
                                            outSysLocation = jsPath + "\\SYS\\"
                                            outSysFileName = jsPath + "\\SYS\\" + os.path.basename(self.fileNamePath)
                                            #time.sleep(2)
                                            try:
                                                copyfile(self.fileNamePath, outFileName)
                                                self.text_queue.put("Completed..")
                                            except Exception as e:
                                                self.lg("Error While Copying File.." + str(e))
                                                self.text_queue.put("Error While Copying File.." + str(e))
                                            if os.path.exists(outSysLocation):
                                                if os.path.isfile(outSysFileName):
                                                    self.text_queue.put("Deleting " + outSysFileName)
                                                    try:
                                                        os.remove(outSysFileName)
                                                        self.text_queue.put("Completed..")
                                                    except Exception as e:
                                                        self.lg("Error While Removing File.." + str(e))
                                                        self.text_queue.put("Error While Copying File.." + str(e))
                    else:
                        self.lg("Deploy JS - This Operation Only Available on Directories.")
                        self.status_queue.put("Please select a Directory...")
                        isError = 1
                else:
                    self.lg("JS Location Does Not Exists.")
                    self.text_queue.put("JS Location Does Not Exists : " + jsPath)

                self.lg("Processing for UIXML files...")
                inc_patterns = sqlLite.getParamValue("UIXMLPATTERN", "inc_patterns", CommonParams.settingsDb)
                self.lg("inc_patterns = " + inc_patterns)
                if inc_patterns == "Not_Found":
                    inc_patterns = "*.xml"
                    sqlLite.setParamValue("UIXMLPATTERN", "inc_patterns", inc_patterns, CommonParams.settingsDb)

                uiPatternList = inc_patterns.split(";")

                exc_patterns = sqlLite.getParamValue("UIXMLPATTERN", "exc_patterns", CommonParams.settingsDb)
                self.lg("exc_patterns = " + exc_patterns)
                if exc_patterns == "Not_Found":
                    sqlLite.setParamValue("UIXMLPATTERN", "exc_patterns", exc_patterns, CommonParams.settingsDb)

                if exc_patterns != "Not_Found":
                    uiExcPatternList = exc_patterns.split(";")

                if os.path.exists(uiXmlPath):
                    if CommonParams.fileOrDir == 1:
                        fileExists = str(os.path.exists(self.dirname))
                        if fileExists == "True":
                            for baseFolder, subFolder, files in os.walk(self.dirname):
                                if not files:
                                    continue
                                for p in uiPatternList:
                                    filteredFiles = fnmatch.filter(files, p)
                                    for item in filteredFiles:
                                        skip_loop = False
                                        if exc_patterns != "Not_Found":
                                            for e in uiExcPatternList:
                                                self.lg("File = " + item + ", Ex Filter = " + e)
                                                toExclude = fnmatch.fnmatch(item, e)
                                                if toExclude:
                                                    skip_loop = True
                                                    break
                                        if skip_loop == False:
                                            self.fileNamePath = str(os.path.normpath(os.path.join(baseFolder, item)))
                                            # fileNamePath = str(files)
                                            self.lg("self.fileNamePath = " + self.fileNamePath)
                                            # self.l2.config(text=fileNamePath)
                                            if self.gui.showFullPath.get() == 0:
                                                dispFileName = os.path.basename(self.fileNamePath)
                                            else:
                                                dispFileName = self.fileNamePath
                                            self.text_queue.put("Transferring " + dispFileName + " to " + uiXmlPath)
                                            outFileName = uiXmlPath + "\\" + os.path.basename(self.fileNamePath)
                                            try:
                                                copyfile(self.fileNamePath, outFileName)
                                                self.text_queue.put("Completed..")
                                            except Exception as e:
                                                self.lg("Error While Copying File.." + str(e))
                                                self.text_queue.put("Error While Copying File.." + str(e))
                    else:
                        self.lg("Deploy UIXML - This Operation Only Available on Directories.")
                        self.status_queue.put("Please select a Directory...")
                        isError = 1
                else:
                    self.lg("UIXML Location Does Not Exists.")
                    self.text_queue.put("UIXML Location Does Not Exists : " + uiXmlPath)
        if isError == 0:
            self.status_queue.put("Ready")
        self.gui.lockScreen = 0

    # Calls Methods to Execute Files in Oracle
    def execInOracle(self):
        self.lg("In execInOracle...")
        # global fileOrDir
        global osUser
        isError = 0
        self.text_queue.put("~~~Empty~Text~Area~~~")
        self.lg("Console Cleared.")
        userName = ""
        dbSid = ""
        passWord = ""
        dbHost = ""
        dbPort = ""
        self.status_queue.put("Processing...")
        dbConnection = self.gui.comboVariable.get()
        self.lg("dbConnection = " + dbConnection)
        print(dbConnection)
        if dbConnection == "Select A Connection" or dbConnection == "":
            self.lg("Select A Valid Oracle Connection from List.")
            self.status_queue.put("Select A Valid Oracle Connection from List.")
            isError = 1
        else:
            sqlLite.setParamValue("DATABASE", "default_db_conn", dbConnection, CommonParams.settingsDb)
            userName = sqlLite.getParamValue("DB_USER_NAME", dbConnection, CommonParams.settingsDb)
            dbSid = sqlLite.getParamValue("DB_CONN_SID", dbConnection, CommonParams.settingsDb)
            self.lg("userName, dbSid = " + userName + ", " + dbSid)
            
            passWord = sqlLite.getPassword(osUser, dbSid, userName, CommonParams.settingsDb)
            if passWord == "Not_Found":
                self.lg("Please Set the Password in the Settings Menu.")
                self.status_queue.put("Please Set the Password in the Settings Menu.")
                isError = 1
            dbHost = sqlLite.getParamValue("HOST", dbSid, CommonParams.settingsDb)
            dbPort = sqlLite.getParamValue("PORT", dbSid, CommonParams.settingsDb)
            if dbHost == "Not_Found" or dbPort == "Not_Found":
                self.lg("Db Host and Port Not Available for the Selected Databse")
                self.status_queue.put("Db Host and Port Not Available for the Selected Database.. " + dbConnection)
                isError = 1
            else:
                self.lg("dbHost, dbPort = " + dbHost + ", " + dbPort)
                connectString = userName + "/" + passWord + "@" + dbHost + ":" + dbPort + "/" + dbSid
                self.lg(userName + "/*****@" + dbHost + ":" + dbPort + "/" + dbSid)

                inc_patterns = sqlLite.getParamValue("DATABASE", "inc_patterns", CommonParams.settingsDb)
                self.lg("inc_patterns = " + inc_patterns)
                if inc_patterns == "Not_Found":
                    inc_patterns = "*.*"
                    sqlLite.setParamValue("DATABASE", "inc_patterns", inc_patterns, CommonParams.settingsDb)
                patternList = inc_patterns.split(";")

                exc_patterns = sqlLite.getParamValue("DATABASE", "exc_patterns", CommonParams.settingsDb)
                self.lg("exc_patterns = " + exc_patterns)
                if exc_patterns == "Not_Found":
                    sqlLite.setParamValue("DATABASE", "exc_patterns", exc_patterns, CommonParams.settingsDb)
                elif exc_patterns != "Not_Found":
                    excPatternList = exc_patterns.split(";")

                allFiles = []
                if CommonParams.fileOrDir == 1:
                    fileExists = str(os.path.exists(self.gui.dirname))
                    if fileExists == "True":
                        for baseFolder, subFolder, files in os.walk(self.gui.dirname):
                            if not files:
                                continue
                            for p in patternList:
                                filteredFiles = fnmatch.filter(files, p)
                                for item in filteredFiles:
                                    skip_loop = False
                                    if exc_patterns != "Not_Found":
                                        for e in excPatternList:
                                            self.lg("File = " + item + ", Ex Filter = " + e)
                                            toExclude = fnmatch.fnmatch(item, e)
                                            if toExclude:
                                                skip_loop = True
                                                break

                                    if skip_loop == False:
                                        self.fileNamePath = str(os.path.normpath(os.path.join(baseFolder, item)))
                                        allFiles.append(self.fileNamePath)
                                        # fileNamePath = str(files)
                                        #self.lg("self.fileNamePath = " + self.fileNamePath)
                                        ## self.l2.config(text=fileNamePath)
                                        #if self.showFullPath.get() == 0:
                                        #    dispFileName = os.path.basename(self.fileNamePath)
                                        #else:
                                        #    dispFileName = self.fileNamePath
                                        #self.setText("Processing.. " + dispFileName)
                                        #self.parseAndExecuteSql(self.fileNamePath, connectString)
                        for p in patternList:
                            for files in fnmatch.filter(allFiles, p):
                                if self.gui.showFullPath.get() == 0:
                                    dispFileName = os.path.basename(files)
                                else:
                                    dispFileName = files
                                self.text_queue.put("Processing.. " + dispFileName)
                                print("Processing..")
                                self.parseAndExecuteSql(files, connectString)
                        
                    else:
                        self.status_queue.put("Directory Does Not Exist. " + self.gui.dirname)
                        isError = 1
                else:
                    fileExists = str(os.path.exists(self.gui.filename))
                    if fileExists == "True":
                        self.text_queue.put("Processing File : " + self.gui.filename)
                        self.parseAndExecuteSql(self.gui.filename, connectString)
                    else:
                        self.status_queue.put("File Does Not Exist. " + self.gui.filename)
                        isError = 1
        if isError == 0:
            self.status_queue.put("Ready.")
        self.gui.lockScreen = 0

    def parseAndExecuteSql(self, fullFileName, connectString):
        #global outFileLoc
        global outFile
        print("Here")
        self.lg("In launchFileProcessor...")
        if createOneFile == 0:
            baseFileName = os.path.basename(fullFileName)
            baseFileNameNoExt = ('.').join(baseFileName.split('.')[:-1])
            outFile = CommonParams.outFileLoc + "\\" + baseFileNameNoExt + "_Out.csv"
            out_initialize(outFile)
        fileName = fullFileName
        processNext = 1
        self.lg("Processing : " + fileName)
        #self.lg("connectString : " + connectString)
        #self.text_queue.put("Trying to connect to Oracle")
        try:
            con = cx_Oracle.connect(connectString)
            #self.text_queue.put("Processing File")
        except Exception as e:
            processNext = 0
            self.text_queue.put("Oracle Connection Failed : " + str(e))
            self.lg(str(e))
        
        if processNext == 1:
            try:
                cur = con.cursor()
            except Exception as e:
                processNext = 0
                self.text_queue.put("Oracle access denied : " + str(e))
                con.close()
                self.lg(str(e))
        
        if processNext == 1:
            new_line = ""
            curr_word = ""
            word = ""
            prev_word = ""
            curr_delim = ""
            sql_var = ""
            start_new_word = 0
            inside_quote = 0
            creating_something = 0
            wait_for_replace = 0
            object_type_next = 0
            error_parsing = 0
            wait_for_end = 0
            inside_comment = 0
            multi_line_comment_flg = 0
            multi_line_comment = 0
            single_line_comment = 0
            skip_next_char = 0
            new_word = 0
            print_once = 0
            check_param = 0
            check_as_is = 0
            check_as_is_next = 0
            params_started = 0
            begin_next = 0
            param_name_next = 0
            default_value_next = 0
            param_dir_next = 0
            param_type_next = 0
            set_param_vars_later = 0
            reset_at_next_word = 0
            in_pkg = 0
            proc_or_func_next = 0
            in_pkg_proc_or_func = 0
            check_semicolon_next = 0
            next_word_if = 0
            next_word_loop = 0
            obj_body_str = ""
            obj_nested_cnt = 0
            mother_object_name = ""
            mother_object_type = ""
            mother_object_indicator = 0
            wait_for_slash = 0
            wait_for_semicolon = 0
            object_name_next = 0
            word_already_processed = 0
            in_proc_or_func = 0
            in_trigger = 0
            altering_something = 0
            ins_or_del_something = 0
            deleting_something = 0
            updating_something = 0
            into_or_from_next = 0
            from_or_obj_next = 0
            reset_at_nth_word = 0
            object_name = ""
            object_type = ""
            out_display_str = ""
            file_line_number = 0
            first_valid_line_char = 0
            with open(fileName) as f:
                for line in f:
                    if closeApplication == 1:
                        break
                    self.dlg("")
                    self.dlg(line)
                    file_line_number = file_line_number + 1
                    line_len = len(line)
                    first_valid_line_char = 0
                    for x in range(0, line_len):
                        if closeApplication == 1:
                            break
                        if skip_next_char == 1:
                            skip_next_char = 0
                            sql_var = sql_var + line[x]
                        elif line[x] == "'" and inside_comment == 0:
                            sql_var = sql_var + line[x]
                            check_param = 0
                            first_valid_line_char = 1
                            check_semicolon_next = 0
                            if inside_quote == 0:
                                inside_quote = 1
                                if default_value_next == 1:
                                    default_value_next = 0
                            else:
                                inside_quote = 0
                        elif line[x] == ";" and inside_comment == 0 and inside_quote == 0:
                            check_param = 0
                            first_valid_line_char = 1
                            print("Inside ; wait_for_semicolon = " + str(wait_for_semicolon))
                            curr_delim = ";"
                            start_new_word = 1
                            if check_semicolon_next == 1:
                                check_semicolon_next = 0
                                in_pkg_proc_or_func = 0
                                check_as_is = 0
                                proc_or_func_next = 1
                                self.dlg("Here2....")
                            if wait_for_semicolon == 1:
                                wait_for_semicolon = 0
                                wait_for_slash = 0
                                creating_something = 0
                                altering_something = 0
                                mother_object_indicator = 0
                                proc_or_func_next = 0
                                start_new_word = 0
                                ins_or_del_something = 0
                                deleting_something = 0
                                updating_something = 0
                                self.dlg(sql_var)
                                self.dlg("............................................................")
                                out(out_display_str, outFile)
                                self.text_queue.put(out_display_str)
                                print(sql_var)
                                print("About to Exec...")
                                #self.setText(out_display_str)
                                try:
                                    if closeApplication == 1:
                                        break
                                    cur.execute(sql_var)
                                    self.text_queue.put("Done...")
                                    print(mother_object_name)
                                    #self.setText("Done...")
                                    out("Done...", outFile)
                                except Exception as e:
                                    self.text_queue.put("Error = " + str(e))
                                    #self.setText("Error = " + str(e))
                                    out("Error = " + str(e), outFile)
                                #self.setText("............................................................")
                                self.text_queue.put("............................................................")
                                out("............................................................", outFile)
                                sql_var = ""
                                out_display_str = ""
                            else:
                                sql_var = sql_var + line[x]
                        elif line[x] == "/" and inside_quote == 0:
                            self.dlg("wait_for_slash = " + str(wait_for_slash))
                            put_slash = 1
                            if x < line_len - 1 and single_line_comment == 0:
                                if line[x + 1] == "*":
                                    #sql_var = sql_var + line[x]
                                    multi_line_comment = 1
                                    inside_comment = 1
                                    start_new_word = 1
                                    self.dlg("Multi Line Comment On")
                            if inside_comment == 0:
                                curr_delim = "/"
                                check_param = 0
                                check_semicolon_next = 0
                                start_new_word = 1
                                if wait_for_slash == 1 or first_valid_line_char == 0:
                                    wait_for_slash = 0
                                    put_slash = 0
                                    wait_for_semicolon = 0
                                    creating_something = 0
                                    mother_object_indicator = 0
                                    start_new_word = 0
                                    in_proc_or_func = 0
                                    in_pkg = 0
                                    in_trigger = 0
                                    self.dlg(sql_var)
                                    self.dlg("............................................................")
                                    out(out_display_str, outFile)
                                    self.text_queue.put(out_display_str)
                                    #self.setText(out_display_str)
                                    try:
                                        if closeApplication == 1:
                                            break
                                        cur.execute(sql_var)
                                        print(mother_object_name)
                                        dotPresent = mother_object_name.find(".")
                                        if dotPresent == -1:
                                            v_sql = "SELECT 'Line : ' || line || ' - ' || text FROM USER_ERRORS WHERE name = '" + mother_object_name.upper() + "' ORDER BY SEQUENCE"
                                            try:
                                                if closeApplication == 1:
                                                    break
                                                cur.execute(v_sql)
                                                resultSet = cur.fetchall()
                                                if resultSet:
                                                    print("Errors : " + mother_object_type + " " + mother_object_name)
                                                    self.text_queue.put("Errors : " + mother_object_type + " " + mother_object_name)
                                                    for data in resultSet:
                                                        print(data[0])
                                                        self.text_queue.put(' '.join(data[0].split()))
                                                else:
                                                    self.text_queue.put("Done...")
                                            except Exception as e:
                                                #self.setText("Error = " + str(e))
                                                self.text_queue.put("Error While Fetching Error Details = " + str(e))
                                                out("Error = " + str(e), outFile)
                                        else:
                                            owner = mother_object_name[:dotPresent]
                                            oracle_object_name = mother_object_name[dotPresent + 1:]
                                            v_sql = "SELECT 'Line : ' || line || ' - ' || text FROM ALL_ERRORS WHERE owner = '" + owner.upper() + "' AND name = '" + oracle_object_name.upper() + "' ORDER BY SEQUENCE"
                                            try:
                                                if closeApplication == 1:
                                                    break
                                                cur.execute(v_sql)
                                                resultSet = cur.fetchall()
                                                if resultSet:
                                                    print("Errors : " + mother_object_type + " " + mother_object_name)
                                                    self.text_queue.put("Errors : " + mother_object_type + " " + mother_object_name)
                                                    for data in resultSet:
                                                        if closeApplication == 1:
                                                            break
                                                        print(data[0])
                                                        self.text_queue.put(data[0])
                                                else:
                                                    self.text_queue.put("Done...")
                                            except Exception as e:
                                                #self.setText("Error = " + str(e))
                                                self.text_queue.put("Error While Fetching Error Details = " + str(e))
                                                out("Error = " + str(e), outFile)
                                        #self.setText("Done...")
                                        out("Done...", outFile)
                                    except Exception as e:
                                        #self.setText("Error = " + str(e))
                                        self.text_queue.put("Error = " + str(e))
                                        out("Error = " + str(e), outFile)
                                    #self.setText("............................................................")
                                    self.text_queue.put("............................................................")
                                    out("............................................................", outFile)
                                    sql_var = ""
                                    out_display_str = ""
                            if put_slash == 1:
                                sql_var = sql_var + line[x]
                        elif line[x] == "*" and inside_quote == 0 and single_line_comment == 0:
                            sql_var = sql_var + line[x]
                            if x < line_len - 1 and multi_line_comment == 1:
                                if line[x + 1] == "/":
                                    multi_line_comment_flg = 1
                                    skip_next_char = 1
                                    start_new_word = 1
                                    self.dlg("Multi Line Comment Off " + line[x] + line[x+1])
                            if multi_line_comment_flg == 0:
                                curr_delim = "*"
                                check_param = 0
                                first_valid_line_char = 1
                                check_semicolon_next = 0
                                start_new_word = 1
                        elif line[x] == "-" and inside_quote == 0:
                            sql_var = sql_var + line[x]
                            if x < line_len - 1 and multi_line_comment == 0:
                                if line[x + 1] == "-":
                                    single_line_comment = 1
                                    inside_comment = 1
                                    start_new_word = 1
                                    self.dlg("Single Line Comment On")
                            if inside_comment == 0:
                                curr_word = curr_word + line[x]
                                check_param = 0
                                first_valid_line_char = 1
                                check_semicolon_next = 0
                        elif line[x] == " " and inside_quote == 0 and single_line_comment == 0:
                            sql_var = sql_var + line[x]
                            curr_delim = " "
                            start_new_word = 1
                        elif line[x] == "\n" and inside_quote == 0 and single_line_comment == 0:
                            sql_var = sql_var + line[x]
                            curr_delim = " "
                            start_new_word = 1
                        elif line[x] == "(" and inside_quote == 0 and single_line_comment == 0:
                            sql_var = sql_var + line[x]
                            curr_delim = "("
                            start_new_word = 1
                            check_semicolon_next = 0
                            first_valid_line_char = 1
                            if check_param == 1:
                                check_param = 0
                                check_as_is = 0
                                params_started = 1
                                param_name_next = 1
                        elif line[x] == ")" and inside_quote == 0 and single_line_comment == 0:
                            sql_var = sql_var + line[x]
                            curr_delim = ")"
                            start_new_word = 1
                            check_param = 0
                            first_valid_line_char = 1
                            if params_started == 1:
                                set_param_vars_later = 1
                                # if check_as_is_next == 0:
                                #    check_as_is_next = 1
                                # else:
                                #    check_as_is_next = 0
                                #    check_as_is = 1
                                #    params_started = 0
                        elif line[x] == "=" and inside_quote == 0 and single_line_comment == 0:
                            sql_var = sql_var + line[x]
                            curr_delim = "="
                            start_new_word = 1
                            check_param = 0
                            first_valid_line_char = 1
                            check_semicolon_next = 0
                        elif line[x] == "," and inside_quote == 0 and single_line_comment == 0:
                            sql_var = sql_var + line[x]
                            curr_delim = ","
                            start_new_word = 1
                            check_param = 0
                            check_semicolon_next = 0
                            first_valid_line_char = 1
                        elif inside_quote == 0 and single_line_comment == 0:
                            curr_word = curr_word + line[x]
                            sql_var = sql_var + line[x]
                            check_param = 0
                            first_valid_line_char = 1
                            check_semicolon_next = 0
                        else:
                            sql_var = sql_var + line[x]
                            first_valid_line_char = 1
    
                        if start_new_word == 1:
                            # print(curr_word.strip())
                            start_new_word = 0
                            if len(curr_word.strip()) > 0:
                                prev_word = word
                                word = curr_word.strip()
                                new_word = 1
                            curr_word = ""
                            if inside_comment == 0 and inside_quote == 0 and new_word == 1:
                                new_word = 0
                                self.dlg(word + " check_as_is = " + str(check_as_is) + " obj_nested_cnt = " + str(obj_nested_cnt))
                                if word.lower() == "update" and mother_object_indicator == 0:
                                    updating_something = 1
                                    object_name_next = 1
                                    #print("Inside Update..." + str(mother_object_indicator))
                                    out_display_str = "Line Number : " + str(file_line_number) + "\nUPDATING"
                                elif updating_something == 1:
                                    if object_name_next == 1:
                                        object_name_next = 0
                                        object_name = word
                                        out_display_str = out_display_str + " " + word
                                        if mother_object_indicator == 0:
                                            mother_object_indicator = 1
                                            mother_object_name = object_name
                                            mother_object_type = "TABLE"
                                            if mother_object_type.lower() == "table":
                                                wait_for_semicolon = 1
                                                wait_for_slash = 1
                                elif word.lower() == "insert" and mother_object_indicator == 0:
                                    ins_or_del_something = 1
                                    into_or_from_next = 1
                                    out_display_str = "Line Number : " + str(file_line_number) + "\nINSERTING INTO"
                                elif word.lower() == "delete" and mother_object_indicator == 0:
                                    ins_or_del_something = 1
                                    into_or_from_next = 1
                                    out_display_str = "Line Number : " + str(file_line_number) + "\nDELETING FROM"
                                elif ins_or_del_something == 1:
                                    if into_or_from_next == 1:
                                        into_or_from_next = 0
                                        if word.lower() == "into" or word.lower() == "from":
                                            if mother_object_indicator == 0:
                                                mother_object_type = "TABLE"
                                            object_name_next = 1
                                        else:
                                            object_name = word
                                            print("Deleting...." + word)
                                            if mother_object_indicator == 0:
                                                mother_object_indicator = 1
                                                out_display_str = out_display_str + " " + object_name
                                                mother_object_name = object_name
                                                mother_object_type = "TABLE"
                                                if mother_object_type.lower() == "table":
                                                    wait_for_semicolon = 1
                                                    wait_for_slash = 1
                                                    if curr_delim == ";":
                                                        sql_var = sql_var[:-1]
                                                        wait_for_semicolon = 0
                                                        wait_for_slash = 0
                                                        creating_something = 0
                                                        altering_something = 0
                                                        mother_object_indicator = 0
                                                        proc_or_func_next = 0
                                                        start_new_word = 0
                                                        ins_or_del_something = 0
                                                        deleting_something = 0
                                                        updating_something = 0
                                                        self.dlg(sql_var)
                                                        self.dlg("............................................................")
                                                        out(out_display_str, outFile)
                                                        self.text_queue.put(out_display_str)
                                                        print(sql_var)
                                                        print("About to Exec...")
                                                        #self.setText(out_display_str)
                                                        try:
                                                            cur.execute(sql_var)
                                                            self.text_queue.put("Done...")
                                                            print(mother_object_name)
                                                            #self.setText("Done...")
                                                            out("Done...", outFile)
                                                        except Exception as e:
                                                            self.text_queue.put("Error = " + str(e))
                                                            #self.setText("Error = " + str(e))
                                                            out("Error = " + str(e), outFile)
                                                        #self.setText("............................................................")
                                                        self.text_queue.put("............................................................")
                                                        out("............................................................", outFile)
                                                        sql_var = ""
                                                        out_display_str = ""
                                    elif object_name_next == 1:
                                        object_name_next = 0
                                        object_name = word
                                        if mother_object_indicator == 0:
                                            mother_object_indicator = 1
                                            out_display_str = out_display_str + " " + object_name
                                            mother_object_name = object_name
                                            if mother_object_type.lower() == "table":
                                                wait_for_semicolon = 1
                                                wait_for_slash = 1
                                elif word.lower() == "begin" and mother_object_indicator == 0:
                                    mother_object_indicator = 1
                                    mother_object_name = "BEGIN"
                                    mother_object_type = "ANONYMOUS"
                                    out_display_str = "Line Number : " + str(file_line_number) + "\nEXECUTING ANONYMOUS BLOCK"
                                    in_proc_or_func = 1
                                    obj_body_str = obj_body_str = obj_body_str + "b"
                                    self.dlg("Begin Start")
                                    obj_nested_cnt = obj_nested_cnt + 1
                                    creating_something = 1
                                elif word.lower() == "declare" and mother_object_indicator == 0:
                                    mother_object_indicator = 1
                                    mother_object_name = "DECLARE"
                                    mother_object_type = "ANONYMOUS"
                                    out_display_str = "Line Number : " + str(file_line_number) + "\nEXECUTING ANONYMOUS BLOCK"
                                    creating_something = 1
                                    begin_next = 1
                                    in_proc_or_func = 1
                                elif word.lower() == "alter" and mother_object_indicator == 0:
                                    altering_something = 1
                                    object_type_next = 1
                                    out_display_str = "Line Number : " + str(file_line_number) + "\nALTERING"
                                elif altering_something == 1:
                                    if object_type_next == 1:
                                        object_type_next = 0
                                        object_type = word
                                        if mother_object_indicator == 0:
                                            mother_object_type = object_type
                                            out_display_str = out_display_str + " " + object_type
                                        object_name_next = 1
                                    elif object_name_next == 1:
                                        object_name_next = 0
                                        object_name = word
                                        if mother_object_indicator == 0:
                                            mother_object_indicator = 1
                                            out_display_str = out_display_str + " " + object_name
                                            mother_object_name = object_name
                                            if mother_object_type.lower() == "table" or "package" or "synonym":
                                                wait_for_semicolon = 1
                                                wait_for_slash = 1
                                elif word.lower() == "create" and mother_object_indicator == 0:
                                    creating_something = 1
                                    reset_at_nth_word = 2
                                    out_display_str = "Line Number : " + str(str(file_line_number)) + "\nCREATING"
                                    # for View Create or Replace Force EDITIONABLE View
                                    # for Procedure and Func, Exit when obj_nested_cnt = 0 (No Need of Processing like in case of Package)
                                    # Create Unique Index or Create Index
                                    # Trigger (Does not have as/is)
                                    # Create Sequence Sequence_name
                                    # CREATE OR REPLACE EDITIONABLE/NONEDITIONABLE/PUBLIC SYNONYM Name FOR obj_name
                                    # CREATE DATABASE LINK Name
                                    # Create or Replace directory directory_name as 'Path'
                                    # Create table table_name
                                    # ALTER TABLE CATM_FP_BMPRM_CONFIG_CUSTOM
                                    # Anonymous Block - Declare or Begin
                                    # INSERT INTO CSTB_LABELS
                                    # DELETE FROM CATM_BMPRM_PMT_PARAM_CUSTOM
                                    # UPDATE CATM_FP_BMPRM_CONFIG_CUSTOM
                                    # Commit
                                    # @
                                elif creating_something == 1:
                                    if word.lower() == "or":
                                        wait_for_replace = 1
                                    elif word.lower() == "force" or word.lower() == "editionable" \
                                            or word.lower() == "unique" or word.lower() == "noneditionable" or word.lower() == "public":
                                        if reset_at_nth_word > 0:
                                            reset_at_nth_word += 1
                                    elif wait_for_replace == 1:
                                        wait_for_replace = 0
                                        if word.lower() == "replace":
                                            object_type_next = 1
                                        else:
                                            error_parsing = 1
                                    elif object_type_next == 1:
                                        if word.lower() == "database":
                                            pass
                                        else:
                                            object_type_next = 0
                                            if prev_word.lower() == "database" and word.lower() == "link":
                                                object_type = prev_word + " " + word
                                            else:
                                                object_type = word
                                            if mother_object_indicator == 0:
                                                mother_object_type = object_type
                                                out_display_str = out_display_str + " " + object_type
                                            object_name_next = 1
                                    elif object_name_next == 1:
                                        if word.lower() == "body":
                                            object_type = object_type + " " + word
                                            if mother_object_indicator == 0:
                                                mother_object_type = object_type
                                                out_display_str = out_display_str + " " + word
                                        else:
                                            object_name_next = 0
                                            object_name = word
                                            if mother_object_indicator == 0:
                                                mother_object_indicator = 1
                                                mother_object_name = object_name
                                                out_display_str = out_display_str + " " + object_name
                                                if mother_object_type.lower() == "procedure" or mother_object_type.lower() == "function":
                                                    in_proc_or_func = 1
                                                elif mother_object_type.lower() == "view" or mother_object_type.lower() == "index" \
                                                        or mother_object_type.lower() == "sequence" or mother_object_type.lower() == "synonym" \
                                                        or mother_object_type.lower() == "directory" or mother_object_type.lower() == "table":
                                                    wait_for_semicolon = 1
                                                    wait_for_slash = 1
                                                    self.dlg("Here..." + str(wait_for_semicolon) )
                                                elif mother_object_type.lower() == "trigger":
                                                    in_trigger = 1
                                                elif mother_object_type.lower() == "package" or mother_object_type.lower() == "package body":
                                                    in_pkg = 1
                                            self.lg("object_name = " + object_name)
                                            if curr_delim == "(":
                                                params_started = 1
                                                param_name_next = 1
                                            else:
                                                check_param = 1
                                                check_as_is = 1
                                        self.lg("object_type = " + object_type)
                                    elif params_started == 1:
                                        if word.lower() == "default":
                                            default_value_next = 1
                                        elif default_value_next == 1:
                                            default_value_next = 0
                                        elif param_name_next == 1:
                                            param_name_next = 0
                                            param_name = word
                                            self.lg("param_name = " + param_name)
                                            param_dir_next = 1
                                        elif param_dir_next == 1:
                                            param_dir_next = 0
                                            self.dlg("Here Checking Dir")
                                            if word.lower() == "in" or word.lower() == "out":
                                                param_dir = word
                                                self.lg("param_dir = " + param_dir)
                                                param_type_next = 1
                                            else:
                                                param_type = word
                                                self.lg("param_type = " + param_type)
                                                param_dir = "IN"
                                                self.lg("param_dir = " + param_dir)
                                                param_name_next = 1
                                        elif param_type_next == 1:
                                            if word.lower() == "out":
                                                param_dir = param_dir + " " + word
                                                self.lg("Param Dir : " + param_dir)
                                            else:
                                                param_type_next = 0
                                                param_type = word
                                                self.lg("param_type = " + param_type)
                                                self.lg("param_dir = " + param_dir)
                                                param_name_next = 1
                                    elif check_as_is == 1:
                                        self.dlg("As Is : object_type = " + str(check_as_is) + " " + object_type)
                                        if in_trigger == 1:
                                            if word.lower() == "declare":
                                                check_as_is = 0
                                                begin_next = 1
                                        elif word.lower() == "as" or word.lower() == "is":
                                            check_as_is = 0
                                            self.dlg("As Found")
                                            # if object_type.lower() == "package" or object_type.lower() == "package body":
                                            # if in_pkg == 1:
                                            #    proc_or_func_next = 1
                                            # else:
                                            #    begin_next = 1
                                            begin_next = 1
                                    elif begin_next == 1:
                                        if word.lower() == "begin":
                                            begin_next = 0
                                            obj_body_str = obj_body_str = obj_body_str + "b"
                                            self.dlg("Begin Start... obj_body_str...." + obj_body_str)
                                            obj_nested_cnt = obj_nested_cnt + 1
                                    elif proc_or_func_next == 1:
                                        if word.lower() == "procedure" or word.lower() == "function":
                                            proc_or_func_next = 0
                                            in_pkg_proc_or_func = 1
                                            self.dlg("Found " + word)
                                            object_type = word
                                            object_name_next = 1
                                    elif reset_at_nth_word == 1:
                                        object_type = word
                                        if mother_object_indicator == 0:
                                            mother_object_type = object_type
                                        self.dlg("Here..1")
                                        self.dlg("object_type = " + object_type)
                                        object_name_next = 1
                                    elif obj_nested_cnt > 0:
                                        self.dlg("Here0...")
                                        if next_word_if == 1:
                                            next_word_if = 0
                                            if word.lower() == "if":
                                                obj_nested_cnt = obj_nested_cnt - 1
                                                obj_body_str = obj_body_str[:-1]
                                        elif next_word_loop == 1:
                                            next_word_loop = 0
                                            if word.lower() == "loop":
                                                obj_nested_cnt = obj_nested_cnt - 1
                                                obj_body_str = obj_body_str[:-1]
                                        elif word.lower() == "begin":
                                            obj_body_str = obj_body_str = obj_body_str + "b"
                                            obj_nested_cnt = obj_nested_cnt + 1
                                        elif word.lower() == "if":
                                            obj_body_str = obj_body_str = obj_body_str + "i"
                                            obj_nested_cnt = obj_nested_cnt + 1
                                        elif word.lower() == "loop":
                                            obj_body_str = obj_body_str = obj_body_str + "l"
                                            obj_nested_cnt = obj_nested_cnt + 1
                                        elif word.lower() == "end":
                                            self.dlg("Here...")
                                            word_already_processed = 1
                                            if obj_body_str[len(obj_body_str) - 1] == "b":
                                                obj_nested_cnt = obj_nested_cnt - 1
                                                obj_body_str = obj_body_str[:-1]
                                            elif obj_body_str[len(obj_body_str) - 1] == "i":
                                                next_word_if = 1
                                            elif obj_body_str[len(obj_body_str) - 1] == "l":
                                                next_word_loop = 1
                                        if obj_nested_cnt == 0:
                                            if in_proc_or_func == 1 or in_trigger == 1:
                                                wait_for_slash = 1
                                            else:
                                                proc_or_func_next = 1
                                                #print("proc_or_func_next = " + str(proc_or_func_next))
                                        self.dlg("obj_body_str....." + obj_body_str)
                                    if obj_nested_cnt == 0 and wait_for_slash == 0 and word_already_processed == 0:
                                        if word.lower() == "end":
                                            self.lg("mother_object_type = " + mother_object_type)
                                            self.lg("mother_object_name = " + mother_object_name)
                                            proc_or_func_next = 0
                                            if mother_object_type.lower() == "package" or mother_object_type.lower() == "package body" \
                                                    or mother_object_type.lower() == "procedure" or mother_object_type.lower() == "function":
                                                self.dlg("Here...3")
                                                wait_for_slash = 1
    
                                if reset_at_nth_word > 0:
                                    reset_at_nth_word -= 1
                        if set_param_vars_later == 1:
                            set_param_vars_later = 0
                            param_name_next = 0
                            check_as_is = 1
                            params_started = 0
                            check_semicolon_next = 1
    
                        if word_already_processed == 1:
                            word_already_processed = 0
    
                    if single_line_comment == 1:
                        single_line_comment = 0
                        self.dlg("Single Line Comment Off")
                        if multi_line_comment == 0:
                            inside_comment = 0
    
                    if multi_line_comment_flg == 1:
                        multi_line_comment_flg = 0
                        multi_line_comment = 0
                        inside_comment = 0
                        
            cur.close()
            con.close()
            
    def get_description(self, param_name):
        self.dlg("In get_description...")
        words = re.split('_', param_name)
        desc = ""
        #self.dlg(words)
        for x in range(0, len(words)):
            if words[x].lower() == 'p' and x == 0:
                pass
            elif keyValue:
                if words[x].lower() in keyValue:
                    desc = desc + keyValue[words[x].lower()] + " "
                else:
                    desc = desc + words[x] + " "
            else:
                desc = desc + words[x] + " "
        self.dlg(desc.strip())
        return desc.strip()

    def process_function(self, word):
        global multiLineComment
        global insideProcedure
        global insideFunction
        global targetNameNext
        global parameterNameNext
        global parameterTypeNext
        global parameterDirectionNext
        global returnTypeNext
        global functionDeclareNext
        global functionBodyNext
        global waitForNextWord
        global stopReadingParams
        global output
        global description
        global checkNoBody
        global checkEnd
        global skipNextWord
        global beginBlockStarted

        self.dlg("In process_function...")
        skipNextCode = 0
        self.dlg("checkNoBody = " + str(checkNoBody))
        if checkNoBody == 1:
            checkNoBody = 0
            if word.lower() == "procedure":
                self.dlg("if word is procedure = " + word)
                insideProcedure = 1
                insideFunction = 0
                targetNameNext = 1
                stopReadingParams = 0
                parameterNameNext = 0
                checkEnd = 0
                skipNextCode = 1
                self.text_queue.put("")
                out("", outFile)
            elif word.lower() == "function":
                self.dlg("if word is function = " + word)
                insideFunction = 1
                insideProcedure = 0
                targetNameNext = 1
                stopReadingParams = 0
                parameterNameNext = 0
                checkEnd = 0
                skipNextCode = 1
                self.text_queue.put("")
                out("", outFile)

        if checkEnd == 1:
            checkEnd = 0
            if word.lower() == "if" or word.lower() == "loop":
                skipNextCode = 1

        if skipNextCode == 1 or skipNextWord == 1:
            skipNextCode = 0
            skipNextWord = 0
        elif len(word) == 0:
            pass
        elif word.lower() == "begin" and stopReadingParams == 1:
            functionBodyNext += 1
            beginBlockStarted = 1
            self.dlg("2 " + str(functionBodyNext))
        elif word.lower() == "if" and beginBlockStarted == 1:
            functionBodyNext += 1
            self.dlg("2 " + str(functionBodyNext))
        elif word.lower() == "loop" and beginBlockStarted == 1:
            functionBodyNext += 1
            self.dlg("2 " + str(functionBodyNext))
        elif word.lower() == "end" and beginBlockStarted == 1:
            functionBodyNext -= 1
            checkEnd = 1
            self.dlg("3 " + str(functionBodyNext))
            if functionBodyNext == 0:
                self.dlg("Function End")
                insideFunction = 0
                beginBlockStarted = 0
        elif stopReadingParams == 1:
            pass
        elif word.lower() == "return":
            parameterNameNext = 0
            returnTypeNext = 1
            self.dlg("1 2 3 = " + str(returnTypeNext))
        elif word.lower() == "default":
            if singleQuoteInLine == 0 and parameterNameNext == 1:
                skipNextWord = 1
        elif waitForNextWord == 1:
            waitForNextWord = 0
            if word.lower() == "out":
                output = output + ' ' + word + ','
                parameterTypeNext = 1
            else:
                # checkNoBody = 1
                parameterType = word
                output = output + ',' + parameterType + "," + description
                out(output, outFile)
                self.text_queue.put(output)
                parameterNameNext = 1
        elif targetNameNext == 1:
            functionName = word
            self.dlg("Function : " + functionName)
            out("Function : " + functionName, outFile)
            self.text_queue.put("Function : " + functionName)
            targetNameNext = 0
            parameterNameNext = 1
        elif parameterNameNext == 1:
            parameterName = word
            description = self.get_description(parameterName)
            self.dlg(parameterName)
            output = parameterName + ","
            parameterNameNext = 0
            parameterDirectionNext = 1
        elif parameterDirectionNext == 1:
            parameterDirection = word
            parameterDirectionNext = 0
            if parameterDirection.lower() == "in":
                waitForNextWord = 1
                output = output + parameterDirection
            elif parameterDirection.lower() == "out":
                output = output + parameterDirection + ","
                parameterTypeNext = 1
            else:
                output = output + "IN," + word + "," + description
                out(output, outFile)
                self.text_queue.put(output)
                parameterNameNext = 1
        elif parameterTypeNext == 1:
            self.dlg("checkNoBody Here = " + str(checkNoBody))
            parameterType = word
            output = output + parameterType + "," + description
            out(output, outFile)
            self.text_queue.put(output)
            parameterTypeNext = 0
            parameterNameNext = 1
        elif returnTypeNext == 1:
            functionRetType = word
            self.dlg("Return Type : " + functionRetType + "\n")
            self.text_queue.put("Return Type : " + functionRetType)
            self.text_queue.put("")
            out("Return Type : " + functionRetType, outFile)
            out("", outFile)
            checkNoBody = 1
            returnTypeNext = 0
            stopReadingParams = 1

    def process_procedure(self, word):
        global multiLineComment
        global insideProcedure
        global insideFunction
        global targetNameNext
        global parameterNameNext
        global parameterTypeNext
        global parameterDirectionNext
        global procedureDeclareNext
        global procedureBodyNext
        global waitForNextWord
        global stopReadingParams
        global output
        global description
        global checkNoBody
        global checkEnd
        global skipNextWord
        global beginBlockStarted
        self.dlg("In process_procedure...")
        skipNextCode = 0
        self.dlg("checkNoBody = " + str(checkNoBody))
        if checkNoBody == 1:
            checkNoBody = 0
            if word.lower() == "procedure":
                self.dlg("Checking if Procedure : " + word)
                insideProcedure = 1
                insideFunction = 0
                targetNameNext = 1
                stopReadingParams = 0
                parameterNameNext = 0
                checkEnd = 0
                skipNextCode = 1
                out("", outFile)
                self.text_queue.put("")
            elif word.lower() == "function":
                insideFunction = 1
                insideProcedure = 0
                targetNameNext = 1
                stopReadingParams = 0
                parameterNameNext = 0
                checkEnd = 0
                skipNextCode = 1
                out("", outFile)
                self.text_queue.put("")

        if checkEnd == 1:
            checkEnd = 0
            if word.lower() == "if" or word.lower() == "loop":
                skipNextCode = 1

        if skipNextCode == 1 or skipNextWord == 1:
            skipNextCode = 0
            skipNextWord = 0
        elif len(word) == 0:
            pass
        elif word.lower() == "begin" and stopReadingParams == 1:
            procedureBodyNext += 1
            beginBlockStarted = 1
            self.dlg("2 " + str(procedureBodyNext))
        elif  word.lower() == "if" and beginBlockStarted == 1:
            procedureBodyNext += 1
            self.dlg("2 " + str(procedureBodyNext))
        elif word.lower() == "loop" and beginBlockStarted == 1:
            procedureBodyNext += 1
            self.dlg("2 " + str(procedureBodyNext))
        elif word.lower() == "end" and beginBlockStarted == 1:
            procedureBodyNext -= 1
            checkEnd = 1
            self.dlg("3 " + str(functionBodyNext))
            if procedureBodyNext == 0:
                self.dlg("Procedure End")
                insideProcedure = 0
                beginBlockStarted = 0
        elif word.lower() == "default":
            if singleQuoteInLine == 0 and parameterNameNext == 1:
                skipNextWord = 1
        elif stopReadingParams == 1:
            pass
        elif word.lower() == "is" or word.lower() == "as":
            parameterNameNext = 0
            stopReadingParams = 1
            out("", outFile)
            self.text_queue.put("")
        elif waitForNextWord == 1:
            waitForNextWord = 0
            if word.lower() == "out":
                output = output + ' ' + word + ','
                parameterTypeNext = 1
            else:
                checkNoBody = 1
                parameterType = word
                output = output + ',' + parameterType + "," + description
                out(output, outFile)
                self.text_queue.put(output)
                parameterNameNext = 1
        elif targetNameNext == 1:
            procedureName = word
            out("Procedure : " + procedureName, outFile)
            self.text_queue.put("Procedure : " + procedureName)
            targetNameNext = 0
            parameterNameNext = 1
            checkNoBody = 1
        elif parameterNameNext == 1:
            parameterName = word
            self.dlg(parameterName)
            description = self.get_description(parameterName)
            self.dlg(description)
            output = parameterName + ","
            parameterNameNext = 0
            parameterDirectionNext = 1
        elif parameterDirectionNext == 1:
            parameterDirection = word
            parameterDirectionNext = 0
            if parameterDirection.lower() == "in":
                waitForNextWord = 1
                output = output + parameterDirection
            elif parameterDirection.lower() == "out":
                output = output + parameterDirection + ","
                parameterTypeNext = 1
            else:
                checkNoBody = 1
                output = output + "IN," + word + "," + description
                out(output, outFile)
                self.text_queue.put(output)
                parameterNameNext = 1
        elif parameterTypeNext == 1:
            checkNoBody = 1
            self.dlg("checkNoBody Here = " + str(checkNoBody))
            parameterType = word
            output = output + parameterType + "," + description
            out(output, outFile)
            self.text_queue.put(output)
            parameterTypeNext = 0
            parameterNameNext = 1

    def processFile(self, fullFileName):
        global multiLineComment
        global insideFunction
        global targetNameNext
        global parameterNameNext
        global parameterTypeNext
        global parameterDirectionNext
        global returnTypeNext
        global functionDeclareNext
        global functionBodyNext
        global waitForNextWord
        global stopReadingParams
        global insideProcedure
        global procedureDeclareNext
        global procedureBodyNext
        global output
        global description
        global singleQuoteStart
        global checkNoBody
        global checkEnd
        global skipNextWord
        global singleQuoteInLine
        global prevChar
        global currChar
        global skipFileValidations
        global beginBlockStarted
        global closeApplication
        fileName = fullFileName
        fileValidations = 0
        firstValidWord = 0
        invalidFile = 0
        self.lg("skipFileValidations : " + skipFileValidations)
        out("Processing : " + fileName, outFile)
        out("", outFile)
        self.text_queue.put("Processing : " + fileName)
        self.text_queue.put("")

        if skipFileValidations == str(1):
            fileValidations = 5
            firstValidWord = 1
            self.dlg("firstValidWord " + str(firstValidWord))

        with open(fileName) as f:
            for line in f:
                if closeApplication == 1:
                    break
                cleanLine = ""
                cleanerLine = ""
                finalLine = ""
                cleanLine = ' '.join(line.split())
                # Find and Remove Multi Line Comments in cleanLine
                if multiLineComment > 0:
                    multiLnCmtPosEnd = cleanLine.find("*/")
                    if multiLnCmtPosEnd == -1:
                        cleanerLine = ""
                    elif multiLnCmtPosEnd >= 0:
                        cleanerLine = cleanLine[multiLnCmtPosEnd + 2:]
                        multiLineComment = 0
                elif multiLineComment == 0:
                    multiLnCmtPosSt = cleanLine.find("/*")
                    multiLnCmtPosStEnd = cleanLine.find("*/")
                    if multiLnCmtPosSt == -1:
                        cleanerLine = cleanLine
                    elif multiLnCmtPosSt >= 0:
                        cleanerLine = cleanLine[:multiLnCmtPosSt]
                        multiLineComment = 1
                        if multiLnCmtPosStEnd > 0:
                            cleanerLine = cleanerLine + cleanLine[multiLnCmtPosStEnd + 2:]
                            multiLineComment = 0
                # Remove text in Single Quotes
                lineWoSingleQuotes = ""
                singleQuoteInLine = 0
                for i in range(0, len(cleanerLine)):
                    currChar = cleanerLine[i]
                    singleLinCmt = prevChar + currChar
                    if singleLinCmt == "--" and singleQuoteStart == 0:
                        lineWoSingleQuotes = lineWoSingleQuotes.rstrip("-")
                        #self.dlg("lineWoSingleQuotes = " + lineWoSingleQuotes)
                        break
                    if cleanerLine[i] == "'" and singleQuoteStart == 0:
                        singleQuoteStart = 1
                        #self.dlg("singleQuoteStart = " + str(singleQuoteStart))
                        singleQuoteInLine = 1
                    elif cleanerLine[i] == "'" and singleQuoteStart == 1:
                        singleQuoteStart = 0
                        #self.dlg("singleQuoteStart = " + str(singleQuoteStart))
                        singleQuoteInLine = 1
                    elif singleQuoteStart == 0:
                        lineWoSingleQuotes = lineWoSingleQuotes + cleanerLine[i]
                        #self.dlg(lineWoSingleQuotes)
                    prevChar = currChar
                # Find and Remove Single Line Comments in cleanLine
                if len(lineWoSingleQuotes) > 0:
                    singleLnCmtPos = lineWoSingleQuotes.find("--")
                    if singleLnCmtPos == -1:
                        finalLine = lineWoSingleQuotes
                        self.dlg(finalLine)
                    elif singleLnCmtPos >= 0:
                        finalLine = lineWoSingleQuotes[:singleLnCmtPos]
                        self.dlg(finalLine)
                # All Comments Removed. Processing can start.
                if len(finalLine) > 0:
                    self.dlg(finalLine)
                    # Check if function
                    words = re.split(' |,|;|\(|\)|\n', finalLine)
                    # print(words)
                    for x in range(0, len(words)):
                        if len(words[x]) > 0:
                            if firstValidWord == 0:
                                firstValidWord = 1
                                #print("Here0")
                                if fileValidations == 0:
                                    if words[x].lower() == "create":
                                        fileValidations = 1
                                        #print("Here1")
                                    else:
                                        invalidFile = 1
                                        #print("Here-1" + words[x])
                            elif fileValidations == 1:
                                if words[x].lower() == "or":
                                    #print("Here2")
                                    fileValidations = 2
                                elif words[x].lower() == "package" or words[x].lower() == "procedure" or words[x].lower() == "function":
                                    fileValidations = 5
                                    #print("Here3")
                                    if words[x].lower() == "function":
                                        insideFunction = 1
                                        targetNameNext = 1
                                        stopReadingParams = 0
                                        checkEnd = 0
                                        self.dlg("In a Function")
                                    elif words[x].lower() == "procedure":
                                        insideProcedure = 1
                                        targetNameNext = 1
                                        stopReadingParams = 0
                                        checkEnd = 0
                                        self.dlg("In a Procedure")
                                else:
                                    invalidFile = 1
                                    #print("Here-3")
                            elif fileValidations == 2:
                                if words[x].lower() == "replace":
                                    fileValidations = 3
                                    #print("Here4")
                                else:
                                    invalidFile = 1
                                    #print("Here-4")
                            elif fileValidations == 3:
                                if words[x].lower() == "package" or words[x].lower() == "procedure" or words[x].lower() == "function":
                                    fileValidations = 5
                                    self.lg("File Validations Completed Sucessfully")
                                    if words[x].lower() == "function":
                                        insideFunction = 1
                                        targetNameNext = 1
                                        stopReadingParams = 0
                                        checkEnd = 0
                                        self.dlg("In a Function")
                                    elif words[x].lower() == "procedure":
                                        insideProcedure = 1
                                        targetNameNext = 1
                                        stopReadingParams = 0
                                        checkEnd = 0
                                        self.dlg("In a Procedure")
                                else:
                                    invalidFile = 1
                            elif insideFunction == 1:
                                #print("Func : " + str(insideFunction) + "," + str(functionBodyNext) + "," + words[x] + "," + finalLine)
                                self.process_function(words[x])
                            elif insideProcedure == 1:
                                self.dlg ("Proc : " + str(insideProcedure) + "," + str(procedureBodyNext) + "," + words[x] + "," + finalLine)
                                self.process_procedure(words[x])
                            else:
                                if words[x].lower() == "function":
                                    insideFunction = 1
                                    targetNameNext = 1
                                    stopReadingParams = 0
                                    checkEnd = 0
                                    self.dlg("In a Function")
                                elif words[x].lower() == "procedure":
                                    insideProcedure = 1
                                    targetNameNext = 1
                                    stopReadingParams = 0
                                    checkEnd = 0
                                    self.dlg("In a Procedure")
                            if invalidFile == 1:
                                self.lg("File Validations Failed...")
                                break
                if invalidFile == 1:
                    break

        if invalidFile == 1:
            out("Invalid File " + fileName, outFile)
            out("", outFile)
            self.text_queue.put("Invalid File : " + fileName)
            self.text_queue.put("")
    
    # Calls the File Processor : Extract Metadata from Pkgs
    def launchFileProcessor(self, fileName):
        #global outFileLoc
        global outFile
        self.lg("In launchFileProcessor...")
        if createOneFile == 0:
            baseFileName = os.path.basename(fileName)
            baseFileNameNoExt = ('.').join(baseFileName.split('.')[:-1])
            outFile = CommonParams.outFileLoc + "\\" + baseFileNameNoExt + "_Out.csv"
            out_initialize(outFile)
        self.processFile(fileName)
        
    # Calls Methods to Extraxt Metadata from PLSQL Scripts
    def process(self):
        # global fileOrDir
        global skipFileValidations
        isError = 0
        self.status_queue.put("Processing...")
        self.lg("In process...")
        self.text_queue.put("~~~Empty~Text~Area~~~")
        self.lg("Console Cleared..")
        outFile = CommonParams.outFileLoc + "\\SqlTool_Output.csv"
        out_initialize(outFile)
        skipFileValidations = sqlLite.getParamValue("PROCESS", "skip_file_validations", CommonParams.settingsDb)
        self.lg("skipFileValidations = " + skipFileValidations)
        if skipFileValidations == "Not_Found":
            skipFileValidations = "0"
            sqlLite.setParamValue("PROCESS", "skip_file_validations", "0", CommonParams.settingsDb)

        inc_patterns = sqlLite.getParamValue("PROCESS", "inc_patterns", CommonParams.settingsDb)
        self.lg("inc_patterns = " + inc_patterns)
        if inc_patterns == "Not_Found":
            inc_patterns = "*.sql"
            sqlLite.setParamValue("PROCESS", "inc_patterns", inc_patterns, CommonParams.settingsDb)

        patternList = inc_patterns.split(";")

        exc_patterns = sqlLite.getParamValue("PROCESS", "exc_patterns", CommonParams.settingsDb)
        self.lg("exc_patterns = " + exc_patterns)
        if exc_patterns == "Not_Found":
            sqlLite.setParamValue("PROCESS", "exc_patterns", exc_patterns, CommonParams.settingsDb)

        if exc_patterns != "Not_Found":
            excPatternList = exc_patterns.split(";")

        if CommonParams.fileOrDir == 1:
            fileExists = str(os.path.exists(self.gui.dirname))
            if fileExists == "True":
                for baseFolder, subFolder, files in os.walk(self.gui.dirname):
                    if closeApplication == 1:
                        break
                    if not files:
                        continue
                    for p in patternList:
                        if closeApplication == 1:
                            break
                        filteredFiles = fnmatch.filter(files, p)
                        for item in filteredFiles:
                            skip_loop = False
                            if exc_patterns != "Not_Found":
                                for e in excPatternList:
                                    self.lg("File = " + item + ", Ex Filter = " + e)
                                    toExclude = fnmatch.fnmatch(item, e)
                                    if toExclude:
                                        skip_loop = True
                                        break

                            if skip_loop == False:
                                self.fileNamePath = str(os.path.normpath(os.path.join(baseFolder, item)))
                                # fileNamePath = str(files)
                                self.lg("self.fileNamePath : " + self.fileNamePath)
                                # self.l2.config(text=fileNamePath)
                                if self.gui.showFullPath.get() == 0:
                                    dispFileName = os.path.basename(self.fileNamePath)
                                else:
                                    dispFileName = self.fileNamePath
                                #self.setText("Processing... " + dispFileName)
                                self.launchFileProcessor(self.fileNamePath)
            else:
                self.status_queue.put("Directory Does not Exists. " + self.gui.dirname)
                isError = 1
        else:
            fileExists = str(os.path.exists(self.gui.filename))
            if fileExists == "True":
                #self.setText("Processing File : " + self.gui.filename)
                self.launchFileProcessor(self.gui.filename)
            else:
                self.status_queue.put("File Does not Exists. " + self.gui.filename)
                isError = 1
        if isError == 0:
            self.status_queue.put("Ready.")
        self.gui.lockScreen = 0
    
    def endApplication(self):
        self.running = 0
        
def callback():
    global closeApplication
    print("Quitting...")
    closeApplication = 1
    root.destroy()
    

root = Tk()

print("script: sys.argv[0] is", str(sys.argv[0]))
print("script: __file__ is", repr(__file__))
print("script: cwd is", str(os.getcwd()))
print("script: cwd is", str(os.getcwd()))
#settingsFileName = myLocation + "\\cfg\\settings.cfg"

CommonParams.myLocation = str(os.getcwd())
CommonParams.appHomeLocation = str(os.path.dirname(os. getcwd()))
CommonParams.configFileName = CommonParams.appHomeLocation + "\\cfg\\config.cfg"
CommonParams.settingsDb = CommonParams.appHomeLocation + "\\cfg\\settings.db"
CommonParams.logFileLoc = CommonParams.appHomeLocation + "\\log"
CommonParams.outFileLoc = CommonParams.appHomeLocation + "\\out"

log_location = sqlLite.getParamValue("APPLICATION", "log_location", CommonParams.settingsDb)
if os.path.exists(log_location):
    CommonParams.logFileLoc = log_location
    
detailedLogs = sqlLite.getParamValue("APPLICATION", "deep_log", CommonParams.settingsDb)

out_location = sqlLite.getParamValue("APPLICATION", "out_location", CommonParams.settingsDb)
if os.path.exists(out_location):
    CommonParams.outFileLoc = out_location

consolidate_out = sqlLite.getParamValue("APPLICATION", "consolidate_out", CommonParams.settingsDb)

logFile = CommonParams.logFileLoc + "\\logfile.log"
CommonParams.logFile = logFile
print("logFile = " + logFile)
log_initialize(logFile)

if str(consolidate_out) == str("0"):
    createOneFile = 0
else:
    createOneFile = 1
    outFile = CommonParams.outFileLoc + "\\SqlTool_Output.csv"
    out_initialize(outFile)

# os.environ["PATH"] = CommonParams.appHomeLocation + "\\OracleClient\\instantclient-basic-nt-12.2.0.1.0\\instantclient_12_2;" + os.environ["PATH"]
os.environ["PATH"] = CommonParams.appHomeLocation + "\\OracleClient\\Client;" + os.environ["PATH"]
#print(os.environ["PATH"])

osUser = os.getlogin()
machineId = subprocess.check_output('wmic csproduct get uuid').decode('utf8').split('\n')[1].strip()

storedMachineId = sqlLite.getParamValue("ALL", "machine_id", CommonParams.settingsDb)
#print(machineId + " " + storedMachineId)
if storedMachineId == "Not_Found" or storedMachineId != machineId:
    storedMachineId = machineId
    sqlLite.setParamValue("ALL", "machine_id", storedMachineId, CommonParams.settingsDb)
    sqlLite.delAllPasswords(CommonParams.settingsDb)

#print(str("skipFileValidations " + str(skipFileValidations)))

fh = FileHandler.FileHandler()
keyValue = fh.parse_config(CommonParams.configFileName)
log("keyValue = " + str(keyValue), logFile)

#f = SQLTool(root)
f = ThreadedClient(root)

root.protocol("WM_DELETE_WINDOW", callback)

root.mainloop()
