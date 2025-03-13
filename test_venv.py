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


def setup_venv_from_requirements(venv_dir, env_py, pyprt_wheel):
    venv.create(venv_dir, with_pip=True)

    py_cmd = get_python_cmd(venv_dir)
    os.system(f"{py_cmd} -m pip install --upgrade pip")
    os.system(f"{py_cmd} -m pip install --upgrade wheel")

    env_os = "windows" if platform.system() == "Windows" else "linux"
    req_file = f'envs/{env_os}/requirements-{env_py}.txt'

    # remove existing PyPRT entry in case of custom PyPRT wheel
    if pyprt_wheel:
        with open(req_file, "r") as f:
            lines = f.readlines()
        with tempfile.NamedTemporaryFile(prefix=f"reqs-filtered-{env_py}-", suffix=".txt", mode="w+", delete=False) as f:
            for line in lines:
                if 'PyPRT' not in line:
                    f.write(line)
            req_file = f.name

    os.system(f"{py_cmd} -m pip install -r {req_file}")
    if pyprt_wheel:
        add_custom_pyprt_wheel(venv_dir, pyprt_wheel)


def add_custom_pyprt_wheel(venv_dir, pyprt_wheel_path):
    py_cmd = get_python_cmd(venv_dir)
    os.system(f"{py_cmd} -m pip install --trusted-host zrh-code.esri.com --upgrade {pyprt_wheel_path}")


def run_examples(venv_dir):
    py_cmd = get_python_cmd(venv_dir)
    print(">>> CHECK VERSION:")
    os.system(f'{py_cmd} -c "import pyprt; print(pyprt.get_api_version())"')
    print(">>> EXAMPLE 1:")
    os.system(f"{py_cmd} ex1_python_encoder.py")
    print(">>> EXAMPLE 2:")
    os.system(f"{py_cmd} ex2_obj_initial_shape.py")
    print(">>> EXAMPLE 3:")
    os.system(f"{py_cmd} ex3_format_exporter.py")
    print(">>> EXAMPLE 4:")
    os.system(f"{py_cmd} ex4_multi_generations.py")
    print(">>> DONE.")


def main():
    env_py = f"py{sys.version_info[0]}{sys.version_info[1]}"

    parser = argparse.ArgumentParser(description='PyPRT venv tests for examples')
    parser.add_argument(
        '--pyprt_wheel', help='custom pyprt build to use in venv test', type=str, required=False)
    parser.add_argument('--venv_path', help='use specific venv location and keep it around', type=str, required=False)
    args = parser.parse_args()

    venv_temp_dir = None
    venv_dir = None
    if args.venv_path:
        venv_dir = args.venv_path
    else:
        venv_temp_dir = tempfile.TemporaryDirectory(prefix=f'pyprt-venv-test-py{env_py}-')
        venv_dir = venv_temp_dir.name

    setup_venv_from_requirements(venv_dir, env_py, args.pyprt_wheel)
    run_examples(venv_dir)


if __name__ == '__main__':
    main()
