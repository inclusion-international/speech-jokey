# Speech Jokey

This project is about building an application which synthesizes speech from user-provided text. The application is written in Python and uses the [Kivy](https://kivy.org/#home) framework for the user interface.

Implementing intonations and emotions is still a significant challenge in the Assistive Technology applications of Text-To-Speech, but it would definitely enhance the communication experience for people with speech impairment. The aim of Speech Jokey is therefore to allow people with communication difficulties to interact with more intonation, emotions and emphasis pauses. 
In addition, the application is specifically designed to be used with eye tracking systems, facilitating the positioning of the cursor between lines and words of a text.  

Like a DJ, this application allows you to create your own text with impressive emotions, different intonations and meaningful pauses as voice output just the way you like it, which explains the name Speech Jokey.

The designed logo for the application is currently: 

![speech-jokey](https://github.com/HackXIt/assist-heidi-speech-jokey/assets/1595680/b5cd0eb0-2baa-4a0c-b463-ace9526c8def)

A [video showcase](https://github.com/HackXIt/assist-heidi-speech-jokey/blob/f180d5f0ac2c26254804e884c03c75cedc8ba890/doc/SpeechJokey_PreRelease-Development_Showcase.mp4) of the current project state of the running application can be found in the `/doc` folder.

## Speech synthesis
The application currently supports the following speech synthesis engines:
* ElevenLabs API

# Project setup
The project is based on Python `3.11`, but it also supports lower version down to `3.9`. To install Python, follow the instructions on the [Python website](https://www.python.org/downloads/).

## Install dependencies
We use poetry for dependency management. To install poetry, please check their [installation instructions](https://python-poetry.org/docs/main/#installing-with-the-official-installer). Or simply install it by running:

```
pip install poetry
```

Then make sure to configure poetry to install the virtual environment in the project root. This can be done by running:
```
poetry config virtualenvs.in-project true
```

### Linux specific dependencies

Please install the following packages first:
```
sudo apt-get install xsel xclip
```

### Python dependency installation

Installing the virtual environment is done by running:
```
poetry install --no-root
```

## Installing ffmpeg
To be able to generate and play audio files with the ElevenLabs API you additionally need the multimedia framework FFmpeg.

### Windows
To install it on Windows, follow the instructions on [this website](https://phoenixnap.com/kb/ffmpeg-windows). This includes downloading the source Code and adding ffmpeg to the Path variable.

After updating the Path variable it is important to restart your IDE (e.g. PyCharm or VSCode). 

### Mac/OS
To install it on Mac/OS, follow the instructions on [this website](https://phoenixnap.com/kb/ffmpeg-mac).

[comment]: <> (Have to try that!)

### Linux/Ubuntu
To install it on Linux/Ubuntu, follow the instructions on [this website](https://phoenixnap.com/kb/install-ffmpeg-ubuntu).

[comment]: <> (Have to try that!)

# Managing Dependencies
The dependencies are listed in the [pyproject.toml](pyproject.toml) file. To add a new dependency, run:
```
poetry add <dependency>
```

# Project building
The following procedures assume that you have installed the dependencies and that you are working inside the virtual environment.

## Running the application (Any OS / Development)
To run the application, execute the following command in the root of the project:
```
poetry run python src/main.py
```

[comment]: <> (Maybe add description on how to run it by selecting the main.py and running it with Pycharm)

## Building the application executable (Windows / Local Development)
To build the application, execute the following command in the root of the project:

_(You might wanna grab a coffee while running this)_
```
poetry run pyinstaller src/main.py --onefile --name SpeechJokey
```

The created build application specification `SpeechJokey.spec` can now be found in the root of the project.
This file needs to be modified according to the following steps:
1. Import kivy dependencies at the top of the file: `from kivy_deps import sdl2, glew`
2. Add source tree after `COLLECT(exe,`: `Tree('src\\'),`
3. Add source dependencies after `a.datas,`: `*[Tree(p) for p in (sdl2.dep_bins + glew.dep_bins)],`

After these modifications, the application can be finalized by running:

_(Should be very quick after the initial build)_
```
poetry run pyinstaller SpeechJokey.spec
```

Inside the `dist` output folder a folder with the name `SpeechJokey` can be found. This folder contains the final `.exe` build of the application.

For a detailed step-by-step guide on how to build a Kivy application, see [this written tutorial](https://github.com/CovidCoder/Kivy-App-Package-Windows-Tutorial/blob/master/KivyPackageTut.md). 
_(Keep in mind that the tutorial doesn't use poetry, so any command should be preceeded by `poetry run`)_

## Building the application executable (Windows / CI)
To build the application similar to how it would be built by the CI, copy the `SpeechJokey.spec` from `.github\static` to the project root and then execute the following command in the root of the project:
```
poetry run pyinstaller SpeechJokey.spec
```

# Intended features  

This is what the application currently looks like.

![picture of application](./doc/picture%20of%20application.png)


Some of the screenshots following this are a little different, but hopefully they get the concept across for others to contribute.

## Loading the text
Using the loading button, the user can select a saved text file and upload it in the text input. The text can still be edited.

<details><summary>Load</summary><img width="933" alt="f61731c8-2529-4369-a9df-3a00e0e86f1c" src="https://github.com/HackXIt/assist-heidi-speech-jokey/assets/1595680/672ef958-2c51-4865-afd5-3eaabe9c43be"></details>

## Editing the text
To simplify editing the text, the cursor set via eye tracker is always placed at the end of a word. To move the cursor one position to the left or right, the user can use the arrow buttons at the bottom left of the application.

<details><summary>Editing</summary><img width="935" alt="9fe969ae-a399-4d36-9f8d-ca0d118edc63" src="https://github.com/HackXIt/assist-heidi-speech-jokey/assets/1595680/ce8be5b4-ce4c-4943-befc-1e5fc54878d9"></details>

The editing feature is adressed especially to people who need eye tracking devices to move the cursor. 

## Selecting voice
The voice can be selected using the voice selection button or in the settings. All available voices are listed and the selected voice is displayed. 

## Selecting model
The model can be selected in the settings. All available models are listed and the selected model is displayed. 

## Entering API Key
To use ElevenLabs API the generated API Key must be entered in the settings.

## SSML features for encoding intonation
To change the intonation adding breaks into text, shortcuts are implented. The break time can be adjusted in the code:
* , adds a break of 0.0s
* . adds a break of 0.5s
* ; adds a break of 0.5s

<details><summary>Add Break</summary><img width="932" alt="39508a72-aee9-49f7-aa97-c2bd5eb76607" src="https://github.com/HackXIt/assist-heidi-speech-jokey/assets/1595680/2dff8a4d-2ef7-4245-b596-6584dd006c25"></details>

## Synthesizing of an audio file 
An audio file is generated using the synthesizing button. 

## Playing the audio file
Before playing the audio file, an audio file has to be synthesized using the synthesizing button.

## Saving the text file 
The final version of the edited text can be saved as a text file.

## Demonstration of SpeechJokey
Here is a video of the intended features of the application.

<video src=".\src\assets\speech-jokey-demo.mp4" controls></video>

# Tutorials for beginner contributors
## How to use Git
Git is a version control system. It allows you to keep track of changes made to your code and to collaborate with others. To learn more about Git, see [this fundamental beginner tutorial](https://www.youtube.com/watch?v=HVsySz-h9r4).

Alternatively, you can play the [Git game](https://ohmygit.org/) to learn git interactively.

## How to use GitHub
GitHub is a platform for hosting Git repositories. It allows you to collaborate with others on your code. To learn more about GitHub, see [this crash course](https://www.youtube.com/watch?v=iv8rSLsi1xo).

## How to use VS Code
VS Code is a code editor. It allows you to write code and to collaborate with others. To learn more about VS Code, see [this crash course](https://www.youtube.com/watch?v=WPqXP_kLzpo).

## How to use Kivy
Kivy is a framework for building user interfaces. It allows you to build user interfaces for your application. To learn more about Kivy, watch [this playlist](https://www.youtube.com/playlist?list=PLCC34OHNcOtpz7PJQ7Tv7hqFBP_xDDjqg) for a beginner friendly introduction to the framework.

## How-to use poetry
Poetry is a tool for dependency management and packaging in Python. It allows you to declare the libraries your project depends on and it will manage (install/update) them for you.
For a short introduction to poetry, see [this tutorial](https://python-poetry.org/docs/basic-usage/).
