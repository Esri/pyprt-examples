# PyPRT Examples

<img align="left" alt="PyPRT Icon" width="40px" src="images/pyprt_logo.png" />

PyPRT provides a Python binding for the [CityEngine Procedural RunTime (PRT)](https://github.com/esri/cityengine-sdk). This enables the execution of CityEngine CGA rules within Python. PyPRT allows to easily and efficiently generate 3D geometries, process them as Python data structures and export them to [multiple 3D file formats](https://esri.github.io/cityengine-sdk/html/esri_prt_codecs.html).

This repo contains examples of PyPRT usage. You can find installation instructions and the source code in the main [PyPRT](https://github.com/Esri/pyprt) repository.

<p align="center"><img src="images/building.png" alt="green building" /></p>
<p align="center"><img src="images/generated_trees.png" alt="city with trees" /></p>

## Table of Contents

* [Requirements](#requirements)
* [Running the Examples](#running-the-examples)
* [Available Examples](#available-examples)
* [Provided Rule Packages](#provided-rule-packages)
* [Licensing Information](#licensing-information)

### More Documentation
  * [Built-In PRT Encoders and Options](https://esri.github.io/cityengine-sdk/html/esri_prt_codecs.html)
  * [Authoring of Rule Packages in CityEngine](https://doc.arcgis.com/en/cityengine/latest/help/help-rule-package.htm#ESRI_SECTION1_F9D4CCCE0EC74E5FB646A8BD141A38F9)
  * [CityEngine SDK (PRT) C++ API Reference](https://esri.github.io/cityengine-sdk/html/index.html)

## Requirements

* Windows 10/11 64bit or Linux 64bit (RHEL 7/8/9 and compatible distributions)
* Python 3.7 64bit or later. Please note, we currently provide PyPRT builds for Python 3.7 (only Windows), 3.8, 3.9 and 3.10(*). For other Python versions, please [build](https://github.com/Esri/pyprt) PyPRT yourself.
* Required Python packages: see `envs` directory

(*) A note regarding Python 3.10: The arcgis package is [not yet available for Python 3.10](https://developers.arcgis.com/python/guide/system-requirements/), therefore the examples 8, 9 and 10 are not yet supported with Python 3.10.

## Running the examples

PyPRT can be installed with `pip install pyprt` or `conda install -c esri pyprt`. To run the examples a few more packages are required, so please read on! :-)

### Using virtualenv and pip

1. Open a shell and change to the root of this example repository.
1. First time setup:
   1. Create a virtualenv: `python3.8 -m venv .venv` (replace `python3.8` with path to desired Python version if necessary)
   1. Update to latest `pip`:
      * Linux: `.venv/bin/python -m pip install --upgrade pip`
      * Windows: `.venv\Scripts\python -m pip install --upgrade pip`
    1. Update to latest `wheel`:
      * Linux: `.venv/bin/python -m pip install --upgrade wheel`
      * Windows: `.venv\Scripts\python -m pip install --upgrade wheel`
   1. Install required packages for the example - this will fetch PyPRT from PyPI and all packages necessary to run the examples (replace `py38` with the used Python version):
      * Linux: `.venv/bin/python -m pip install -r envs/linux/requirements-py38.txt`
      * Windows: `.venv\Scripts\python -m pip install -r envs\windows\requirements-py38.txt`
1. Activate the environment:
   * Linux: `source .venv/bin/activate`
   * Windows: `.venv\Scripts\activate.bat`
1. Now run the examples, e.g. `python ex1_python_encoder.py` 
1. For the examples based on Jupyter Notebooks, first start jupyter with `jupyter notebook` and then open the desired example notebook in the opened browser window.

### Alternative: using Anaconda

1. Open the Anaconda prompt and change to the directory where you checked out this repository.
1. Ensure you have a working Anaconda Python 3.8, 3.9 or 3.10 64bit installation (or additionally Python 3.7 on Windows). For other Python versions, please [build](https://github.com/Esri/pyprt) PyPRT yourself at the moment.
1. Run `conda env create --prefix env --file envs/environment-py38.yml` to install PyPRT and all dependencies for the examples (replace `py38` with the used Python version).
1. Activate the Anaconda environment: `conda activate ./env`
1. Now run e.g. `python ex1_python_encoder.py` to execute the corresponding Python script. For the examples based on Jupyter Notebooks, first run `jupyter notebook` and open the desired example notebook in the opening browser page.

### In case of issues with Jupyter Notebook
* If the map widgets in e.g. example 8 do not show up, try to [manually enable](https://developers.arcgis.com/python/guide/install-and-set-up/#install-offline) the corresponding notebook extensions:
   * `jupyter nbextension enable --py --sys-prefix widgetsnbextension`
   * `jupyter nbextension enable --py --sys-prefix arcgis`
* If the notebook examples do not open correctly in a Conda environment, try to run `conda update --all` before running `jupyter notebook`. This will make sure the packages are up-to-date.

## Available Examples

<table style="width:100%">
  <tr>
    <th>#</th>
    <th>Features</th> 
    <th>Notes</th>
  </tr>
  <tr>
    <td>1</td>
    <td>This example shows the use of the Python encoder and the encoder options for generating (or not) geometries and CGA reports. </td>
    <td> </td>
  </tr>
  <tr>
    <td>2</td>
    <td>This example demonstrates the use of an OBJ file as initial shape.</td>
    <td> </td>
  </tr>
  <tr>
    <td>3</td>
    <td>In this example, the generated models are exported as OBJ files using the PRT OBJ exporter.</td>
    <td> </td>
  </tr>
  <tr>
    <td>4</td>
    <td>This example shows the two ways of calling the generate_model function in case of multiple successive geometry generations.</td> 
    <td> </td>
  </tr>
  <tr>
    <td>5</td>
    <td>This example demonstrates how PyPRT can be used to collect a dataset stored as pandas dataframe, using the PyEncoder options.</td>
    <td> </td>
  </tr>
  <tr>
    <td>6</td>
    <td>In this examples, VisPy is used as a mesh visualization tool taking PyPRT generated model (vertices and faces) as input.</td>
    <td> </td>
  </tr>
  <tr>
    <td>7</td>
    <td>This example is about optimizing the attributes of a building generated on a parcel considering the green area of the building. SciPy is used as the optimization library.</td>
    <td><a href="https://docs.pyvista.org/">PyVista</a> is used as a visualization tool in this example.</td>
  </tr>
  <tr>
    <td>8</td>
    <td>This example demonstrates how PyPRT can be used with the <a href="https://developers.arcgis.com/python/">ArcGIS API for Python</a> in order to collect data from <a href="https://www.esri.com/en-us/arcgis/products/arcgis-online/overview">ArcGIS Online</a>, generate 3D content and publish the content back to ArcGIS Online.</td>
    <td>Please note that in order to publish and visualize the generated models, the user needs an <a href="https://developers.arcgis.com/">ArcGIS Developer account</a>. Also, the published item needs to be manually deleted from the ArcGIS Online account before the example script can be run again (we do not want to delete things from your account).</td>
  </tr>
  <tr>
    <td>9</td>
    <td>In this example, PyPRT is used as a 3D geometry converter. Using PyPRT, the <a href="https://developers.arcgis.com/javascript/">ArcGIS JavaScript API</a> and the <a href="https://developers.arcgis.com/python/">ArcGIS API for Python</a>, you can visualize your 3D model on a map in the Web.</td>
    <td>Please note that in order to publish and visualize the generated models, the user needs an <a href="https://www.esri.com/en-us/arcgis/products/create-account">ArcGIS Online account</a>. To try the example, run
	  <code>
	    python ex9_model_vis_web.py --username=my_AGO_username
      </code>
	  in your Python environment.
	</td>
  </tr>
  <tr>
    <td>10</td>
    <td>This example demonstrates how an existing Scene Layer can be updated without having to touch any related Web Scenes. We use PyPRT to create a Scene Layer with a 3d visualization of the Swiss population density. We then recreate the Scene Layer with different visualization properties and show how the Web Scene updates automatically.</td>
    <td>You might want to use the keyring package to store your credentials for arcgis.com. The example script will automatically pick them up.<br/>To store the credentials execute the following once in a terminal:<pre>$ python
>>> import keyring
>>> keyring.set_password("arcgis.com",
      "your_user", "your_password")</pre></td>
  </tr>
</table>


## Provided Rule Packages

<table style="width:100%">
  <tr>
    <th>Rule Package</th>
    <th>Shape Attributes</th>
	<th>Attributes Default Values</th>
    <th>Brief Description</th>
  </tr>
  <tr>
    <td>candler.rpk</td>
    <td>BuildingHeight<br/>
		Mode<br/>
		FloorHeight<br/>
		GroundfloorHeight<br/>
		TileWidth<br/>
		CorniceOverhang<br/>
		WindowHeight<br/>
		FrontWindowWidth<br/>
		RearWindowWidth<br/>
		SillSize<br/>
		CornerWallWidth<br/>
		WallTexture<br/>
		ColorizeWall</td>
	<td>62.0<br/>
		"Visualization"<br/>
		3.5<br/>
		4.3<br/>
		3.55<br/>
		1.2<br/>
		2.05<br/>
		2.15<br/>
		1.2<br/>
		0.26<br/>
		1.0<br/>
		"facade/walls/bricks.jpg"<br/>
		"#FCEFE2"</td>
    <td>Allows generating a "candler" building model, which is textured, detailed and realistic.</td>
  </tr>
  <tr>
    <td>envelope2002.rpk</td>
    <td>Density_bonus_height<br/>
		shape_of_building<br/>
		lot_coverage_parameter<br/>
		height_first_tier<br/>
		first_setback_size<br/>
		height_second_tier<br/>
		second_setback_size<br/>
		ground_floors_use<br/>
		main_building_use<br/>
		create_green_spaces<br/>
		report_but_not_display_green<br/>
		etc...</td>
	<td>60.0<br/>
		1.0<br/>
		60.0<br/>
		12.2<br/>
		3.0<br/>
		40.0<br/>
		3.0<br/>
		"commercial"<br/>
		"residential"<br/>
		false<br/>
		false<br/>
		etc...</td>
    <td>Allows generating a realistic and detailed building.</td>
  </tr>
  <tr>
    <td>extrusion_rule.rpk</td>
    <td>minBuildingHeight<br/>
		maxBuildingHeight<br/>
		buildingColor<br/>
		OBJECTID<br/>
		text</td>
	<td>10.0<br/>
		30.0<br/>
		"#FF00FF"<br/>
		0.0<br/>
		"salut"</td>
    <td>Performs a simple extrusion of the initial shape with a height equals to a random number between the min and maxBuildingHeight.</td>
  </tr>
  <tr>
    <td>noRule.rpk</td>
    <td/>
	<td/>
    <td>Performs the identity operation.</td>
  </tr>
  <tr>
    <td>translateModel.rpk</td>
    <td>vec_x<br/>
		vec_y<br/>
		vec_z</td>
	<td>0.0<br/>
		0.0<br/>
		0.0</td>
    <td>Allows translating the initial shape in x, y and z directions.</td>
  </tr>
</table>

## Licensing Information

PyPRT is free for personal, educational, and non-commercial use. Commercial use requires at least one commercial license of the latest CityEngine version installed in the organization. Redistribution or web service offerings are not allowed unless expressly permitted.

PyPRT is under the same license as the included [CityEngine SDK](https://github.com/esri/cityengine-sdk#licensing). An exception is the PyPRT source code (without CityEngine SDK, binaries, or object code), which is licensed under the Apache License, Version 2.0 (the “License”); you may not use this work except in compliance with the License. You may obtain a copy of the License at https://www.apache.org/licenses/LICENSE-2.0.

All content in the "Examples" directory/section is licensed under the APACHE 2.0 license as well.

For questions or enquiries, please contact the Esri CityEngine team (cityengine-info@esri.com).

[Back to top](#table-of-contents)

[Go to source code](https://github.com/Esri/pyprt)
