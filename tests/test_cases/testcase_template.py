# -*- coding: utf-8 -*-
"""
Created on Sat Apr  9 15:36:59 2016

@author: derrick
Module for running test casses
"""

###### imports and such
from __future__ import print_function, unicode_literals, division, absolute_import
from six import string_types
import pytest
import os
import detex
import obspy
from collections import namedtuple
# define named tuples used by fixtures
CasePaths = namedtuple('CasePaths', ['temkey', 'stakey', 'phases', 'condir',
                                     'evedir', 'casedir'])
DetexKeys = namedtuple('DetexKeys', ['temkey', 'stakey', 'phases'])

########## globals, functions and determine if this module should be skipped

# define path to directory that contains keys and phases
test_case = 'TestX'
directory_path = os.path.join('Test_Cases', test_case)
log_path = '.detex.log'
subspace_database = 'SubSpace.db'
# dict of parameters for continuous data fetcher used for get data call
get_data_fet_args = {'method':'iris', 'client':obspy.clients.fdsn}
# dict of parameters for the make data directories call
make_data_args = {'timeBeforeOrigin':60, 'timeAfterOrigin':240, 'secBuf':120,
                  'conDatDuration':3600, 'getContinuous':True, 
                  'getTemplates':True, 'removeResponse':True, 'opType':'VEL',
                  'prefilt':[0.05, 0.1, 15, 20]}
# dict of params for data fetcher for continuous data
con_data_args = {}
# dict of params for event data fetcher
eve_data_args = {} 
# dict for create cluster args
create_cluster_args = {}
# dict for create subspace args
create_subspace_args = {}
# attach phases params
attach_pick_time_args = {'defaultDuration':30}
# params for SVD 
svd_params = {'conDatNum':100, 'threshold':None, 'normalize':False, 
              'useSingles':False, 'validateWaveforms':True}
# params for running detections
detection_params = {'utcStart':None, 'utcEnd':None, 'subspaceDB':subspace_database,
                    'delOldCorrs':True, 'calcHist':True, 'useSubSpaces':True,
                    'useSingles':False, 'estimateMags':True, 'fillZeros':False}
# params for running detResults
results_params = {'ss_associateBuffer':1, 'sg_associateBuffer':2.5, 
                  'requiredNumStations':4, 'veriBuffer':1, 'ssDB':subspace_database,
                  'rediceDets':True, 'Pf':False, 'stations':None, 'starttime':None,
                  'endtime':None, 'fetch':'ContinuousWaveForms'}



# mark skip on module if required command line not passed or other case run
opt = pytest.config.getoption('--test_case')
if bool(opt):
    if isinstance(opt, string_types):
        if opt in os.path.basename(__file__):
            run_module = True
    else:
        run_module = True
else:
     run_module = False
# skip if required
reason = "test cases not used or this one not selected"
pytestmark = pytest.mark.skipif(not run_module, reason=reason)
#pytestmark = pytest.mark(test_case)
########### detex workflow setup fixtures
# These fixtures run the basic tutorial workflow

# get paths to keys and directory, return namedtuple else fail downstream tests
@pytest.fixture(scope='module')
def case_paths():
    """
    return the paths to the key files for detex and current test directory in 
    """
#    test_dirs = request.config.getoption("--test_direcotory")
    temkey_path = os.path.join(directory_path, 'TemplateKey.csv')
    stakey_path = os.path.join(directory_path, 'StationKey.csv')
    phase_path = os.path.join(directory_path, 'PhasePicks.csv')
    condir_path = os.path.join(directory_path, 'ContinuousWaveForms')
    evedir_path = os.path.join(directory_path, 'EventWaveForms')
    case_paths = CasePaths(temkey_path, stakey_path, phase_path, condir_path,
                           evedir_path, directory_path)
    if all([os.path.exists(x) for x in [temkey_path, stakey_path, phase_path]]):
        return case_paths
    else: # if not all keys are found fail the rest of the tests
        msg = ("StationKey.csv, TemplateKey.csv, and PhasePicks.csv not all" 
                " found in %s, failing dependant tests" % directory_path)
        pytest.fail(msg)

# Set the logger and delete it when finished
@pytest.yield_fixture(case_paths, scope="module")
def set_logger():
    detex.setLogger(fileName=log_path)
    yield log_path
    os.remove(log_path)

# Load keys into memory
@pytest.fixture(scope="module")
def load_keys(case_paths):
    temkey_path, stakey_path, phase_path, case_path = case_paths
    temkey = detex.util.readKey(temkey_path, 'template')
    stakey = detex.util.readKey(stakey_path, 'station')
    phases = detex.util.readKey(phase_path, 'phase')
    detex_keys = DetexKeys(temkey, stakey, phases)
    return detex_keys

# init data fetcher of choice for downloading continuous data
@pytest.fixture(scope="module")
def get_data_fetcher(load_keys):
    fet = detex.getdata.DataFetcher(**get_data_fet_args)
    return fet

# Make data dirs, (eg download data from IRIS)
@pytest.fixture(scope="module")
def make_data_dirs(load_keys, get_data_fetcher):
    fet = get_data_fetcher
    temkey, stakey, phases = load_keys
    detex.getdata.makeDataDirectories(templateKey=temkey, stationKey=stakey,
                                      fetch=fet, **make_data_args)
    # dont delete when finished gitignore will keep it from being pushed  
                                      
# return continuous data fetcher from continuous data file
@pytest.fixture(scope="module")
def continuous_data_fetcher_condir(case_paths):
    path = case_paths.condir
    fet = detex.getdata.DataFetcher(method='dir', directoryName=path, 
                                    **con_data_args)
    return fet

# return event data fetcher from event waveforms file
@pytest.fixture(scope="module")
def event_data_fetcher_evedir(case_paths):
    path = case_paths.evedir
    fet = detex.getdata.DataFetcher(method='dir', directoryName=path, 
                                    **eve_data_args)
    return fet

## Create Cluster
@pytest.fixture(scope="module")
def create_cluster(make_data_dirs, event_data_fetcher_evedir):
    cl = detex.createCluster(fetch_arg=event_data_fetcher_evedir,
                             **create_cluster_args)
    return cl

# any actions to perform on cluster go here
@pytest.fixture(scope="module")
def modify_cluster(create_cluster):
    cl = create_cluster
    return cl

# create the subspace object
@pytest.fixture(scope='module')
def create_subspace(modify_cluster, continuous_data_fetcher):
    cl = modify_cluster
    ss = detex.createSubSpace(clust=cl, conDatFetcher=continuous_data_fetcher,
                              **create_subspace_args)
    return ss

# attach picktimes found in the phase file
@pytest.fixture(scope='module')
def attach_pick_times(create_subspace, case_paths):
    ss = create_subspace
    ss.attachPickTimes(pksFile=case_paths.phases, **attach_pick_time_args)
    return ss

# perform the svd 
@pytest.fixture(scope='module')
def perform_svd(attach_pick_times):
    ss = attach_pick_times
    ss.SVD(**svd_params)
    return ss

# perform any additional modifications
@pytest.fixture(scope='module')
def modify_subspace(perform_svd):
    ss = perform_svd
    return ss

# run detections
@pytest.fixture(scope='module')
def run_detections(modify_subspace):
    ss = modify_subspace
    ss.detex(**detection_params)
    return ss

# load results
@pytest.fixture(scope='module')
def get_results(run_detections):
    res = detex.results.detResults(**results_params)
    return res
    





























