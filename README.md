# PyPRT Examples

<img alt="PyPRT Icon" width="40px" src="images/pyprt_logo.png" />

PyPRT is a Python binding for PRT (CityEngine Procedural Runtime). It enables the execution of CityEngine CGA rules within Python. PyPRT allows to easily and efficiently generate 3D geometries.

This repo contains examples of PyPRT usage. You can find the source code in the main [PyPRT](https://github.com/Esri/pyprt) repository. More detailed information is available there.

<p align="center"><img src="images/building.png" alt="green building" /></p>
<p align="center"><img src="images/generated_trees.png" alt="city with trees" /></p>

## Table of Contents

* [Requirements](#requirements)
* [Running the examples](#running-the-examples)
* [Available Examples](#available-examples)
* [Provided Rule Packages](#provided-rule-packages)
* [License](#license)

## Requirements

* Windows 10 64bit or Linux 64bit (RHEL7/CentOS7 compatible distro)
* Python 3.6 64bit or later. Please note, we currently provide PyPRT builds for Python 3.6 and Python 3.8. For other Python versions, please [build](https://github.com/Esri/pyprt) PyPRT yourself. 

## Running the examples

### Using Virtualenv

1. Open a terminal with Python available and change to the root of this example repository.
1. Create a virtualenv: `python3.8 -m venv .venv` (change Python version if necessary)
1. Update to latest `pip`: `.venv/bin/python -m pip install --upgrade pip`
1. Install required packages for these examples: `.venv/bin/python -m pip install -r envs/py38/requirements.txt`. This will fetch PyPRT from PyPI and all packages necessary to run the examples.
1. Now run e.g. `.venv/bin/python ex1_python_encoder.py` to execute the corresponding Python script. For the examples based on Jupyter Notebooks, first run `.venv/bin/jupyter notebook` and open the desired example notebook in the opening browser page.

### Using Anaconda

1. Open the Anaconda prompt and change to the directory where you checked out this repository.
1. Ensure you have a working Python 3.6 64bit installation. For other Python versions, please [build](https://github.com/Esri/pyprt) PyPRT yourself at the moment.
1. Run `conda env create --prefix ./env --file environment.yml` to install PyPRT and all dependencies for the examples.
1. Activate the Anaconda environment: `activate ./env`
1. Now run e.g. `python ex1_python_encoder.py` to execute the corresponding Python script. For the examples based on Jupyter Notebooks, first run `jupyter notebook` and open the desired example notebook in the opening browser page.

## Available Examples

<table style="width:100%">
  <tr>
    <th>Name</th>
    <th>Features</th> 
    <th>Notes</th>
  </tr>
  <tr>
    <td>ex1_python_encoder.py</td>
    <td>This example shows the use of the Python encoder and the encoder options for generating (or not) geometries and CGA reports. </td>
    <td> </td>
  </tr>
  <tr>
    <td>ex2_obj_initial_shape.py</td>
    <td>This example demonstrates the use of an OBJ file as initial shape.</td>
    <td> </td>
  </tr>
  <tr>
    <td>ex3_format_exporter.py</td>
    <td>In this example, the generated models are exported as OBJ files using the PRT OBJ exporter.</td>
    <td> </td>
  </tr>
  <tr>
    <td>ex4_multi_generations.py</td>
    <td>This example shows the two ways of calling the generate_model function in case of multiple successive geometry generations.</td> 
    <td> </td>
  </tr>
  <tr>
    <td>ex5_dataset_collection.ipynb</td>
    <td>This example demonstrates how PyPRT can be used to collect a dataset stored as pandas dataframe, using the PyEncoder options.</td>
    <td> </td>
  </tr>
  <tr>
    <td>ex6_3d_visualization_vispy.py</td>
    <td>In this examples, VisPy is used as a mesh visualization tool taking PyPRT generated model (vertices and faces) as input.</td>
    <td> </td>
  </tr>
  <tr>
    <td>ex7_building_modeling_optimization.ipynb</td>
    <td>This example is about optimizing the attributes of a building generated on a parcel considering the green area of the building. SciPy is used as the optimization library.</td>
    <td><a href="https://pypi.org/project/PyGEL3D">PyGEL3D</a> is used as a visualization tool in this example. Unfortunately the pre-built package of PyGEL3D on PyPI is broken for Linux (you can <a href="https://github.com/janba/GEL">try</a> to build it locally).</td>
  </tr>
  <tr>
    <td>ex8_3d_gis_content_generation.ipynb</td>
    <td>This example demonstrates how PyPRT can be used with the <a href="https://developers.arcgis.com/python/">ArcGIS API for Python</a> in order to collect data from <a href="https://www.esri.com/en-us/arcgis/products/arcgis-online/overview">ArcGIS Online</a>, generate 3D content and publish the content back to ArcGIS Online.</td>
    <td>Please note that in order to publish and visualize the generated models, the user needs an <a href="https://developers.arcgis.com/">ArcGIS Developer account</a>. Also, the published item needs to be manually deleted from the ArcGIS Online account before the example script can be run again (we do not want to delete things from your account).</td>
  </tr>
  <tr>
    <td>ex9_model_vis_web.py</td>
    <td>In this example, PyPRT is used as a 3D geometry converter. Using PyPRT, the <a href="https://developers.arcgis.com/javascript/">ArcGIS JavaScript API</a> and the <a href="https://developers.arcgis.com/python/">ArcGIS API for Python</a>, you can visualize your 3D model on a map in the Web.</td>
    <td>Please note that in order to publish and visualize the generated models, the user needs an <a href="https://www.esri.com/en-us/arcgis/products/create-account">ArcGIS Online account</a>. To try the example, run
	  <code>
	    python ex9_model_vis_web.py --username=my_AGO_username
      </code>
	  in your Python environment.
	</td>
  </tr>
</table>


## Provided Rule Packages

<table style="width:100%">
  <tr>
    <th>Rule Package</th>
    <th>CGB Rule File</th>
	<th>Start Rule</th> 
    <th>Shape Attributes</th>
	<th>Attributes Default Values</th>
    <th>Brief Description</th>
  </tr>
  <tr>
    <td>candler.rpk</td>
    <td>bin/candler.cgb</td>
	<td>Default$Footprint</td>
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
    <td>rules/typology/envelope2002.cgb</td>
    <td>Default$Lot</td>
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
    <td>bin/extrusion_rule.cgb</td>
    <td>Default$Footprint</td>
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
    <td>bin/noRule.cgb</td>
    <td>Default$Lot</td>
    <td> </td>
	<td> </td>
    <td>Performs the identity operation.</td>
  </tr>
  <tr>
    <td>translateModel.rpk</td>
    <td>bin/translateModel.cgb</td>
    <td>Default$Lot</td>
    <td>vec_x<br/>
		vec_y<br/>
		vec_z</td>
	<td>0.0<br/>
		0.0<br/>
		0.0</td>
    <td>Allows translating the initial shape in x, y and z directions.</td>
  </tr>
</table>

## License

PyPRT is under the same license as the included [CityEngine SDK](https://github.com/Esri/esri-cityengine-sdk#licensing).

An exception is the PyPRT source code (without CityEngine SDK, binaries, or object code), which is licensed under the Apache License, Version 2.0 (the “License”); you may not use this work except in compliance with the License. You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0.

[Back to top](#table-of-contents)

[Go to source code](https://github.com/Esri/pyprt)
