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

import sys
import os

import pyprt
from pyprt.pyprt_utils import vertices_vector_to_matrix, faces_indices_vectors_to_matrix

import numpy as np
import itertools
from vispy import app, scene, visuals
from vispy.color import Color
from vispy.geometry.meshdata import MeshData

CS_FOLDER = os.path.dirname(os.path.realpath(__file__))


def asset_file(filename):
    return os.path.join(CS_FOLDER, 'data', filename)


class Canvas(scene.SceneCanvas):
    def __init__(self, geometries_number, generated_data, generated_data_faces, window_range_xmin, window_range_xmax, window_range_ymin, window_range_ymax, window_range_zmin, window_range_zmax):
        scene.SceneCanvas.__init__(self, keys='interactive', size=(
            800, 550), show=True, title='Visualization of the generated model(s)')

        self.unfreeze()
        self.view = self.central_widget.add_view()
        self.view.camera = 'turntable'
        self.view.camera.set_range((window_range_xmin, window_range_xmax), (
            window_range_ymin, window_range_ymax), (window_range_zmin, window_range_zmax))
        self.selected_point = None
        scene.visuals.GridLines(parent=self.view.scene)

        for k in range(geometries_number):
            if generated_data_faces[k] is not None:
                mdata = MeshData(
                    vertices=generated_data[k], faces=generated_data_faces[k])

                rng = np.random.RandomState(0)
                nf = mdata.n_faces
                fcolor = np.ones((nf, 4), dtype=np.float32)
                someColors = [Color('green').RGBA, Color('yellow').RGBA, Color(
                    'blue').RGBA, Color('red').RGBA, Color('white').RGBA, Color('fuchsia').RGBA]

                for l in range(0, nf):
                    k_ind = k
                    if k >= len(someColors):
                        k_ind -= len(someColors)
                    fcolor[l] = someColors[k_ind]

                mdata.set_face_colors(fcolor)
                edge_v_index = mdata.get_edges()

                mesh = scene.visuals.Mesh(meshdata=mdata)

                mesh.set_gl_state('additive', depth_test=False)
                mlines = scene.visuals.Line(
                    pos=generated_data[k], color='red', connect=edge_v_index)

                self.view.add(mesh)
                self.view.add(mlines)

            s = scene.Markers(pos=generated_data[k])

            self.view.add(s)

        self.freeze()


if __name__ == '__main__':
    print('\nInitializing PRT.')
    pyprt.initialize_prt()

    if not pyprt.is_prt_initialized():
        raise Exception('PRT is not initialized')

    initial_geometry = pyprt.InitialShape(
        np.array([0, 0, 0,  0, 0, 2,  1, 0, 1,  1, 0, 0], dtype='f'))
    initial_geometry2 = pyprt.InitialShape(
        np.array([4, 0, 0,  4, 0, 2,  5, 0, 1,  5, 0, 0], dtype='f'))
    rpk = asset_file('extrusion_rule.rpk')
    attrs = {}

    mod = pyprt.ModelGenerator([initial_geometry, initial_geometry2])
    generated_mod = mod.generate_model(
        [attrs], rpk, 'com.esri.pyprt.PyEncoder', {})
    all_vertices = []
    all_faces = []

    for model in generated_mod:
        if model:
            geo = model.get_vertices()
            ind = model.get_indices()
            face_geo = model.get_faces()

            model_vertices = vertices_vector_to_matrix(geo)
            model_faces = faces_indices_vectors_to_matrix(ind, face_geo)

            if len(geo) > 0:
                print('Size of the model vertices matrix: (' +
                      str(len(model_vertices)) + ', 3)')
                all_vertices.append(model_vertices)
            if len(face_geo) > 0:
                print('Size (first dimension) of the model faces matrix: ' +
                      str(len(model_faces)))
                all_faces.append(model_faces)
        else:
            print('\nError while instanciating the model generator.')

    print('\nShutdown PRT.')
    pyprt.shutdown_prt()

    # Data
    mat = np.array(all_vertices).copy()
    mat[:, :, 1], mat[:, :, 2] = mat[:, :, 2], mat[:, :, 1].copy()
    mat_f = []

    xmin = np.amin(mat[:, :, 0])
    xmax = np.amax(mat[:, :, 0])
    ymin = np.amin(mat[:, :, 1])
    ymax = np.amax(mat[:, :, 1])
    zmin = np.amin(mat[:, :, 2])
    zmax = np.amax(mat[:, :, 2])

    for k in range(mat.shape[0]):
        mat_faces = []
        for f in all_faces[k]:
            if len(f) == 3:
                mat_faces.append(f)
            elif len(f) > 3:
                # in vispy, 3 vertex indices per face
                for new_f in np.array(list(itertools.combinations(f, 3))):
                    mat_faces.append(new_f)
            elif len(f) < 3:
                # repeat one vertex index
                current_ind = 0
                new_f2 = []
                while len(new_f2) < 3:
                    new_f2.append(f[current_ind])
                    if current_ind < len(f)-1:
                        current_ind += 1
                    else:
                        while len(new_f2) < 3:
                            new_f2.append(f[current_ind])
                        current_ind += 1

                mat_faces.append(new_f2)

        mat_f.append(mat_faces)

    win = Canvas(mat.shape[0], mat, np.array(mat_f),
                 xmin, xmax, ymin, ymax, zmin, zmax)
    if sys.flags.interactive != 1:
        app.run()
