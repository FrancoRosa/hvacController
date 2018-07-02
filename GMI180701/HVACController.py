import psycopg2,time,datetime,minimalmodbus

import serial, threading, pickle
from threading import Lock, Thread
from time import sleep, ctime, localtime, strftime
from flask import Flask, request, redirect


#######################################################
#######################################################
# Data Base config
Host=  'codeado.com'     # Host of web service 
User=  'postgres'           # User of database
Pass=  'codeadopro'           # Password of database
DBName='db_hvac'    # Name of the database

#######################################################
#######################################################

f_user = "admin" 
f_pass = "1234edi"

# USB Rs485
modport = '/dev/ttyUSB0'
modbaudrate = 9600
connected = False
busy = False
logged = False
RS485Debug = False
# Colors shown in debugging mode
class color: #Prints events on diferent colors for debugging porpouses
    GTX = '\033[95m' # Modem GSM Transmited data    _pink
    GRX = '\033[94m' # Modem GSM Received data      _blue
    DBQ = '\033[92m' # Data Base Queries            _lemon
    DBA = '\033[93m' # Data Base Answers            _yellow
    FUN = '\033[91m' # Function Name                -red

building = '0'
devices = ''
flagOnline = True
flagRS485 = True
floor = 0

configdir = "/home/pi/hvac/"
configfile =  "HVACconfig.pkl"
message=''
buildingID=''
floorID=''
addresses=''
instruments=[]

############################################
############################################
# Reistros Modbus
readfunCode = 3
writefunCode = 16

regTemp1 = 1
regTemp2 = 2
regTemp3 = 3
regHum1  = 4
regCurn  = 5
regInp1  = 6
regInp2  = 7

regSetPointTem = 8
regSetPointHum = 9
regPowerMode =   10
regManualMode =  11

regValve = 12
regFanMt = 13

############################################


def saveConfig():
    with open(configdir+configfile, 'w') as f:  # Python 3: open(..., 'wb')
        pickle.dump([building, floor], f)

def getConfig():
    global building,floor
    with open(configdir+configfile, 'r') as f:
        building, floor = pickle.load(f)

getConfig()


def fanIndex(x):
    return {
        'Off':   0,
        'Low':   1,
        'Medium':2,
        'High':  3,
    }[x[0][0]]

def fanIndexi(x):
    return {
        0:'Off',
        1:'Low',
        2:'Medium',
        3:'High',
    }[x]

def valveIndex(x):
    return {
        True:   1,
        False:  0,
    }[x[0][0]]


def httpStatus():
    return """
    <!DOCTYPE html>
    <html lang="en-us">
        <head>
        <title>HVAC Controller</title>
        <meta http-equiv="refresh" content="10"> 
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        </head>
        <body style="background-color:black">
            <center>
            <font color="lime">
                <h1> HVAC Gateway </h1> 
                <h2>
                    <font color="green">
                    Building: %s              <br>
                    Floor: %d                 <br>
                    </font>
                </h2>
                <h3>
                    <font color="green">
                        Date: %s<br>
                        Time: %s<br>
                    </font>
                </h3>
                
                <h2>
                    <font color="green">
                    Devices: %s<br>
                    Message: %s<br>
                    RS485:  %s
                    </font>
                </h2>

            </font>

            <h3>
                <font color="green">
                    
                    <form action="u_building" method="post">
                        <input style="color:green;background-color:black;border:1px solid #336600;padding:10px" type="text" name = "building">
                        <button style="color:green;background-color:black;border:1px solid #336600;padding:10px">
                        Update Building</button>
                    </form>
                    <br>
                    <form action="u_floor" method="post">
                        <input style="color:green;background-color:black;border:1px solid #336600;padding:10px" type="text" name = "floor">
                        <button style="color:green;background-color:black;border:1px solid #336600;padding:10px">
                        Update Floor</button>
                    </form>
                    <br>
                    <form action="" method="post">
                        <button style="color:green;background-color:black;border:1px solid #336600;padding:10px">
                        refresh</button>
                    </form>
                    <br>
                    <br>
                    <form action="logout" method="post">
                        <button style="color:green;background-color:black;border:1px solid #336600;padding:10px">
                        logout</button>
                    </form>
                    <br>
            </h3>

            </center>
        </body>
    </html>
    """%(building,floor,strftime("%d/%m/%y"),strftime("%H:%M:%S"), repr(addresses), message, flagRS485)

