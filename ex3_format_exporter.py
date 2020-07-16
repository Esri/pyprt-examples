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
rpk = asset_file('candler.rpk')
attrs = {}


# Initial Shapes
shape_geometry_1 = pyprt.InitialShape(
    [0, 0, 0,  0, 0, 100,  100, 0, 100,  100, 0, 0])
shape_geometry_2 = pyprt.InitialShape(
    [0, 0, 0,  0, 0, -10,  -10, 0, -10,  -10, 0, 0, -5, 0, -5])


# PRT Generation
m = pyprt.ModelGenerator([shape_geometry_2, shape_geometry_1])

encoder_options = {'outputPath': '/tmp/pyprt_output'}
os.makedirs(encoder_options['outputPath'], exist_ok=True)

models = m.generate_model(
    [attrs], rpk, 'com.esri.prt.codecs.OBJEncoder', encoder_options)
print('\nGenerated models located in '+encoder_options['outputPath'])


# PRT End
pyprt.shutdown_prt()
print('\nShutdown PRT.')
