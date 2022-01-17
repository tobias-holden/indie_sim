import sys
import numpy as np

from dtk.utils.core.DTKConfigBuilder import DTKConfigBuilder
from simtools.ExperimentManager.ExperimentManagerFactory import ExperimentManagerFactory
from simtools.ModBuilder import ModBuilder, ModFn
from simtools.SetupParser import SetupParser

sys.path.append('helpers/')
from helpers.load_paths import load_box_paths
from helpers.set_up_indie_grid import setup_simulation
from malaria.reports.MalariaReport import add_event_counter_report, add_filtered_spatial_report

SetupParser.default_block = 'HPC'
datapath, projectpath = load_box_paths()

exp_name = 'bf_indie_basic'

years = 1
reporting_start_day = 1
numseeds = 1

cb = DTKConfigBuilder.from_defaults('MALARIA_SIM')

setup_simulation(cb, years)
add_filtered_spatial_report(cb, start=reporting_start_day, channels=["Population","PCR_Parasite_Prevalence"])

builder = ModBuilder.from_list([[ModFn(DTKConfigBuilder.set_param, 'Run_Number', x)]
                                for x in range(numseeds)
                               ])

# run_sim_args is what the `dtk run` command will look for
run_sim_args = {
    'exp_name': exp_name,
    'config_builder': cb,
    'exp_builder': builder
}

if __name__ == "__main__":
    SetupParser.init()
    exp_manager = ExperimentManagerFactory.init()
    exp_manager.run_simulations(**run_sim_args)
