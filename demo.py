#!/usr/bin/env python

import os
import sys
import optparse
import pymongo
from pymongo import MongoClient
import xml.etree.ElementTree as ET
from urllib2 import urlopen

try: 
    conn = pymongo.MongoClient('mongodb://admin:password@localhost:27017/')
    print("Connected successfully!!!") 
except:   
    print("Could not connect to MongoDB") 

#get a client
client = MongoClient()
db = conn.aacmdatabase
coll1 = db["collezione1"]
coll2 = db["collezione2"]
coll1.drop()
coll2.drop()

# we need to import some python modules from the $SUMO_HOME/tools directory
if 'SUMO_HOME' in os.environ:
    tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
    sys.path.append(tools)
else:
    sys.exit("please declare environment variable 'SUMO_HOME'")


from sumolib import checkBinary  # Checks for the binary in environ vars
import traci


def get_options():
    opt_parser = optparse.OptionParser()
    opt_parser.add_option("--nogui", action="store_true",
                         default=False, help="run the commandline version of sumo")
    options, args = opt_parser.parse_args()
    return options


# contains TraCI control loop
def run():
    step = 0
    while traci.simulation.getMinExpectedNumber() > 0:
        traci.simulationStep()
        #print(step)
        #tempo di attesa su specifico edge=strada
        waiting_time = traci.edge.getWaitingTime("1to2")
        waiting_time2 = traci.edge.getWaitingTime("2to1")
        #print(waiting_time)
        #get id veicolo su specifico edge
        veh_id=traci.edge.getLastStepVehicleIDs("7to1")
        #get emission su spec edge
        emission= traci.edge.getCO2Emission("1to2")
        if float(emission)>10000:
            for id_veicolo in veh_id:
                print(id_veicolo)
                print("EMISSIONI CO2 ELEVATE SULLA STRADA CHE STAI PER PRENDERE")
                print(emission)
        
        if float(waiting_time)>10:
            #print("WAITING")
            #get id veicolo su specifico edge
            veh_id=traci.edge.getLastStepVehicleIDs("7to1")
            for id_veicolo in veh_id:
                #print(id_veicolo)
                #cambio di direzione per veicolo selezionato
                traci.vehicle.changeTarget(id_veicolo, "4to3")
            #id veicoli provenienti dalla sinistra dell'intersezione 1
            veh_id3=traci.edge.getLastStepVehicleIDs("6to1")
            for id_veicolo3 in veh_id3:
                #print(id_veicolo3)
                #cambio di direzione per veicolo selezionato
                traci.vehicle.changeTarget(id_veicolo3, "4to3")

        if float(waiting_time2)>10:
            #id veicoli sopra l'intersezione 2
            veh_id2=traci.edge.getLastStepVehicleIDs("8to2")
            for id_veicolo2 in veh_id2:
                #print(id_veicolo2)
                #cambio di direzione per veicolo selezionato
                traci.vehicle.changeTarget(id_veicolo2, "3to4")

        step += 1

    traci.close()
    sys.stdout.flush()
          

