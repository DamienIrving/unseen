"""Plot hottest SeaTac day in observations"""

import pdb
import sys
script_dir = sys.path[0]
repo_dir = '/'.join(script_dir.split('/')[:-2])
module_dir = repo_dir + '/unseen'
sys.path.insert(1, module_dir)

import argparse
import warnings
warnings.filterwarnings('ignore')
import logging

import numpy as np
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import xarray as xr

import fileio
import general_utils
import plot_reanalysis_hottest_day as prhd


def get_max_indices(infiles, config_file):
    """Get the time and ensemble index for hottest day at SeaTac"""

    ds = fileio.open_mfzarr(infiles,
                            variables=['tasmax'],
                            metadata_file=config_file,
                            spatial_coords=[47.45, -122.31 + 360])

    argmax = ds['tasmax'].argmax(dim=['ensemble', 'time'])

    time_idx = int(argmax['time'].values)
    logging.info(f'Max temperature at SeaTac, time index: {time_idx}')

    ens_idx = int(argmax['ensemble'].values)
    logging.info(f'Max temperature at SeaTac, ensemble index: {ens_idx}')

    max_temp = float(ds['tasmax'].isel({'ensemble': ens_idx , 'time': time_idx}).values)
    max_temp = max_temp - 273.15
    logging.info(f'Maximum temperature at SeaTac: {max_temp}C')

    return time_idx, ens_idx


def _main(args):
    """Run the command line program."""

    logfile = args.logfile if args.logfile else args.outfile.split('.')[0] + '.log'
    logging.basicConfig(level=logging.INFO, filename=logfile, filemode='w')
    general_utils.set_plot_params(args.plotparams)

    if args.max_index:
        time_idx, ens_idx = args.max_index
    else:
        time_idx, ens_idx = get_max_indices(args.infiles, args.config) 

    ds = fileio.open_mfzarr(args.infiles,
                            variables=['h500', 'tasmax'],
                            metadata_file=args.config)
    ds_max = ds.isel({'ensemble': ens_idx, 'time': time_idx})
    ds_max['tasmax'] = general_utils.convert_units(ds_max['tasmax'], 'C')
    ds_max = ds_max.compute()

    new_log = fileio.get_new_log(repo_dir=repo_dir)
    metadata_key = fileio.image_metadata_keys[args.outfile.split('.')[-1]]
    prhd.plot_usa(ds_max['tasmax'], ds_max['h500'], args.outfile, metadata_key, new_log, 'Model')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument("infiles", nargs='*', type=str, help="model data files")
    parser.add_argument("config", type=str, help="configuration file")
    parser.add_argument("outfile", type=str, help="output file")
    
    parser.add_argument('--max_index', type=int, nargs=2, default=None,
                        help='time and ensemble index of hottest day')
    parser.add_argument('--plotparams', type=str, default=None,
                        help='matplotlib parameters (YAML file)')
    parser.add_argument('--logfile', type=str, default=None,
                        help='name of logfile (default = same as outfile but with .log extension')
    
    args = parser.parse_args()
    _main(args)