def httpLogin():
    return """
    <!DOCTYPE html>
    <html lang="en-us">
        <head>
        <title>login</title>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        </head>
        <body style="background-color:black">
            <center>
            <font color="lime">
                <h1>login</h1> 
            </font>

            <h3>
                <font color="green">
                    
                    <form action="logintest" method="post">
                        <input style="color:green;background-color:black;border:1px solid #336600;padding:10px" type="text" name = "usr">
                        <br>
                        <input style="color:green;background-color:black;border:1px solid #336600;padding:10px" type="password" name = "pss">
                        <br><br>
                        <button style="color:green;background-color:black;border:1px solid #336600;padding:10px">
                        > > > > </button>
                    </form>
                    <br>
            </h3>

            </center>
        </body>
    </html>
    """

def httpNolog():
    return """
    <!DOCTYPE html>
    <html lang="en-us">
        <head>
        <title>login</title>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        </head>
        <body style="background-color:black">
            <center>
            <font color="lime">
                <h1>access denied</h1> 
            </font>
            </center>
        </body>
    </html>
    """

app = Flask(__name__)

@app.route('/u_building', methods=['GET', 'POST'])
def updateBuilding():
    global building, floor
    if request.method=="POST":
        building = request.form['building']
        if len(building)>2:
            saveConfig()
    return redirect("/")

@app.route('/u_floor', methods=['GET', 'POST'])
def updateFloor():
    global building, floor
    if request.method=="POST":
        try:
            floor = int(request.form['floor'])
            saveConfig()
        except:
            pass
    return redirect("/")

@app.route('/login', methods=['GET', 'POST'])
def login():
    return httpLogin()

@app.route('/logintest', methods=['GET', 'POST'])
def logintest():
    global logged
    if request.method=="POST":
        usr = request.form['usr']
        pss = request.form['pss']
        if usr == f_user and pss == f_pass:
            logged = True
            return redirect("/")
        else:
            logged=False
            return redirect("/nolog")

@app.route('/nolog', methods=['GET', 'POST'])
def nologged():
    return httpNolog()

@app.route('/logout', methods=['GET', 'POST'])
def logout():
    global logged
    logged = False
    return redirect("/")

@app.route('/', methods=['GET', 'POST'])
def home():
    global logged
    if logged:
        getConfig()
        return httpStatus()
    else:
        return httpLogin() 

def createModbusInstruments(addresses):
    try:
        global instruments
        instruments=[]
        for k in addresses:
        
            instrument = minimalmodbus.Instrument(modport, int("%s"%k)) 
            instrument.serial.baudrate = 9600   # Baud
            instrument.serial.bytesize = 8
            instrument.serial.parity   = serial.PARITY_NONE
            instrument.serial.stopbits = 1
            instrument.serial.timeout  = 1   # seconds

            instrument.address     # this is the slave address number
            instrument.mode = minimalmodbus.MODE_RTU   # rtu or ascii mode
            instrument.debug = RS485Debug
            instruments.append(instrument)
        return True
    except:
        print "... Serial Port Error"
        return False

def setModbusPower(slaveAdd,powermode):
    print color.GTX, "... Modbus Power", powermode
    ins = instruments[addresses.index(slaveAdd)]
    if 'On' in powermode: 
        powermodebool = 1
    if 'Off' in powermode:
        powermodebool = 0
    return ins.write_register(regPowerMode,powermodebool,0)

def setModbusControl(slaveAdd,controlmode):
    print color.GTX, "... Modbus setModbusControl", controlmode
    ins = instruments[addresses.index(slaveAdd)]
    if 'Manual' in controlmode[0]: 
        controlmodebool = 0
    if 'Autom' in controlmode[0]:
        controlmodebool = 1
    return ins.write_register(regManualMode,controlmodebool)

def setModbusSetPointTemp(slaveAdd):
    print color.GTX, "... Modbus Setpoint Temp"    
    ins = instruments[addresses.index(slaveAdd)]
    ins.write_register(regSetPointTem,int(10*float(getTargetTemperature(slaveAdd)[0][0])))

def setModbusSetPointHumd(slaveAdd):
    print color.GTX, "... Modbus Setpoint Humd"
    ins = instruments[addresses.index(slaveAdd)]
    ins.write_register(regSetPointHum,int(10*float(getTargetHumidity(slaveAdd)[0][0])))

def setModbusFan(slaveAdd):
    print color.GTX, "... Modbus WriteFanStatus"
    ins = instruments[addresses.index(slaveAdd)]
    ins.write_register(regFanMt,fanIndex(getFan(slaveAdd)))

def setModbusValve(slaveAdd):
    print color.GTX, "... Modbus WriteValveStatus"
    ins = instruments[addresses.index(slaveAdd)]
    ins.write_register(regValve,valveIndex(getValve(slaveAdd)))