#get data from xml file and put in mongo db collection
def insert_data_mongo(file_xml,coll):
    tree = ET.parse(file_xml)
    root = tree.getroot()
    lista_mtt=[]
    lista_ms=[]
    lista_mhpv=[]
    lista_mtl=[]
    lista_vs=[]
    lista_msw=[]
    lista_mhpvw=[]
    lista_mdw=[]
    lista_vsw=[]
    lista_misw=[]
    lista_midw=[]
    lista_mtlw=[]
    lista_mongo=[]
    id_order=[]
    for o in range(51):
        id_order.append(o)
    for type_tag in root.findall('interval'):
        meanTravelTime = type_tag.get('meanTravelTime')
        meanSpeed = type_tag.get('meanSpeed')
        meanHaltsPerVehicle = type_tag.get('meanHaltsPerVehicle')
        meanTimeLoss = type_tag.get('meanTimeLoss')
        vehicleSum = type_tag.get('vehicleSum')
        meanSpeedWithin = type_tag.get('meanSpeedWithin')
        meanHaltsPerVehicleWithin = type_tag.get('meanHaltsPerVehicleWithin')
        meanDurationWithin = type_tag.get('meanDurationWithin')
        vehicleSumWithin = type_tag.get('vehicleSumWithin')
        meanIntervalSpeedWithin = type_tag.get('meanIntervalSpeedWithin')
        meanIntervalDurationWithin = type_tag.get('meanIntervalDurationWithin')
        meanTimeLossWithin = type_tag.get('meanTimeLossWithin')

        lista_mtt.append(meanTravelTime)
        lista_ms.append(meanSpeed)
        lista_mhpv.append(meanHaltsPerVehicle)
        lista_mtl.append(meanTimeLoss)
        lista_vs.append(vehicleSum)
        lista_msw.append(meanSpeedWithin)
        lista_mhpvw.append(meanHaltsPerVehicleWithin)
        lista_mdw.append(meanDurationWithin)
        lista_vsw.append(vehicleSumWithin)
        lista_misw.append(meanIntervalSpeedWithin)
        lista_midw.append(meanIntervalDurationWithin)
        lista_mtlw.append(meanTimeLossWithin)
    for i in range(51):
        lista_mongo =[ {"_id": id_order[i],"meanTravelTime": lista_mtt[i],"meanSpeed": lista_ms[i] ,"meanHaltsPerVehicle": lista_mhpv[i], "meanTimeLoss": lista_mtl[i], "vehicleSum": lista_vs[i], "meanSpeedWithin": lista_msw[i],"meanHaltsPerVehicleWithin": lista_mhpvw[i],"meanDurationWithin": lista_mdw[i],"vehicleSumWithin": lista_vsw[i],"meanIntervalSpeedWithin": lista_misw[i],"meanIntervalDurationWithin": lista_midw[i],"meanTimeLossWithin": lista_mtlw[i]}] 
        coll.insert(lista_mongo)

def insert_emission_mongo(file_xml,coll):
    tree = ET.parse(file_xml)
    root = tree.getroot()
    lista_idv=[]
    lista_co2=[]
    lista_fuel=[]
    lista_noise=[]
    lista_type=[]
    lista_lane=[]
    lista_pos=[]
    lista_speed=[]
    lista_emissioni_db=[]
    id_order=[]
    for o in range(51):
        id_order.append(o)
    for type_tag in root.findall('timestep/vehicle'):
        id_v = type_tag.get('id')
        co2 = type_tag.get('CO2')
        fuel = type_tag.get('fuel')
        noise = type_tag.get('noise')
        type_v = type_tag.get('type')
        lane = type_tag.get('lane')
        pos = type_tag.get('pos')
        speed = type_tag.get('speed')
        #append in the lists
        lista_idv.append(id_v)
        lista_co2.append(co2)
        lista_fuel.append(fuel)
        lista_noise.append(noise)
        lista_type.append(type_v)
        lista_lane.append(lane)
        lista_pos.append(pos)
        lista_speed.append(speed)
    for i in range(51):
        lista_emissioni_db =[ {"_id": id_order[i],"id_vehicle": lista_idv[i],"co2": lista_co2[i],"fuel": lista_fuel[i],"noise": lista_noise[i],"type_v": lista_type[i],"lane": lista_lane[i],"position": lista_pos[i],"speed": lista_speed[i]}]
        coll.insert(lista_emissioni_db)

def print_data_from_mongo(coll):
    # Printing the data inserted 
    cursor = coll.find() 
    for record in cursor: 
        print(record)
     
# main entry point
if __name__ == "__main__":
    options = get_options()

    # check binary
    if options.nogui:
        sumoBinary = checkBinary('sumo')
    else:
        sumoBinary = checkBinary('sumo-gui')

    # traci starts sumo as a subprocess and then this script connects and runs
    traci.start([sumoBinary, "-c", "demo.sumocfg",
                             "--tripinfo-output", "tripinfo.xml"])
    run()
    # Insert Data 
    insert_data_mongo("out.xml",coll1)
    insert_emission_mongo("emissioni.xml",coll2)
    #insert_data_mongo("out2.xml",coll2)
    # Printing the data inserted 
    print_data_from_mongo(coll1)
    print_data_from_mongo(coll2)

