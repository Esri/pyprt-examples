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
import platform
import argparse
import shutil
import tempfile


def setup_conda_env_from_requirements(conda_cmd, conda_env, py_ver):
    os.system(f"{conda_cmd} env remove -y -n {conda_env}")
    os.system(f"{conda_cmd} env create -y -n {conda_env} --file envs/environment-py{py_ver}.yml")


# one cannot directly install/update a .tar.bz2 conda package
# first, we need to create a local channel directory and index it
def add_custom_pyprt_package(conda_cmd, conda_env, custom_pyprt_package):
    with tempfile.TemporaryDirectory(prefix="pyprt-conda-channel-") as local_channel:
        cat_name = "win-64" if platform.system() == "Windows" else "linux-64"
        dst = os.path.join(local_channel, cat_name)
        os.makedirs(dst)
        shutil.copy(src=custom_pyprt_package, dst=dst)
        os.system(f"{conda_cmd} install -y conda-index")
        os.system(f"{conda_cmd} index {local_channel}")
        os.system(f"{conda_cmd} install -y -n {conda_env} -c {local_channel} pyprt")


def run_examples(conda_cmd, conda_env):
    py_cmd = f"{conda_cmd} run -n {conda_env} python"
    os.system(f'{py_cmd} -c "import pyprt; print(pyprt.get_api_version())"')
    os.system(f"{py_cmd} ex1_python_encoder.py")
    os.system(f"{py_cmd} ex2_obj_initial_shape.py")
    os.system(f"{py_cmd} ex3_format_exporter.py")
    os.system(f"{py_cmd} ex4_multi_generations.py")


def main():
    conda_cmd_default = "%LOCALAPPDATA%\\miniconda3\\condabin\\conda" if platform.system() == "Windows" else "/opt/miniconda3/bin"

    parser = argparse.ArgumentParser(description='PyPRT conda env tests for examples')
    parser.add_argument("--py_ver", help="Python version to build for (38, ...)", type=str, required=True)
    parser.add_argument(
        '--pyprt_conda_package', help='custom pyprt build to use in conda env test', type=str, required=False)
    parser.add_argument('--conda_env_name', help='name of conda env', type=str, required=False)
    parser.add_argument("--conda_cmd", help="absolute path to conda executable", type=str,
                        default=conda_cmd_default)
    args = parser.parse_args()

    if not args.conda_env_name:
        args.conda_env_name = f"pyprt-examples-py{args.py_ver}"

    setup_conda_env_from_requirements(args.conda_cmd, args.conda_env_name, args.py_ver)
    if args.pyprt_conda_package:
        add_custom_pyprt_package(args.conda_cmd, args.conda_env_name, args.pyprt_conda_package)
    run_examples(args.conda_cmd, args.conda_env_name)


if __name__ == '__main__':
    main()