def getModbusSensors(slaveAdd):
    print color.GTX, "... Modbus ReadSensors"
    ins = instruments[addresses.index(slaveAdd)]
    #temp1 = ins.read_register(regTemp1)
    temp2 = ins.read_register(regTemp2)
    #temp3 = ins.read_register(regTemp3)
    hum1 = ins.read_register(regHum1)
    curn = ins.read_register(regCurn)
    #inp1 = ins.read_register(regInp1)
    #inp2 = ins.read_register(regInp2)
    #updateTemp1(slaveAdd,temp1)
    print "...%2.2f, %2.2f, %d"%(temp2/10.0,hum1/10.0,curn)
    updateTemp2(slaveAdd,temp2/10.0)
    #updateTemp3(slaveAdd,temp3/10.0)
    updateHum1(slaveAdd,hum1/10.0)
    updateCurrent(slaveAdd,curn)
    #updateInput2(slaveAdd,inp2)

def getModbusFan(slaveAdd):
    print color.GTX, "... Modbus ReadFanStatus"
    ins = instruments[addresses.index(slaveAdd)]
    fan = ins.read_register(regFanMt)
    updateFan(slaveAdd,fanIndexi(fan))

def getModbusValve(slaveAdd):
    print color.GTX, "... Modbus ReadValveStatus"
    ins = instruments[addresses.index(slaveAdd)]
    valve = ins.read_register(regValve)
    updateValve(slaveAdd,bool(valve))

def connect():                      #Connects with database
    global conn
    global cur
    global connected
    while True:
        try:
            conn = psycopg2.connect(dbname=DBName, host=Host, user=User, password=Pass)
            conn.autocommit = True
            cur = conn.cursor()
            print color.FUN, "... db conection success"
            connected = True
            break
        except:
            print color.FUN, "... db conection fail"
            connected = False

        time.sleep(10)

def DBquery(query_text):                #Function to execute Querys to dataBase 
    try:
        #print color.DBQ, query_text            #prints the query text in debug mode 
        return cur.execute(query_text)      #executes query
    except:
        connect()

def DBans():                            #Reads query results and writes result
    try:
        ans_text = cur.fetchall()           
        #print color.DBA, repr(ans_text)
        return ans_text
    except:
        connect()

def getDBData(table, field, keyfield, key):
    c_search = "SELECT %s FROM %s where %s = '%s';"%(field, table, keyfield,key)
    DBquery(c_search)
    return DBans()    

def updateDBData(table, field, value, keyfield, key):
    c_update= "UPDATE %s SET %s = '%s' WHERE %s = '%s'"%(table,field,value,keyfield,key)
    DBquery(c_update)
    
def updateTemp1(addr,value):
    updateDBData("motors_cooler","temperature1","%s"%value,"floor_id=%s and addr"%(floorID),"%s"%addr)

def updateTemp2(addr,value):
    updateDBData("motors_cooler","temperature2","%s"%value,"floor_id=%s and addr"%(floorID),"%s"%addr)

def updateTemp3(addr,value):
    updateDBData("motors_cooler","temperature3","%s"%value,"floor_id=%s and addr"%(floorID),"%s"%addr)

def updateHum1(addr,value):
    updateDBData("motors_cooler","humidity1","%s"%value,"floor_id=%s and addr"%(floorID),"%s"%addr)
    
def updateInput1(addr,value):
    updateDBData("motors_cooler","input1","%s"%value,"floor_id=%s and addr"%(floorID),"%s"%addr)
    
def updateInput2(addr,value):
    updateDBData("motors_cooler","input2","%s"%value,"floor_id=%s and addr"%(floorID),"%s"%addr)
    
def updateFan(addr,value):
    updateDBData("motors_cooler","fan","%s"%value,"floor_id=%s and addr"%(floorID),"%s"%addr)
    
def updateValve(addr,value):
    updateDBData("motors_cooler","valve","%s"%value,"floor_id=%s and addr"%(floorID),"%s"%addr)

def updateCurrent(addr,value):
    updateDBData("motors_cooler","current","%s"%value,"floor_id=%s and addr"%(floorID),"%s"%addr)
    
def getBuildingID(building):
    return getDBData("motors_building", "id", "name", building)[0]

def getFloorID(buildingID,floor):
    return getDBData("motors_floor","id","building_id = %s and level"%buildingID,floor)[0]

def getControllerAddress(floorID):
    return getDBData("motors_cooler","addr","floor_id","%s"%floorID)

def getTargetTemperature(addr):
    return getDBData("motors_cooler","target_temp","floor_id = %s and addr"%floorID,"%s"%addr)

def getTargetHumidity(addr):
    return getDBData("motors_cooler","target_hum","floor_id = %s and addr"%floorID,"%s"%addr)

def getPowerMode(addr):
    return getDBData("motors_cooler","powermode","floor_id = %s and addr"%floorID,"%s"%addr)[0]

def getControlMode(addr):
    return getDBData("motors_cooler","controlmode","floor_id = %s and addr"%floorID,"%s"%addr)

