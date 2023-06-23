# Copyright (c) 2012-2023 Esri R&D Center Zurich

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

import os
import sys
import tempfile
import platform
import venv
import argparse


def get_python_cmd(venv_dir):
    bin_segment = "Scripts" if platform.system() == "Windows" else "bin"
    py_cmd = os.path.join(venv_dir, bin_segment, 'python')
    return py_cmd


def setup_venv_from_requirements(venv_dir, env_py):
    venv.create(venv_dir, with_pip=True)

    py_cmd = get_python_cmd(venv_dir)
    os.system(f"{py_cmd} -m pip install --upgrade pip")
    os.system(f"{py_cmd} -m pip install --upgrade wheel")

    env_os = "windows" if platform.system() == "Windows" else "linux"
    os.system(f"{py_cmd} -m pip install -r envs/{env_os}/requirements-{env_py}.txt")


def add_custom_pyprt_wheel(venv_dir, pyprt_wheel_path):
    py_cmd = get_python_cmd(venv_dir)
    os.system(f"{py_cmd} -m pip install --trusted-host zrh-code.esri.com --upgrade {pyprt_wheel_path}")


def run_examples(venv_dir):
    py_cmd = get_python_cmd(venv_dir)
    os.system(f"{py_cmd} ex1_python_encoder.py")
    os.system(f"{py_cmd} ex2_obj_initial_shape.py")
    os.system(f"{py_cmd} ex3_format_exporter.py")
    os.system(f"{py_cmd} ex4_multi_generations.py")


def main():
    env_py = f"py{sys.version_info[0]}{sys.version_info[1]}"

    parser = argparse.ArgumentParser(description='PyPRT venv tests for examples')
    parser.add_argument(
        '--pyprt_wheel', help='custom pyprt build to use in venv test', type=str, required=False)
    parser.add_argument('--venv_path', help='use specific venv location and keep it around', type=str, required=False)
    args = parser.parse_args()

    venv_dir = tempfile.TemporaryDirectory(
        prefix=f'pyprt-venv-test-py{env_py}') if not args.venv_path else args.venv_path

    setup_venv_from_requirements(venv_dir, env_py)
    if args.pyprt_wheel:
        add_custom_pyprt_wheel(venv_dir, args.pyprt_wheel)
    run_examples(venv_dir)


if __name__ == '__main__':
    main()
