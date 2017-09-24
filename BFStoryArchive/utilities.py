def write_to_log(caller, s):

    import datetime
    
    logfile = open("log.txt", "a")
    logfile.write(str(datetime.datetime.now()) + " " + caller + " " + s)
    logfile.close()

def checkAvailability(fetched):    
    return "NoSuchKey" in fetched or "Not Found"  in fetched or "Request Timeout" in fetched or "Gateway Timeout" in fetched or "error" in fetched
