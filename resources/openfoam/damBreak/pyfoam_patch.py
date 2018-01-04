#!/usr/bin/env python

from PyFoam.RunDictionary.ParsedParameterFile import ParsedParameterFile

# read existing parameter file
parameter_set = ParsedParameterFile('constant/transportProperties')

parameter_set['water']['nu'] = ${parameters['disperse_nu']}
parameter_set['water']['rho'] = ${parameters['disperse_rho']}

parameter_set['air']['nu'] = ${parameters['continuous_nu']}
parameter_set['air']['rho'] = ${parameters['continuous_rho']}

parameter_set['sigma'] = ${parameters['surface_tension']}

# overwrite existing parameter file
parameter_set.writeFile()
