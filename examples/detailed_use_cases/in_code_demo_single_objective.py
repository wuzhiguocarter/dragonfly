"""
  A demo on an electrolyte optimisation task using various features of Dragonfly.
  -- kirthevasank
"""

from __future__ import print_function
from argparse import Namespace
from dragonfly import load_config_file, maximise_function, maximise_multifidelity_function
# Local imports
import obj_3d
import obj_3d_mf
import obj_5d
from prior_means import conductivity_prior_mean_3d, conductivity_prior_mean_5d, \
                        conductivity_prior_mean_3d_mf


# choose problem
# PROBLEM = '3d'      # Optimisation problem with 3 variables
# PROBLEM = '3d_mf'   # Optimisation problem with 3 variables and 1 fidelity variable
# PROBLEM = '3d_euc'  # Optimisation problem with 3 variables all of which are continuous
PROBLEM = '5d'      # Optimisation problem with 5 variables

USE_CONDUCTIVITY_PRIOR_MEAN = True
# USE_CONDUCTIVITY_PRIOR_MEAN = False

# chooser dict
_CHOOSER_DICT = {
  '3d': (obj_3d.objective, 'config_3d.json', None),
  '3d_euc': (obj_3d.objective, 'config_3d_cts.json', None),
  '3d_mf': (obj_3d_mf.objective, 'config_3d_mf.json', obj_3d_mf.cost),
  '5d': (obj_5d.objective, 'config_5d.json', None),
  }


def main():
  """ Main function. """
  # Load configuration file
  objective, config_file, mf_cost = _CHOOSER_DICT[PROBLEM]
  config = load_config_file(config_file)

  # Specify options
  options = Namespace(
    build_new_model_every=5, # update the model every 5 iterations
    report_results_every=4, # report progress every 4 iterations
    report_model_on_each_build=True, # report model when you build it.
    )

  # Dragonfly allows specifying a mean for the GP prior - if there is prior knowledge
  # on the rough behaviour of the function to be optimised, this is one way that
  # information can be incorporated into the model.
  if USE_CONDUCTIVITY_PRIOR_MEAN:
    if PROBLEM in ['3d', '3d_euc']:
      options.gp_prior_mean = conductivity_prior_mean_3d
    elif PROBLEM == '3d_mf':
      options.gp_prior_mean = conductivity_prior_mean_3d_mf
    elif PROBLEM == '5d':
      options.gp_prior_mean = conductivity_prior_mean_5d
    # The _unproc indicates that the mean function is "unprocessed". Dragonfly converts
    # the domain specified given in the configuration to an internal order which may
    # have reordered the variables. The _unproc tells that the function
    # should be called in the original format.

  # Optimise
  max_capital = 60
  if PROBLEM in ['3d', '3d_euc', '5d']:
    opt_val, opt_pt, history = maximise_function(objective, config.domain, max_capital,
                                                 config=config, options=options)
  else:
    opt_val, opt_pt, history = maximise_multifidelity_function(objective,
                                 config.fidel_space, config.domain, config.fidel_to_opt,
                                 mf_cost, max_capital, config=config, options=options)

  print('opt_pt: %s'%(str(opt_pt)))
  print('opt_val: %s'%(str(opt_val)))


if __name__ == '__main__':
  main()

