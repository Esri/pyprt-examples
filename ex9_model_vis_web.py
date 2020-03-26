import os
import random
import string
import json
import argparse
import math
from pathlib import Path
import tornado.ioloop
import tornado.web
import pyprt
from arcgis.gis import GIS

DBG = True
CS_FOLDER = Path().absolute()
ROOT = os.path.join(CS_FOLDER, 'ex9_html')
OUTPUT_PATH = os.path.join(CS_FOLDER, 'ex9_output')
RPK = os.path.join(CS_FOLDER, 'data', 'translateModel.rpk')
PORT = 9999
AGO_DATA_DIR = 'modelVisServerData'


class MainHandler(tornado.web.RequestHandler):
    def initialize(self, gis):
        self.filename = ''
        self.extension_filename = ''
        self.file_path = ''
        self.filename_slpk = ''
        self.gis = gis

    def save_file(self):
        uploaded_file = self.request.files['file'][0]
        original_filename = uploaded_file['filename']
        extension = os.path.splitext(original_filename)[1]
        self.filename = os.path.splitext(original_filename)[0] + '_' + ''.join(random.choice(string.ascii_lowercase +
                                                                                             string.digits) for x in range(5))
        self.extension_filename = self.filename + extension
        self.file_path = os.path.join(OUTPUT_PATH, self.extension_filename)
        output_file = open(self.file_path, 'wb')
        output_file.write(uploaded_file['body'])

    def convert_to_slpk(self):
        x_coord = self.get_argument("x_coordinate")
        y_coord = self.get_argument("y_coordinate")
        elev = self.get_argument("elevation")

        if DBG:
            print(
                f'Setting georef to ({round(float(x_coord),2)}, {round(float(y_coord),2)}) (Web Mercator) with elevation {int(float(elev))} meters')

        # Model Generator Instance
        mod_generator1 = pyprt.ModelGenerator(
            [pyprt.InitialShape(self.file_path)])

        shape_attributes = {'ruleFile': 'bin/translateModel.cgb',
                            'startRule': 'Default$Lot'}

        model = mod_generator1.generate_model([shape_attributes], RPK,
                                              'com.esri.pyprt.PyEncoder', {'emitReport': False})

        # Bounding box
        mod_vertices = model[0].get_vertices()

        min_y_value = min(mod_vertices[1::3])
        center_x_value = min(mod_vertices[0::3])+(
            max(mod_vertices[0::3])-min(mod_vertices[0::3]))/2.0
        center_z_value = min(mod_vertices[2::3])+(
            max(mod_vertices[2::3])-min(mod_vertices[2::3]))/2.0

        # Offset the initial shape at the right location
        mod_vertices_shift = mod_vertices.copy()
        mod_vertices_shift[0::3] = [a-center_x_value +
                                    float(x_coord) for a in mod_vertices_shift[0::3]]
        mod_vertices_shift[1::3] = [
            a-min_y_value+float(elev) for a in mod_vertices_shift[1::3]]
        mod_vertices_shift[2::3] = [a-center_z_value -
                                    float(y_coord) for a in mod_vertices_shift[2::3]]

        shifted_shape = pyprt.InitialShape(
            mod_vertices_shift, model[0].get_indices(), model[0].get_faces())

        mod_generator2 = pyprt.ModelGenerator([shifted_shape])

        slpk_encoder = 'com.esri.prt.codecs.I3SEncoder'

        slpk_encoder_options = {
            'sceneType': "Local",
            'baseName': self.filename,
            'sceneWkid': "3857",
            'layerTextureEncoding': ["2"],
            'layerEnabled': [True],
            'layerUID': ["1"],
            'layerName': ["1"],
            'layerTextureQuality': [1.0],
            'layerTextureCompression': [9],
            'layerTextureScaling': [1.0],
            'layerTextureMaxDimension': [2048],
            'layerFeatureGranularity': ["0"],
            'layerBackfaceCulling': [False],
            'outputPath': OUTPUT_PATH
        }

        mod_generator2.generate_model([shape_attributes], RPK,
                                      slpk_encoder, slpk_encoder_options)
        self.filename_slpk = os.path.join(
            OUTPUT_PATH, self.filename + '.slpk')

    def publish(self):
        slpk_item = self.gis.content.add(
            {
                "title": f"PyPRT_webApp_{self.filename}",
                "tags": "slpk",
            },
            data=self.filename_slpk,
            folder=AGO_DATA_DIR
        )

        slpk_item_published = slpk_item.publish()
        slpk_item_published.share(everyone=True)
        slpk_item.delete()

        return slpk_item_published.id

    def post(self):
        self.save_file()
        self.convert_to_slpk()

        if DBG:
            print('Publishing file on ArcGIS Online:')
            print(self.filename_slpk)

        id = self.publish()
        self.write(json.dumps({'portalId': id}))
        self.finish()

    def on_finish(self):
        if DBG:
            print('Cleaning up files:')
            print(self.file_path)
            print(self.filename_slpk)

        os.remove(self.file_path)
        os.remove(self.filename_slpk)


if not os.path.exists(OUTPUT_PATH):
    os.makedirs(OUTPUT_PATH)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='ArcGIS Online credentials')
    parser.add_argument(
        '--username', help='Your username for AGO', type=str, required=True)
    parser.add_argument(
        '--password', help='Your password for AGO', type=str, required=True)
    parser.add_argument('--url', help='Url of AGO instance', type=str,
                        default='https://www.arcgis.com')

    args = parser.parse_args()

    gis = GIS(url=args.url, username=args.username, password=args.password)

    # Create folder for scene layers
    gis.content.create_folder(AGO_DATA_DIR)

    application = tornado.web.Application([
        (r"/file-upload", MainHandler, dict(gis=gis)),
        (r"/(.*)", tornado.web.StaticFileHandler,
         {"path": ROOT, "default_filename": "index.html"})
    ])

    # PRT Initialization
    pyprt.initialize_prt()
    application.listen(PORT)
    print(f'Listening on Port={PORT}')
    tornado.ioloop.IOLoop.instance().start()