def getValve(addr):
    return getDBData("motors_cooler","valve","floor_id = %s and addr"%floorID,"%s"%addr)

def getFan(addr):
    return getDBData("motors_cooler","fan","floor_id = %s and addr"%floorID,"%s"%addr)

def getTemp1(addr):
    return getDBData("motors_cooler","temperature1","floor_id = %s and addr"%floorID,"%s"%addr)

def getTemp2(addr):
    return getDBData("motors_cooler","temperature2","floor_id = %s and addr"%floorID,"%s"%addr)

def getHum1(addr):
    return getDBData("motors_cooler","humidity1","floor_id = %s and addr"%floorID,"%s"%addr)

def getName(addr):
    return getDBData("motors_cooler","name","floor_id = %s and addr"%floorID,"%s"%addr)

def getCurrent(addr):
    return getDBData("motors_cooler","current","floor_id = %s and addr"%floorID,"%s"%addr)


def getSchedule(addr):
    coolerID = getDBData("motors_cooler","id","floor_id = %s and addr"%floorID,"%s"%addr)[0]
    return getDBData("motors_schedule","day, s_start, s_stop","cooler_id","%s"%coolerID)

def getScheduleStat(addr):
    k = getSchedule(addr)
    for i in k:
        if datetime.datetime.today().weekday() == int(i[0]):
            now = datetime.datetime.now().time()
            if i[1] <= now <= i[2]:
                return 'On'
    return 'Off'

def saveFloorHistory(addr, floorID):
    print "... Saving historic data, Address:", addr
    th = getTargetHumidity(addr)[0][0]
    tt = getTargetTemperature(addr)[0][0]
    pm = getPowerMode(addr)[0]
    cm = getControlMode(addr)[0][0]
    vl = getValve(addr)[0][0]
    fn = getFan(addr)[0][0]
    t1 = getTemp1(addr)[0][0]
    t2 = getTemp2(addr)[0][0]
    h1 = getHum1(addr)[0][0]
    nm = getName(addr)[0][0]
    cn = getCurrent(addr)[0][0]

    dc = strftime("%m/%d/%y")
    tc = strftime("%H:%M:00")
    c_insert = """
    INSERT INTO motors_coolerrecord (datec, timec, addr, name, floor_id,
                                     fan, valve, target_temp, target_hum,
                                     temperature1, temperature2, humidity1,
                                     powermode, controlmode, current)
           VALUES ('%s', '%s', '%s', '%s', '%s',
                   '%s', '%s', '%s', '%s',
                   '%s', '%s', '%s',
                   '%s', '%s', '%s');
    """%(dc,tc,addr[0],nm,floorID[0],fn,vl,tt,th,t1,t2,h1,pm,cm,cn)
    DBquery(c_insert)

def remoteControl():
    global message, buildingID, floorID, addresses, busy
    while True:
        try:
            message=''
            addresses=''
            connect()
            while True:
                time.sleep(10)

                try:
                    buildingID = getBuildingID(building)
                except IndexError:
                    message = "... revisar nombre de edificio"
                    print message
                    continue
                try:
                    floorID = getFloorID(buildingID,floor)
                except IndexError:
                    message = "... revisar nombre de piso"
                    print message
                    continue

                addresses = getControllerAddress(floorID)
                # Para cada direccion leer el modo de funcionamiento
                if len(addresses)>0:
                    counter=100
                    while createModbusInstruments(addresses):
                        message = "... controlando"
                        activedevices = []
                        counter=counter+1
                        for address in addresses:

                            time.sleep(1)
                            print "______________________________" 
                            print "... Address: %s "%address 
                            controlMode = getControlMode(address)
                            powerMode = getPowerMode(address)

                            if "%s"%powerMode=='Schedule':
                                powerMode = getScheduleStat(address)

                            if setModbusPower(address,powerMode)==False:
                                continue
                            
                            if setModbusControl(address,controlMode)==False:
                                continue

                            activedevices.append(address)
                            message = "Activos:%s"%repr(activedevices)

                            if 'Autom' in controlMode[0]:
                                setModbusSetPointTemp(address)
                                setModbusSetPointHumd(address)
                                getModbusFan(address)
                                getModbusValve(address)
                            
                            if 'Manual' in controlMode[0]:
                                setModbusFan(address)
                                setModbusValve(address)
                            
                            getModbusSensors(address)
        
                        
                        if int(strftime("%M"))%10==0 and counter>20:
                            for address in addresses:
                                saveFloorHistory(address,floorID)
                            counter=0
                        
                        time.sleep(5)
                        busy=True
                
                else:
                    message='... no hay controladores registrados'
            time.sleep(10)
        except:
            print color.FUN, "... fatal Error on main loop"
#
Thread(target=remoteControl).start()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
