MDCatch
=======

A simple PyQt5 app to fetch acquisition metadata from EPU session or SerialEM.
It parses the first found xml/mrc (EPU) or mdoc file (SerialEM) associated with a data collection session and launches Relion or Scipion pipeline.
In case of SerialEM you need to enable saving mdoc file for each movie.

Dependencies
------------

Dependencies are installed from pip automatically:

 * pyqt5 (GUI)
 * numpy (to parse MRC headers)
 * emtable (for some Relion schedules scripts)
 * watchdog (watch folder when running in daemon mode)

Installation
------------

You can install either using pip or from sources.

* From pypi (recommended): **pip install MDCatch**
* From sources - you have two options:

a) Create python virtualenv:

.. code-block:: python

    python3 -m venv mdcatch
    source mdcatch/bin/activate
    git clone https://github.com/azazellochg/MDCatch.git
    cd MDCatch
    pip install -e .

b) Create conda virtualenv (requires miniconda3 installed):

.. code-block:: python

    conda create -n mdcatch python=3.8
    conda activate mdcatch
    git clone https://github.com/azazellochg/MDCatch.git
    cd MDCatch
    pip install -e .


Configuration
-------------

  - Relion 3.1 or Scipion 3.0 is in in your *PATH*
  - Preprocessing templates: *Schedules* folder for Relion, *template.json* for Scipion
  - Edit *config.py* to adjust it to your setup
 
Running
-------

To run with a GUI simply type **mdcatch**.
If you want to run in daemon mode, run **mdcatch --watch /path/to/folder**


Working principle
-----------------

GUI mode (default)
##################

The idea is to run the app on a processing server once EPU/SerialEM starts data collection and the first movie is acquired.
The server has to have access to both EPU session folder and movies folder, or to SerialEM movie folder.

  1. find and parse the first xml/mdoc file, getting all acquisition metadata
  2. create a Relion/Scipion project folder ``username_microscope_date_time`` inside PROJECT_PATH (or inside Scipion default projects folder)
  3. create symlinks for movies, gain reference, defects file, MTF in the project folder
  4. modify existing Relion Schedules/Scipion templates then launch Relion/Scipion on-the-fly processing
  5. *setfacl -R -m u:uid:rwx* is executed on the output folder, where uid is obtained from DEF_USER

Daemon mode
###########

From version 0.9.7 it's possible to run the app in daemon mode. It will run in the background watching for a new directories (directory name should start with PREFIX_USERNAME, other folders are ignored).
Once the new directory is found and it has a first xml file (EPU) or a tif movie (SerialEM), the default pipeline will launch.
The important variables to set in *config.py* are DEF_USER, DEF_SOFTWARE, DEF_PIPELINE, DEF_PREFIX.


Screenshots
-----------

.. image:: https://user-images.githubusercontent.com/6952870/71741099-e2c6d200-2e55-11ea-9c98-66a14dc8cb2e.png
   :width: 600 px

.. image:: https://user-images.githubusercontent.com/6952870/71741103-e5292c00-2e55-11ea-95c3-4cf51de7382c.png
   :width: 800 px
