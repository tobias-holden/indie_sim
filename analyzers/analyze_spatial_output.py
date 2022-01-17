import pandas as pd
import os
from simtools.Analysis.BaseAnalyzers import BaseAnalyzer
import sys
sys.path.append('../helpers/')
from load_paths import load_box_paths
from construct_spatial_output_dataframe import construct_spatial_output_df

datapath, projectpath = load_box_paths()
output_path = os.path.join(projectpath, 'simulation_output')


class SpatialAnalyzer(BaseAnalyzer):

    def __init__(self, expt_name, spatial_channels, sweep_variables=None, working_dir='.'):
        super(SpatialAnalyzer, self).__init__(working_dir=working_dir,
                                              filenames=['output/SpatialReportMalariaFiltered_%s.bin' % x for x in spatial_channels]
                                           )
        self.expt_name = expt_name
        self.sweep_variables = sweep_variables or ['Run_Number']
        self.spatial_channels = spatial_channels
        self.wdir = working_dir

    def select_simulation_data(self, data, simulation):

        simdata = construct_spatial_output_df(data['output/SpatialReportMalariaFiltered_%s.bin' % self.spatial_channels[0]],
                                              self.spatial_channels[0])
        if len(self.spatial_channels) > 1:
            for ch in self.spatial_channels[1:]:
                simdata = pd.merge(left=simdata,
                                   right=construct_spatial_output_df(data['output/SpatialReportMalariaFiltered_%s.bin' % ch], ch),
                                   on=['time', 'node'])

        for sweep_var in self.sweep_variables:
            if sweep_var in simulation.tags.keys():
                simdata[sweep_var] = simulation.tags[sweep_var]
            else:
                simdata[sweep_var] = 0
        return simdata

    def finalize(self, all_data):

        selected = [data for sim, data in all_data.items()]
        if len(selected) == 0:
            print("No data have been returned... Exiting...")
            return

        df = pd.concat(selected).reset_index(drop=True)
        df.to_csv(os.path.join(self.wdir, '%s.csv' % self.expt_name), index=False)


def analyze_by_expt_id(expt_name, expt_id, channels=None,
                       sweep_variables=None) :

    if channels is None:
        channels = ['Population', 'PCR_Parasite_Prevalence', 'New_Infections', "New_Clinical_Cases"]
    from simtools.Analysis.AnalyzeManager import AnalyzeManager
    from simtools.SetupParser import SetupParser

    SetupParser.default_block = 'HPC'
    if not SetupParser.initialized :
        SetupParser.init()

    analyzer = SpatialAnalyzer(expt_name=expt_name,
                               spatial_channels=channels,
                               sweep_variables=sweep_variables,
                               working_dir=output_path)

    am = AnalyzeManager(expt_id, analyzers=analyzer)
    am.analyze()


if __name__ == "__main__":

    expt_name = 'bf_indie_test'
    expt_id = 'b22a3ebc-3677-ec11-a9f2-9440c9be2c51'

    channels = ['Population', 'PCR_Parasite_Prevalence', 'New_Infections', "New_Clinical_Cases"]
    analyze_by_expt_id(expt_name, expt_id, channels=channels)
