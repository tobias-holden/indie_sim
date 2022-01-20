import os
import pandas as pd
import copy
from dtk.vector.species import set_species, set_larval_habitat
from dtk.interventions.habitat_scale import scale_larval_habitats
from dtk.interventions.outbreakindividual import recurring_outbreak
from load_paths import load_box_paths

datapath, projectpath = load_box_paths()


def set_up_basic_params(cb, years) :

    cb.update_params({'Enable_Vital_Dynamics': 1,
                      'Enable_Births': 1,
                      'Birth_Rate_Dependence': 'FIXED_BIRTH_RATE',
                      'Disable_IP_Whitelist': 1,
                      'Maternal_Antibodies_Type': 'CONSTANT_INITIAL_IMMUNITY',
                      "Incubation_Period_Distribution": "EXPONENTIAL_DISTRIBUTION",
                      'Parasite_Smear_Sensitivity': 0.02,
                      "Report_Detection_Threshold_Blood_Smear_Parasites": 10,
                      "Report_Detection_Threshold_PCR_Parasites": 0.1,
                      'logLevel_JsonConfigurable': 'ERROR',
                      'logLevel_SusceptibilityMalaria': 'ERROR',
                      'Simulation_Duration': years * 365
                      })


def set_up_input_files(cb, input_file_name) :

    cb.update_params({'Demographics_Filenames': [os.path.join('demographics',
                                                              '%s_demographics.json' % input_file_name)],
                      "Air_Temperature_Filename": os.path.join('climate', '%s_air_temperature_daily.bin' % input_file_name),
                      "Land_Temperature_Filename": os.path.join('climate', '%s_air_temperature_daily.bin' % input_file_name),
                      "Rainfall_Filename": os.path.join('climate', '%s_rainfall_daily.bin' % input_file_name),
                      "Relative_Humidity_Filename": os.path.join('climate', '%s_relative_humidity_daily.bin' % input_file_name),
                      'Age_Initialization_Distribution_Type': 'DISTRIBUTION_COMPLEX'})


def set_up_larval_habitat(cb) :

    set_species(cb, ['gambiae'])

    ls_hab_ref = {'Capacity_Distribution_Number_Of_Years': 1,
                  'Capacity_Distribution_Over_Time': {
                      'Times': [0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334],
                      'Values': [0, 0, 0, 0, 0, 0.001745998, 0.000224616, 0.0015, 0.0004, 0, 0, 0]
                  },
                  'Max_Larval_Capacity': pow(10, 11.55956955)}

    set_larval_habitat(cb, {'gambiae': {'LINEAR_SPLINE': ls_hab_ref,
                                        'CONSTANT': pow(10, 8.267853145)}})

    # handle node-specific habitat scaling
    hab_list = []
    for species_params in cb.get_param("Vector_Species_Params"):
        habitats = species_params["Larval_Habitat_Types"]
        hab_list += [h for (h, v) in habitats.items()]
    hab_list = list(set(hab_list))

    master_df = pd.read_csv(os.path.join(projectpath, 'simulation_inputs', 'demographics', 'nodes.csv'))
    df = master_df.rename(columns={'nodeid': 'NodeID'})[['NodeID', 'habitat_scale']]
    for hab_type in ['TEMPORARY_RAINFALL', 'CONSTANT', 'LINEAR_SPLINE', 'WATER_VEGETATION'] :
        if hab_type in hab_list :
            df[hab_type] = copy.copy(df['habitat_scale'])
    del df['habitat_scale']
    scale_larval_habitats(cb, df)


def set_up_human_migration(cb, input_file_name) :

    cb.update_params({
        # Migration
        'Migration_Model': 'FIXED_RATE_MIGRATION',
        'Migration_Pattern': 'SINGLE_ROUND_TRIPS',

        'Enable_Local_Migration': 1,
        'Local_Migration_Roundtrip_Duration': 5,
        'Local_Migration_Roundtrip_Probability': 1,
        'x_Local_Migration': 0.02,  # 0.1 -> 5 trips per person per year to each node
        'Local_Migration_Filename': 'migration/%s_Local_Migration.bin' % input_file_name,

        'Enable_Regional_Migration': 1,
        'Regional_Migration_Roundtrip_Duration': 30,
        'Regional_Migration_Roundtrip_Probability': 1,
        'x_Regional_Migration': 0.1,  # 0.1 -> 1 trip per person per year from node 1 or 2 to node 3
        'Regional_Migration_Filename': 'migration/%s_Regional_Migration.bin' % input_file_name,
    })


def set_up_vector_migration(cb, input_file_name) :

    cb.update_params({
        'Enable_Vector_Migration': 1,
        "Vector_Migration_Base_Rate": 0.15,
        'Vector_Migration_Food_Modifier': 0,
        'Vector_Migration_Habitat_Modifier': 0,
        'Vector_Migration_Modifier_Equation': 'LINEAR',
        'Vector_Migration_Stay_Put_Modifier': 0,
        'Enable_Vector_Migration_Local': 1,
        'x_Vector_Migration_Local': 0.01,
        'Vector_Migration_Filename_Local': 'migration/%s_Vector_Local_Migration.bin' % input_file_name,
    })


def set_up_biting_risk(cb):
    cb.update_params({
        'Enable_Demographics_Risk': 1,
        'RiskDistributionFlag': 3,   # Flag for Exponential Distribution
        'RiskDistribution1': 1,      # Exponential Decay Rate
        'RiskDistribution2': 0      # Parameter NA for exponential
    })
    

def setup_simulation(cb, years, input_file_name='bf_indie_full_grid', outbreak=True):

    set_up_basic_params(cb, years)
    set_up_input_files(cb, input_file_name=input_file_name)
    #set_up_larval_habitat(cb)
    set_up_biting_risk(cb)
    #set_up_human_migration(cb, input_file_name=input_file_name)
    #set_up_vector_migration(cb, input_file_name=input_file_name)
    if outbreak :
        recurring_outbreak(cb, start_day=180, repetitions=years, tsteps_btwn=365, outbreak_fraction=0.01)
