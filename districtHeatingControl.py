from cassandra.cluster import Cluster
from datetime import *
import json

import pandas as pd
from dateutil import parser
import pytz
from _overlapped import NULL

class HeatingSystem:
    def __init__(self):
        self.outside_temperature = None
        self.district_total_energy = None
        self.district_total_inflow = None
        self.district_inflow_temperature = None
        self.district_outflow_temperature = None
        self.heating_inflow_temperature = None
        self.heating_setpoint_temperature = None
        self.heating_valve_percentage = None
        self.heating_outflow_temperature = None
        self.heating_inflow_pressure = None
        self.heating_outflow_pressure = None
        self.hotwater_inflow_temperature = None
        self.hotwater_setpoint_temperature = None
        self.hotwater_valve_percentage = None
        self.hotwater_outflow_temperature = None
        self.hotwater_total_outflow = None
        self.coldwater_temperature = None
        self.coldwater_flow = None
        self.delta_district_temperature = None
        

class DistrictHeatingControl():


    def __init__(self, session, customer_id, building_id, asset_id, ts_start, ts_end):
        self.session = session
        self.customer_id = customer_id
        self.building_id = building_id
        self.ts_start = ts_start
        self.ts_end = ts_end
        
    def fetch_heating_status (self): 
        query = "SELECT json * FROM eden.current_state WHERE customer_id = %d AND building_id = %d AND asset_id = 6000 \
        AND ts_start = '%s' AND ts_end = '%s'" % (self.customer_id, self.building_id, self.ts_start, self.ts_end)
        print(query)
        rows = self.session.execute(query)
        
        found = False
        self.heating_status = HeatingSystem()
        
        for row in rows:
            heating_system = json.loads(row.json)["heating_system"]
            
            if heating_system is None:
                print('no heating status is found')
                break
            
            self.heating_status.outside_temperature = heating_system["outside_temperature"]
            self.heating_status.district_total_energy = heating_system["district_total_energy"]
            self.heating_status.district_total_inflow = heating_system["district_total_inflow"]
            self.heating_status.district_inflow_temperature = heating_system["district_inflow_temperature"]
            self.heating_status.district_outflow_temperature = heating_system["district_outflow_temperature"]
            self.heating_status.heating_inflow_temperature = heating_system["heating_inflow_temperature"]
            self.heating_status.heating_setpoint_temperature = heating_system["heating_setpoint_temperature"]
            self.heating_status.heating_valve_percentage = heating_system["heating_valve_percentage"]
            self.heating_status.heating_outflow_temperature = heating_system["heating_outflow_temperature"]
            self.heating_status.heating_inflow_pressure = heating_system["heating_inflow_pressure"]
            self.heating_status.heating_outflow_pressure = heating_system["heating_outflow_pressure"]
            self.heating_status.hotwater_inflow_temperature = heating_system["hotwater_inflow_temperature"]
            self.heating_status.hotwater_setpoint_temperature = heating_system["hotwater_setpoint_temperature"]
            self.heating_status.hotwater_valve_percentage = heating_system["hotwater_valve_percentage"]
            self.heating_status.hotwater_outflow_temperature = heating_system["hotwater_outflow_temperature"]
            self.heating_status.hotwater_total_outflow = heating_system["hotwater_total_outflow"]
            self.heating_status.coldwater_temperature = heating_system["coldwater_temperature"]
            self.heating_status.coldwater_flow = heating_system["coldwater_flow"]
            self.heating_status.delta_district_temperature = heating_system["delta_district_temperature"]
            
            found = True
            break
        
        if not found:
            self.heating_status = None
            return
 
    def manipulate_inflow_temperature(self, ):
        