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

## streamlit credentials
Streamlit can track some usage statistics. Nothing out of the ordinary, but I prefer to not allow it. When launching the `set_config.bat` file, it will attempt to add an opt-out this to `<user_name>\.streamlit\credentials.toml` file in Windows.

## default directory
You can point the app to a default directory with your images. You can at any time in the app change to a different directory, but this one will be used when you launch the app.

## json file
Images will be annotated with labels and stored in a dictionary while the app is running. You can move files within the app, but as a backup, a json file with the annotations is created. `set_config.bat` will set the path to the json file in the `default_directory` that you set.

## categories
The `categories` used in this app are what buttons you will use to annotate files. The default is "keep, delete, fix, other". You can change the default here, or leave it blank to use the default categories. These can be changed at any time in the `config.yml` file, or on the fly in the app. The `categories` will be folders created where your annotated images will be moved.

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


<div align="center">
    <img src="images/demo.gif" width="700" height="auto"/>
    <p>Annotating images with the app.</p>
</div>