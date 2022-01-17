import os
import pandas as pd
import json
from dtk.tools.demographics.DemographicsGeneratorConcern import WorldBankBirthRateConcern, EquilibriumAgeDistributionConcern, DefaultIndividualAttributesConcern
from dtk.tools.demographics.DemographicsGenerator import DemographicsGenerator
from dtk.tools.climate.ClimateGenerator import ClimateGenerator
from simtools.SetupParser import SetupParser
import sys
sys.path.append('../helpers/')
from load_paths import load_box_paths

datapath, projectpath = load_box_paths()


def generate_demographics(demo_df, demo_fname) :

    br_concern = WorldBankBirthRateConcern(country="Burkina_Faso", birthrate_year=2016)

    chain = [
        DefaultIndividualAttributesConcern(),
        br_concern,
        EquilibriumAgeDistributionConcern(default_birth_rate=br_concern.default_birth_rate),
    ]

    current = DemographicsGenerator.from_dataframe(demo_df,
                                                   population_column_name='population',
                                                   nodeid_column_name='nodeid',
                                                   node_id_from_lat_long=False,
                                                   concerns=chain,
                                                   load_other_columns_as_attributes=True,
                                                   include_columns=['Village']
                                                   )

    with open(demo_fname, 'w') as fout :
        json.dump(current, fout, sort_keys=True,indent=4, separators=(',', ': '))


def generate_climate(demo_fname, input_file_name) :

    if not SetupParser.initialized:
        SetupParser.init('HPC')

    cg = ClimateGenerator(demographics_file_path=demo_fname, work_order_path='./wo.json',
                          climate_files_output_path=os.path.join(inputs_path, input_file_name),
                          climate_project='IDM-Burkina_Faso',
                          start_year='2016', num_years='1')
    cg.generate_climate_files()


if __name__ == '__main__' :

    inputs_path = os.path.join(projectpath, 'simulation_inputs')
    master_csv = os.path.join(inputs_path, 'demographics', 'nodes.csv')
    df = pd.read_csv(master_csv, encoding='latin')

    input_file_name = 'bf_indie_grid'

    demo_fname = os.path.join(inputs_path, 'demographics', '%s_demographics.json' % input_file_name)

    generate_demographics(df, demo_fname)

    generate_climate(demo_fname, input_file_name)
    # for tag in ['air_temperature', 'rainfall', 'relative_humidity'] :
    #     os.replace(os.path.join(inputs_path, 'Burkina Faso_30arcsec_%s_daily.bin' % tag),
    #                os.path.join(inputs_path, 'climate', '%s_%s_daily.bin' % (input_file_name, tag)))
    #     os.replace(os.path.join(inputs_path, 'climate', 'Burkina Faso_30arcsec_%s_daily.bin.json' % tag),
    #                os.path.join(inputs_path, 'climate', '%s_%s_daily.bin.json' % (input_file_name, tag)))
    # os.remove(os.path.join(inputs_path, 'climate', 'Burkina Faso_2.5arcmin_demographics.json'))
