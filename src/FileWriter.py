def log(text, log_file_name):
    logFile = open(log_file_name,"a")
    logFile.write(text + "\n")
    logFile.close()
    
def deepLog(text, log_file_name):
    logFile = open(log_file_name,"a")
    logFile.write(text + "\n")
    logFile.close()

def log_initialize(log_file_name):
    logFile = open(log_file_name,"w+")
    logFile.close()


def out(text, out_file_name):
    outFile = open(out_file_name,"a")
    outFile.write(text + "\n")
    outFile.close()


def out_initialize(out_file_name):
    outFile = open(out_file_name,"w+")
    outFile.close()

    

#logFile = r"D:\Data\Work\Active\Py\log\logfile.log"
#log_initialize(logFile)
#
#log("My First Log Out", 1, logFile)
#log("My Second Log Out", 1, logFile)
#
#outFile = r"D:\Data\Work\Active\Py\out\output.csv"
#out_initialize(outFile)
#
#out("Hello,How,Are,You", outFile)
#out("I,Am,Good", outFile)

#import shutil
#shutil.copy(r'C:\Users\skpraman\Desktop\tmp\Code Drop\Code_Drop_16_Mar_2018\MAIN\CORE\SQL\capks_cadbmprm_custom.sql', r'\\XX.XXX.XXX.202\Wellsfargo\Sunil\Test')
