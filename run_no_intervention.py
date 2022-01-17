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
from malaria.interventions.health_seeking import add_health_seeking

SetupParser.default_block = 'HPC'
datapath, projectpath = load_box_paths()

exp_name = 'bf_indie_hs_sweep'

years = 1
reporting_start_day = 1
numseeds = 1

cb = DTKConfigBuilder.from_defaults('MALARIA_SIM')


def add_case_management(cb, coverage):
    # Add Case Management to all nodes (sweep coverage level range)
    add_health_seeking(config_builder=cb, start_day=0, drug=['Artemether', 'Lumefantrine'],
                       targets=[{'trigger': 'NewClinicalCase', 'agemin': 0.25, 'agemax': 100,
                                 'coverage': coverage, 'seek': 1, 'rate': 0.3},
                                {'trigger': 'NewSevereCase', 'agemin': 0.25, 'agemax': 100,
                                 'coverage': coverage, 'seek': 1, 'rate': 0.7}])
    return {'CM_Coverage': coverage}


setup_simulation(cb, years)
add_event_counter_report(cb, event_trigger_list=['Received_Treatment'])
add_filtered_spatial_report(cb, start=reporting_start_day, channels=["Population", "PCR_Parasite_Prevalence",
                                                                     "New_Infections", "New_Clinical_Cases"])

builder = ModBuilder.from_list([[ModFn(DTKConfigBuilder.set_param, 'Run_Number', x),
                                 ModFn(add_case_management, coverage=cov)]
                                for x in range(numseeds)
                                for cov in [0.8]
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
