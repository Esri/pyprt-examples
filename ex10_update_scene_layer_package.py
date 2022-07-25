# Copyright (c) 2012-2022 Esri R&D Center Zurich

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

# Example Steps:
# 1. At first run, the script will create a new Scene Layer called 'PyPRT_Ex10_Scene_Layer'
# 2. Create a Web Scene with this new layer
# 3. Retrieve the item ID of the above layer and set it for 'TARGET_SCENE_LAYER_ID' below
# 4. Now change the POPULATION_DENSITY_MODE to 'logarithmic' and re-run the script
# 5. After a while, the Web Scene will update automatically.

import sys
import getpass
import os.path
import string
import random
import keyring
import tempfile
import shapely
from pathlib import Path
import numpy as np

from arcgis.gis import GIS
from arcgis.geometry import Geometry

import pyprt

SCRIPT_DIR = Path(__file__).resolve().parent

SOURCE_FEATURE_LAYER_ID = 'dfae9883bc3548dcbd29758ff8ea9234'  # Switzerland Kantone Boundaries 2021
SOURCE_FEATURE_LAYER_WKID = '3857'
TARGET_SCENE_LAYER_ID = '0'
TARGET_SCENE_LAYER_DEFAULT_NAME = 'PyPRT_Ex10_Scene_Layer'
RULE_PACKAGE_ITEM_ID = '5ea3e57d47224c21b2678069cd325f84'

POPULATION_DENSITY_MODE = 'linear'  # or 'logarithmic'


def main():
    gis = get_gis()

    print(f"Fetching input features from item {SOURCE_FEATURE_LAYER_ID}... ")
    source_features = fetch_source_features(gis, SOURCE_FEATURE_LAYER_ID)
    print(f"   ... done. Got {len(source_features)} features.")

    print('Fetching target scene layer item...')
    target_scene_layer_item = gis.content.get(TARGET_SCENE_LAYER_ID)
    target_scene_layer_name = target_scene_layer_item.title if target_scene_layer_item else TARGET_SCENE_LAYER_DEFAULT_NAME
    print(f'   ... done: {target_scene_layer_name}')

    with tempfile.TemporaryDirectory() as temp_dir:
        random_suffix = ''.join(random.choice(string.ascii_lowercase + string.digits) for x in range(5))
        new_slpk_name = target_scene_layer_name + '_' + random_suffix

        print(f"Generating new SLPK in {temp_dir}...")
        scene_layer_package = generate_scene_layer_package(gis, new_slpk_name, source_features, temp_dir)
        print(f"   ... done: {scene_layer_package}")

        print(f"Uploading new SLPK ...")
        new_slpk_item = gis.content.add(data=scene_layer_package, item_properties={'title': new_slpk_name})
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

    pyprt.initialize_prt()

    pyprt_initial_shapes = arcgis_to_pyprt(source_features)
    pyprt_model_generator = pyprt.ModelGenerator(pyprt_initial_shapes)
    pyprt_model_generator.generate_model(attrs, rpk, pyprt_slpk_encoder, pyprt_slpk_options)
    pyprt_generated_slpk = os.path.join(output_dir, f'{name}.slpk')
    assert os.path.exists(pyprt_generated_slpk)

    pyprt.shutdown_prt()

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


# --- code copy from pyprt_arcgis start ---

def add_dimension(array_coord_2d):
    array_coord_3d = np.insert(array_coord_2d, 1, 0, axis=1)
    return np.reshape(array_coord_3d, (1, array_coord_3d.shape[0] * array_coord_3d.shape[1]))


def swap_yz_dimensions(array_coord):
    coord_swap_dim = array_coord.copy()
    temp = np.copy(array_coord[:, 1])
    coord_swap_dim[:, 1] = coord_swap_dim[:, 2]
    coord_swap_dim[:, 2] = temp
    return np.reshape(coord_swap_dim, (1, coord_swap_dim.shape[0] * coord_swap_dim.shape[1]))


def holes_conversion(holes_ind_list):
    holes_dict = {}
    holes_list = []
    if len(holes_ind_list) > 0:
        for h_idx in holes_ind_list:
            f_idx = h_idx
            while f_idx > 0:
                f_idx -= 1
                if not (f_idx in holes_ind_list):
                    if not (f_idx in holes_dict):
                        holes_dict[f_idx] = [h_idx]
                    else:
                        holes_dict[f_idx].append(h_idx)
                    break

        for key, value in holes_dict.items():
            face_holes = [key]
            face_holes.extend(value)
            holes_list.append(face_holes)
    return holes_list


def arcgis_to_pyprt(feature_set):
    """arcgis_to_pyprt(feature_set) -> List[InitialShape]
    This function allows converting an ArcGIS FeatureSet into a list of PyPRT InitialShape instances.
    You then typically call the ModelGenerator constructor with the return value if this function as parameter.

    Parameters:
        feature_set: FeatureSet

    Returns:
        List[InitialShape]

    """
    initial_geometries = []
    for feature in feature_set.features:
        try:
            geo = Geometry(feature.geometry)
            if geo.type == 'Polygon' and (not geo.is_empty):
                pts_cnt = 0
                vert_coord_list = []
                face_count_list = []
                holes_ind_list = []
                coord_list = geo.coordinates()

                for face_idx, coord_part in enumerate(coord_list):
                    coord_remove_last = coord_part[:-1]
                    coord_inverse = np.flip(coord_remove_last, axis=0)
                    coord_inverse[:, 1] *= -1

                    if len(coord_part[0]) == 2:
                        coord_fin = add_dimension(coord_inverse)
                    elif len(coord_part[0]) == 3:
                        coord_fin = swap_yz_dimensions(coord_inverse)
                    else:
                        print("Only 2D or 3D points are supported.")

                    vert_coord_list.extend(coord_fin[0])
                    nb_pts = len(coord_fin[0]) / 3
                    pts_cnt += nb_pts
                    face_count_list.append(int(nb_pts))

                # use Shapely to detect interior rings (holes)
                shapely_geo = geo.as_shapely
                shapely_face_index = 0
                for shapely_part in shapely_geo.geoms:
                    shapely_face_index += 1
                    for shapely_interior in shapely_part.interiors:
                        holes_ind_list.append(shapely_face_index)
                        shapely_face_index += 1

                face_indices_list = list(range(0, sum(face_count_list)))
                holes_list = holes_conversion(holes_ind_list)

                initial_geometry = pyprt.InitialShape(vert_coord_list, face_indices_list, face_count_list, holes_list)
                initial_geometries.append(initial_geometry)
        except:
            print("This feature is not valid: ")
            print(feature)
            print()
    return initial_geometries


# --- code copy from pyprt_arcgis end ---

if __name__ == '__main__':
    main()
