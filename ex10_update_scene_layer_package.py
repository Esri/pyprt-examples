# Copyright (c) 2012-2024 Esri R&D Center Zurich

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

# This example demonstrates how an existing Scene Layer can be updated without having to touch any related Web Scenes.
# We use PyPRT to create a Scene Layer with a 3d visualization of the Swiss population density. We then
# recreate the Scene Layer with different visualization properties and show how the Web Scene updates automatically.

# You might want to use the keyring package to store your credentials for arcgis.com.
# The example script will automatically pick them up.
# To store the credentials execute the following once in a terminal:
# $ python
# >>> import keyring
# >>> keyring.set_password("arcgis.com", "your_user", "your_password")

# Example Steps:
# 1. At first run, the script will create a new Scene Layer called 'PyPRT_Ex10_Scene_Layer_<random suffix>'
# 2. On ArcGIS Online, create a Web Scene with this new Scene Layer
# 3. Retrieve the item ID of the new Scene Layer (see console output) and set it for 'TARGET_SCENE_LAYER_ID' below
# 4. Now change the POPULATION_DENSITY_MODE to 'logarithmic' and re-run the script
# 5. After a while, the Web Scene will update automatically.

import getpass
import os.path
import string
import random
import keyring
import tempfile
from pathlib import Path
import numpy as np

from arcgis.gis import GIS, ItemProperties, ItemTypeEnum
from arcgis.geometry import Geometry

import pyprt
from pyprt.pyprt_arcgis import arcgis_to_pyprt

SCRIPT_DIR = Path(__file__).resolve().parent

SOURCE_FEATURE_LAYER_ID = 'dfae9883bc3548dcbd29758ff8ea9234'  # Switzerland Kantone Boundaries 2021
SOURCE_FEATURE_LAYER_WKID = '3857'
TARGET_SCENE_LAYER_ID = '0'
TARGET_SCENE_LAYER_DEFAULT_NAME = 'PyPRT_Ex10_Scene_Layer'
RULE_PACKAGE_ITEM_ID = '4ab3503cd32c46e3ab129aa976b4f373'
PORTAL_DATA_DIR = 'PyPRT Example 10'

POPULATION_DENSITY_MODE = 'linear'  # or 'logarithmic'


def main():
    gis = get_gis()

    print(f"Fetching input features from item {SOURCE_FEATURE_LAYER_ID}... ")
    source_features = fetch_source_features(gis, SOURCE_FEATURE_LAYER_ID)
    print(f"   ... done. Got {len(source_features)} features.")

    print('Fetching target scene layer item...')
    target_scene_layer_item = gis.content.get(TARGET_SCENE_LAYER_ID)
    target_scene_layer_name = target_scene_layer_item.title if target_scene_layer_item else make_name_unique(
        TARGET_SCENE_LAYER_DEFAULT_NAME)
    print(f'   ... done: {target_scene_layer_name}')

    item_folder = gis.content.folders.get(folder=PORTAL_DATA_DIR)
    if item_folder is None:
        print(f"Creating portal folder '{PORTAL_DATA_DIR}' for scene layer item...")
        item_folder = gis.content.folders.create(PORTAL_DATA_DIR)

    with tempfile.TemporaryDirectory() as temp_dir:
        slpk_name = make_name_unique(target_scene_layer_name)

        print(f"Generating new SLPK in {temp_dir}...")
        scene_layer_package = generate_scene_layer_package(gis, slpk_name, source_features, temp_dir)
        print(f"   ... done: {scene_layer_package}")

        print(f"Uploading new SLPK ...")
        item_properties = ItemProperties(title=slpk_name, item_type=ItemTypeEnum.SCENE_PACKAGE.value)
        new_slpk_item = item_folder.add(file=scene_layer_package, item_properties=item_properties).result()
        print(f"   ... done. Uploaded new SLPK item '{new_slpk_item.title}' with id '{new_slpk_item.id}'")

    print("Publish new scene layer from new SLPK...")
    new_scene_layer_item = new_slpk_item.publish()
    print(f"   ... done, scene layer item id = {new_scene_layer_item.id}")

    print("Removing new SLPK again...")
    new_slpk_item.delete()
    print("   ... done.")

    if not target_scene_layer_item:
        new_scene_layer_item.update(item_properties={'title': target_scene_layer_name})
    else:
        print(f"Replacing service for item '{target_scene_layer_name}' ...")
        replacement_successful = gis.content.replace_service(target_scene_layer_item, new_scene_layer_item,
                                                             replace_metadata=True)
        print(f"   Replacement status: {replacement_successful}")
        new_scene_layer_item.delete()
        print(f"   ... done.")

    print("Please allow a few minutes for web scenes using the updated scene layer to update.")


def fetch_source_features(gis, source_item_id):
    source_feature_layer_collection = gis.content.get(source_item_id)
    assert len(source_feature_layer_collection.layers) == 9
    source_feature_layer = source_feature_layer_collection.layers[2]
    assert source_feature_layer.properties.name == 'CHE_Kantone'
    source_features = source_feature_layer.query(return_z=True)
    return source_features


def generate_scene_layer_package(gis, name, source_features, output_dir):
    pyprt_slpk_encoder = 'com.esri.prt.codecs.I3SEncoder'

    rule_package_item = gis.content.get(RULE_PACKAGE_ITEM_ID)
    rpk = rule_package_item.download()

    attrs = []
    for source_feature in source_features:
        attrs.append({
            'populationDensityMode': POPULATION_DENSITY_MODE,
            'population': float(source_feature.get_value('TOTPOP_CY')),
            'area': float(source_feature.get_value('AREA'))
        })

    pyprt_slpk_options = {
        'sceneType': 'Local',  # cannot use Global as PyPRT does not have reprojection capabilities
        'baseName': name,
        'sceneWkid': SOURCE_FEATURE_LAYER_WKID,
        'layerTextureEncoding': ['2'],
        'layerEnabled': [True],
        'layerUID': ['1'],
        'layerName': ['1'],
        'layerTextureQuality': [1.0],
        'layerTextureCompression': [9],
        'layerTextureScaling': [1.0],
        'layerTextureMaxDimension': [2048],
        'layerFeatureGranularity': ['0'],
        'layerBackfaceCulling': [False],
        'outputPath': output_dir
    }

    pyprt_initial_shapes = arcgis_to_pyprt(source_features)
    pyprt_model_generator = pyprt.ModelGenerator(pyprt_initial_shapes)
    pyprt_model_generator.generate_model(attrs, rpk, pyprt_slpk_encoder, pyprt_slpk_options)
    pyprt_generated_slpk = os.path.join(output_dir, f'{name}.slpk')
    assert os.path.exists(pyprt_generated_slpk)

    return pyprt_generated_slpk


def get_gis():
    arcgis_credential = keyring.get_credential(service_name="arcgis.com", username=None)
    if arcgis_credential:
        user_name = arcgis_credential.username
        password = arcgis_credential.password
    else:
        user_name = input('arcgis username:')
        password = getpass.getpass(prompt='arcgis password:')
    gis = GIS(username=user_name, password=password, verify_cert=False)
    return gis


def make_name_unique(name):
    random_suffix = ''.join(random.choice(string.ascii_lowercase + string.digits) for x in range(5))
    return f'{name}_{random_suffix}'
    

if __name__ == '__main__':
    main()
