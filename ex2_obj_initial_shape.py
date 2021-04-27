# Copyright (c) 2012-2021 Esri R&D Center Zurich

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#   https://www.apache.org/licenses/LICENSE-2.0

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
attrs = {}

# STEP 1: Initial Shape (vertices coordinates)
initial_shape1 = pyprt.InitialShape(
    [0, 0, 0,  0, 0, 100,  100, 0, 100,  100, 0, 0])

# PRT Generation
print('\nFirst Generation:\n')
m1 = pyprt.ModelGenerator([initial_shape1])
model1 = m1.generate_model([attrs], rpk, 'com.esri.pyprt.PyEncoder', {})
visualize_prt_results(model1)

# STEP 2: Initial Shape (OBJ file)
initial_shape2 = pyprt.InitialShape(asset_file('building_parcel.obj'))

# PRT Generation
print('\nSecond Generation:\n')
m2 = pyprt.ModelGenerator([initial_shape2])
model2 = m2.generate_model([attrs], rpk, 'com.esri.pyprt.PyEncoder', {})
visualize_prt_results(model2)

# PRT End
print('\nShutdown PRT.')
pyprt.shutdown_prt()
