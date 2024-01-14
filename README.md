# Quality Assurance -- TIFR

## Introduction

The Large Hadron Collider (LHC) at CERN is the largest and most powerful particle accelerator. It accelerates protons to nearly the velocity of light and collides them at four locations around its ring. At one of its four collision points, CMS Detector acts as a giant, high-speed camera, taking 3D “photographs” of particle collisions from all directions up to 40 million times each second. For the High-Granularity Calorimeter in CMS, a sizable number of sensor modules are built across labs all around the world. In doing so, every sensor module goes through around 700 checkpoints for visual inspection. In place of the traditional methods of assessment involving manual intervention, we suggest a Quality Assurance framework analyzing components of sensor modules across various stages of assembly using deep learning-based computer vision techniques to automatically find manufacturing flaws when evaluating a large number of modules in order to more appropriately assess the checkpoints and increase the efficiency for production of sensor modules.

## Installing the application

Before installing the application make sure that you have installed Python in your respective system of version between Python 3.9.10 and 3.11.

### Only for Windows

Follow the below steps to install and run the application:

1. Download the ZIP file of the code from the following links. GitHub Link for Final Integrated Application:
   [https://github.com/GerraAyush/Quality-Assurance.git](url)
2. Extract the downloaded ZIP file.
3. Open a terminal window.
4. Install Python Virtual Environment if not installed already.
    ```
    py -m pip install --user virtualenv
    ```
5. Create a virtual environment for the project.
    ```
    py -m venv venv
    ```
6. Activate the virtual environment.
    ```
    .\venv\Scripts\activate
    ```
7. Your command prompt will now be prefixed with the name of your environment, in this case, it is called venv.
    ```
    Example:
    (combine) PS E:\TIFR Project>
    ```
8. Navigate to the directory where the application has been cloned.
9. Run the following command to install all requirements:
    ```
    $ python.exe -m pip install --upgrade pip
    $ pip install -r requirements.txt
    ```
10. Navigate to the src directory.
11. Launch the application by executing the following command in the src directory.
    ```
    $  python3 VideoUI.py
    ```
12. When you run the above code you will see a GUI.
