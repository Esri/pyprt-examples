# Copyright (c) 2012-2020 Esri R&D Center Zurich

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#   http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# A copy of the license is available in the repository's LICENSE file.

import sys
import os

import pyprt
from pyprt.pyprt_utils import visualize_prt_results

CS_FOLDER = os.path.dirname(os.path.realpath(__file__))


def asset_file(filename):
    return os.path.join(CS_FOLDER, 'data', filename)


# PRT Initialization
print('\nInitializing PRT.')
pyprt.initialize_prt()

if not pyprt.is_prt_initialized():
    raise Exception('PRT is not initialized')

# Data
rpk = asset_file('extrusion_rule.rpk')
attrs = {'ruleFile': 'bin/extrusion_rule.cgb',
         'startRule': 'Default$Footprint'}

# Initial Shape
initial_shape1 = pyprt.InitialShape(
    [0, 0, 0,  0, 0, 100,  100, 0, 100,  100, 0, 0])

# STEP 1: PRT Generation
print('\nFirst Generation: generated geometry + report\n')
m1 = pyprt.ModelGenerator([initial_shape1])
model1 = m1.generate_model([attrs], rpk, 'com.esri.pyprt.PyEncoder', {
                           'emitGeometry': True, 'emitReport': True})
visualize_prt_results(model1)

# STEP 2: PRT Generation
print('\nSecond Generation: generated geometry\n')
m1 = pyprt.ModelGenerator([initial_shape1])
model1 = m1.generate_model([attrs], rpk, 'com.esri.pyprt.PyEncoder', {
                           'emitGeometry': True, 'emitReport': False})
visualize_prt_results(model1)

# PRT End
print('\nShutdown PRT.')
pyprt.shutdown_prt()
