import glmanip as g
import numpy as np

glm_in = "IEEE_123_feeder_0_DER_demo-recorders_Rev0_old.glm"
glm_out = "IEEE_123_feeder_0_DER_demo-recorders_Rev0.glm"

g.ingest(glm_in)
np.random.seed(0)
for key, house in g.model['house'].items():
    cool_set = np.random.uniform(68,73)
    deadband = np.random.uniform(1, 3)
    air_temp = np.random.uniform(cool_set - deadband/2, cool_set + deadband/2)
    house['cooling_setpoint'] = str(cool_set)
    house['thermostat_deadband'] = str(deadband)
    house['air_temperature'] = str(air_temp)
    house['mass_temperature'] = str(air_temp)
    house['thermostat_off_cycle_time'] = str(1)
    house['thermostat_on_cycle_time'] = str(1)


g.write(glm_out)