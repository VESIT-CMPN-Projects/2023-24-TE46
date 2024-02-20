# Quality Assurance -- TIFR

## Introduction

The Large Hadron Collider (LHC) at CERN is the largest and most powerful particle accelerator. It accelerates protons to nearly the velocity of light and collides them at four locations around its ring. At one of its four collision points, CMS Detector acts as a giant, high-speed camera, taking 3D “photographs” of particle collisions from all directions up to 40 million times each second. For the High-Granularity Calorimeter in CMS, a sizable number of sensor modules are built across labs all around the world. In doing so, every sensor module goes through around 700 checkpoints for visual inspection. In place of the traditional methods of assessment involving manual intervention, we suggest a Quality Assurance framework analyzing components of sensor modules across various stages of assembly using deep learning-based computer vision techniques to automatically find manufacturing flaws when evaluating a large number of modules to more appropriately assess the checkpoints and increase the efficiency for production of sensor modules.

## Installing the application

Before installing the application make sure that you have installed Python in your respective system of version between Python 3.9.10 and 3.11.
### Linux
#### Through GUI
(Following Instructions are from gnome based distro with nautilus file explorer)
1. Making the scripts executable:
   1. Right Click and select properties of setup.sh
   2. On Permissions tab, checkmark "Allow executing file as program"
   3. Repeat the above steps for start.sh
2. Right click on setup.sh and "Run as a program"
3. After one time setup, just right click on start.sh and "Run as a program to start it everytime"
#### Command Line
0. Clone or Download the repository:
    ```
    git clone [https://github.com/GerraAyush/Quality-Assurance.git](url)

    ```
##### Using install and run Scripts:
   1. Make the setup and start script executable
      ```
      chmod +x setup.sh
      chmod +x start.sh
      ```
   2. Run install script:
      ```
      ./setup.sh
      ```
   3. Run the application script:
      ```
      ./start.sh
      ```
##### Manually:
   1. Install the following required pacakages through your package manager. Example given is for apt.
      ```
      sudo apt install python3 python3-pip libsane-dev xsane libsane-dev python-tk
      ``` 

   2. Inside the project directory, start a terminal. Create and activate new python virtual environment:
      ```
      python -m venv ./venv
      source ./venv/bin/activate
      ```
   3. Update pip and install requirements:
      ```
      python -m pip install --upgrade pip
      pip install -r requirements.txt
      ```
   4. Launch the Application GUI:
       ```
       python src/app.py
       ```
### Windows

Follow the below steps to install and run the application:

1. Download the ZIP file of the code from the following links. GitHub Link for Application:
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
    python.exe -m pip install --upgrade pip
    pip install -r requirements.txt
    ```
10. Navigate to the src directory.
11. Launch the application by executing the following command in the src directory.
    ```
    python3 app.py
    ```
12. When you run the above code you will see a GUI.

