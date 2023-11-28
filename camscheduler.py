import subprocess
import datetime
import  os

def isNowInTimePeriod(startTime, endTime, nowTime):
    if datetime.datetime.today().weekday() < 5:
        if startTime < endTime:
            return nowTime >= startTime and nowTime <= endTime
        else: #Over midnight
            return nowTime >= startTime or nowTime <= endTime
    else:
        return False

timeStart = datetime.time(10,30)
timeEnd = datetime.time(18,00)
timeNow = datetime.datetime.now().time()
service_state = os.system('sudo systemctl is-active --quiet firefox_hsecure')
print(timeNow, service_state)

if isNowInTimePeriod(timeStart, timeEnd, timeNow) and service_state != 0:
    proc=subprocess.Popen('sudo systemctl start firefox_hsecure', shell=True, stdout=subprocess.PIPE, )
    output=proc.communicate()[0]
    print(output)
elif not(isNowInTimePeriod(timeStart, timeEnd, timeNow)) and service_state ==0:
    proc=subprocess.Popen('sudo systemctl stop firefox_hsecure', shell=True, stdout=subprocess.PIPE, )
    output=proc.communicate()[0]
    print(output)

