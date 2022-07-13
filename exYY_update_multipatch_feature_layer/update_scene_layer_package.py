import os.path
import string
import random
import time
import keyring
import tempfile
from pathlib import Path

from arcgis.gis import GIS

import pyprt
from pyprt.pyprt_arcgis import arcgis_to_pyprt

SCRIPT_DIR = Path(__file__).resolve().parent

USER_NAME = 'simon_zurich'
SOURCE_FEATURE_LAYER_ID = 'b5677b032c224d0a87b7034db72b4b74'
TARGET_SCENE_LAYER_ID = 'bbc15eda30b84754a22a043bb5ae541a'
TARGET_SCENE_LAYER_DEFAULT_NAME = 'PyPRT_Scene_Layer'
RULE_PACKAGE_ITEM_ID = '9b5828f52203403a85556ebd14a617f7'


def main():
    # use keyring.set_password(...) in a local python session to supply your password
    password = keyring.get_password("zurich.maps.arcgis.com", USER_NAME)
    gis = GIS(username=USER_NAME, password=password, verify_cert=False)

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
    source_feature_layer = source_feature_layer_collection.layers[0]
    source_features = source_feature_layer.query(return_z=True)
    return source_features


def generate_scene_layer_package(gis, name, source_features, output_dir):
    pyprt_slpk_encoder = 'com.esri.prt.codecs.I3SEncoder'

    rule_package_item = gis.content.get(RULE_PACKAGE_ITEM_ID)
    rpk = rule_package_item.download()
    attrs = [{'h': 20.0}]  # EPSG:2272 is in feet!

    pyprt_slpk_options = {
        'sceneType': 'Local',  # cannot use Global as PyPRT does not have reprojection capabilities
        'baseName': name,
        'sceneWkid': '2272',  # must match the input feature layer and the target scene layer
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


def delete_items_by_name(gis, name):
    search_results = gis.content.search(query=f"title:{name}")
    exact_results = list(filter(lambda item: item.title == name, search_results))
    if len(exact_results) > 0:
        for i in exact_results:
            i.delete()
    return len(exact_results)


def find_exactly(gis, item_title, item_type):
    results = gis.content.search(query=f'title:"{item_title}" AND type:"{item_type}"')
    results = list(filter(lambda item: item.title == item_title, results))
    return results


if __name__ == '__main__':
    main()
