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
TARGET_SCENE_LAYER_NAME = 'PyPRT_Scene_Layer_Update_Test'
RPK_NAME = 'extrude.rpk'


def main():
    # use keyring.set_password(...) in a local python session to supply your password
    password = keyring.get_password("zurich.maps.arcgis.com", USER_NAME)
    gis = GIS(username=USER_NAME, password=password, verify_cert=False)

    print(f"Fetching input features from item {SOURCE_FEATURE_LAYER_ID}... ")
    source_features = fetch_source_features(gis, SOURCE_FEATURE_LAYER_ID)
    print(f"   ... done. Got {len(source_features)} features.")

    with tempfile.TemporaryDirectory() as temp_dir:
        random_suffix = ''.join(random.choice(string.ascii_lowercase + string.digits) for x in range(5))
        new_slpk_name = TARGET_SCENE_LAYER_NAME + '_' + random_suffix

        print(f"Generating new SLPK in {temp_dir}...")
        scene_layer_package = generate_scene_layer_package(new_slpk_name, source_features, temp_dir)
        print(f"   ... done: {scene_layer_package}")

        print(f"Uploading new SLPK ...")
        new_slpk_item = gis.content.add(data=scene_layer_package, item_properties={'title': new_slpk_name})
        print(f"   ... done. Uploaded new SLPK item '{new_slpk_item.title}' with id '{new_slpk_item.id}'")

    print("Publish new scene layer from new SLPK...")
    new_scene_layer_item = new_slpk_item.publish()
    print("   ... done.")

    print("Removing new SLPK again...")
    new_slpk_item.delete()
    print("   ... done.")

    print(f"Replacing service for item '{TARGET_SCENE_LAYER_NAME}' ...")
    existing_scene_layers = find_exactly(gis, TARGET_SCENE_LAYER_NAME, "Scene Service")
    assert 0 <= len(existing_scene_layers) <= 1
    if len(existing_scene_layers) == 0:
        new_scene_layer_item.update(item_properties={'title': TARGET_SCENE_LAYER_NAME})
    else:
        delete_suffix = ''.join(random.choice(string.ascii_lowercase + string.digits) for x in range(5))
        replaced_scene_layer_name = TARGET_SCENE_LAYER_NAME + '_delete_' + delete_suffix

        scene_layer_item = existing_scene_layers[0]
        replacement_successful = gis.content.replace_service(scene_layer_item, new_scene_layer_item,
                                                             replaced_service_name=replaced_scene_layer_name,
                                                             replace_metadata=True)
        print(f"   Replacement status: {replacement_successful}")
    print(f"   ... done.")

    print("Cleaning up replaced scene layer/service ...")
    max_tries = 5
    if not delete_item_with_retrying(gis, replaced_scene_layer_name, "Scene Service", max_tries):
        print(f"Failed to cleanup replaced service {replaced_scene_layer_name} after {max_tries} attempts.")
    print(f"   ... done.")

    print("Please allow a few minutes for web scenes using the updated scene layer to update.")


def fetch_source_features(gis, source_item_id):
    source_feature_layer_collection = gis.content.get(source_item_id)
    source_feature_layer = source_feature_layer_collection.layers[0]
    source_features = source_feature_layer.query(return_z=True)
    return source_features


def generate_scene_layer_package(name, source_features, output_dir):
    pyprt_slpk_encoder = 'com.esri.prt.codecs.I3SEncoder'

    attrs = [{'h': 20.0}]  # EPSG:2272 is in feet!
    rpk = SCRIPT_DIR.joinpath(RPK_NAME)

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
    pyprt_model_generator.generate_model(attrs, str(rpk), pyprt_slpk_encoder, pyprt_slpk_options)
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


def delete_item_with_retrying(gis, item_name, item_type, max_tries):
    # the replaced item is not immediately findable... let's wait for it
    tries = 0
    while tries < max_tries:
        replaced_scene_layer_item = find_exactly(gis, item_name, item_type)
        if len(replaced_scene_layer_item) == 1:
            replaced_scene_layer_item[0].delete()
            break
        time.sleep(1)
        tries += 1
    return tries < 5


if __name__ == '__main__':
    main()
