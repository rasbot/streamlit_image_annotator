<div align="center">
    <img src="images/logo.png" width="700" height="auto"/>
<p>An annotation tool to sort through images, useful when generating a lot of images with Stable Diffusion.</p>
</div>

## Table of Contents

* [Introduction](#introduction)
* [Installation](#installation)
* [Config](#config)
* [Using the App](#using-the-app)
  * [App Demo](#app-demo)

# Introduction

<div align="center">
    <img src="images/app_layout.png" width="500" height="auto"/>
    <p>Image Annotator interface.</p>
</div>

This tool is helpful to sort images. A good use-case is when generating images with Stable Diffusion, it is possible to batch generate a lot of images. You might want to sort them, and looking at them in a file explorer is difficult if you cannot see the whole image.

## Example:

You generate 50 images with a prompt like "a photo of two people in casual business attire shaking hands, office setting".

When looking at the resulting images you might want to organize them into categories like "keep", "delete", "fix", where the "fix" option could be so you can inpaint to fix any details. Maybe your business people have funny hands?

This app gives you a UI to go through images and organize them into different categories, where you can move them into folders for easy organization.

# Installation

This app uses `streamlit` and has issues with some versions of Python. 3.9.7 does not work specifically. I am using 3.9.12. I have not tested other versions, so I suggest using 3.9.12 for now.

__Note: This installation guide is for Windows. Please adjust accordingly if you are using Linux or Mac.__

You can create a virtual environment with `conda` if you do not have an installation of 3.9.12.  Or, if you have an environment with 3.9.12, you can use `venv` by pointing it to that installation. First you will need to clone this repo.

1. Create a conda environment with Python 3.9.12, or if you already have one, pat yourself on the back and move on to step 2.
```bash
> conda create --name streamlit python=3.9.12
```

2. Clone this repo using:
```bash
> git clone https://github.com/rasbot/streamlit_image_annotator
```

3. If you are not going to use a conda environment, you can use `venv` (if you already have an installation of 3.9.12). Navigate to the repo directory and use:
```bash
> "path to python 3.9.12 executable"  -m venv venv
```

For my installation, I had one in another conda environment so the path to the executable was "C:\users\<my_username>\anaconda3\envs\py3912\python.exe"

4. Activate your virtual environment. If using `conda`, just use:
```bash
> conda activate streamlit
```
If you named it streamlit (as I did in the above example). Or, for `venv`:
```bash
> .\venv\Scripts\activate
```

5. Install requirements:
```bash
> pip install -r requirements.txt
```

# Config

A few options can be configured to running `set_config.bat`. This file will write config values to `config.yml`. You can manually set these values at any time.

## set_config.bat

### streamlit credentials
Streamlit can track some usage statistics. Nothing out of the ordinary, but I prefer to not allow it. When launching the `set_config.bat` file, it will attempt to add an opt-out this to `<user_name>\.streamlit\credentials.toml` file in Windows.

### default directory
You can point the app to a default directory with your images. You can at any time in the app change to a different directory, but this one will be used when you launch the app.

### default categories
The `default_categories` used in this app are what buttons you will use to annotate files. The defaults are "keep, delete, fix, other". You can change the defaults here, or leave it blank to use the default categories. These can be changed at any time in the `config.yml` file, or on the fly in the app. The `default_categories` will be folders created where your annotated images will be moved.

## config.yml

Other than the variables set using `set_config.bat`, there are a few other variables to mention.

### clamp image
This is the default value for if image heights will be clamped. Since larger images will not be completely visible in your browser, the image can be clamped to a height value. This can be toggled on/off in the UI, so this simply sets the default behavior whenever you launch the app.

### image height clamp
This is a integer value of the number if image pixels to clamp. The value set at 896 was what worked for my browswer / monitor. Ideally this should be the largest value that displays the whole height of the image. As mentioned, larger images can be toggled to their full resolution in the UI at any time.

### filter files
This will most likely never be changed, but if you have other image files outside of png and jpg images, you can add them to the list here, otherwise they will not be included in the images shown when using the app.

# Using the App

Launch the app from the repo directory in your terminal:
```bash
> streamlit run .\annotatator.py
```
Which will launch the app in a browser and point to the `default_directory` folder. You can easily change folders in the UI if you are not in the folder you want to use. Click on the "Expand for more options" if it is collapsed. Change the folder path and hit enter.
<div align="center">
    <img src="images/change_folder.gif" width="700" height="auto"/>
    <p>Change the folder path.</p>
</div>

The buttons correspond to the categories provided in the "annotation button names" field. You can change them and upon hitting enter, the UI will refresh the button names.
<div align="center">
    <img src="images/buttons.gif" width="700" height="auto"/>
    <p>Change the button names (categories).</p>
</div>

## App Demo

Annotating / moving images into labeled folders is fairly straightforward. When you have specified a directory that has images, you simply click on the button you want to sort the image to. Each named button category will have a folder with the same name created in the image directory. If you label an image as "really cool image", and the next image as "delete", you will have 2 folders created, "really cool image" and "delete", with the two images being moved to their respective folders.
<div align="center">
    <img src="images/demo.gif" width="900" height="auto"/>
    <p>Annotating images with the app.</p>
</div>
You can change / add buttons on the fly, which will result in different folders being created when the `Move Files` button is pressed.

## Expand for more options
There is a collapsible menu with the directory path, the button names, and a few other options. This is collapsible in case you want to hide the directory path. Some of the sections have been mentioned, so this is to address the other sections not mentioned.

### Hide Image Button
Clicking this will create a button at the top which can be used to hide the current image. The button is named `CLEAR`, and can toggle the image being displayed.

### Reset Annotations?
This will simply delete any annotations that have been stored.
<div align="center">
    <img src="images/more_options.gif" width="700" height="auto"/>
    <p>Hiding the current image and clearing annotations.</p>
</div>

### JSON file
All of the annotation data is stored within the app when running, but as a backup a JSON file is created that temporarily stores the annotations. This was originally the way the annotations were stored and a separate script was called to move the files, but this can also be used as a backup in case the app is closed before you hit `Move Files`. Once any files are moved, they will be removed from the JSON file.
<div align="center">
    <img src="images/json.gif" width="900" height="auto"/>
    <p>Writing to the JSON file.</p>
</div>
Regardless of the image directory you are in, the JSON file will be stored in the location stored in the config file (config.yml).