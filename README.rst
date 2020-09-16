MDCatch
=======

A simple app to fetch acquisition metadata from a running EPU session or SerialEM.
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

* from pypi (recommended): **pip install MDCatch**
* from sources - you have two options:

a) create python virtualenv:

.. code-block:: python

    python3 -m venv mdcatch
    source mdcatch/bin/activate
    git clone https://github.com/azazellochg/MDCatch.git
    cd MDCatch
    pip install -e .

b) create conda virtualenv (requires conda installed):

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

NOTE: You will need to edit the code in schedule.py if you do not use default provided Schedules
 
Running
-------

To run with a GUI simply type **mdcatch**.
If you want to run in daemon mode, run **mdcatch --watch** (or better setup a daily cron job)


Working principle
-----------------

GUI mode (default)
##################

The idea is to run the app on a processing server once EPU/SerialEM starts data collection and the first movie is acquired.
The server has to have access to both EPU session folder and movies folder, or to SerialEM movie folder.

  1. find and parse the first xml/mdoc file, getting all acquisition metadata
  2. create a Relion/Scipion project folder ``username_microscope_date_time`` inside PROJECT_PATH (or inside Scipion default projects folder)
  3. create symlink for movies folder; copy gain reference, defects file, MTF into the project folder
  4. modify existing Relion Schedules/Scipion templates, copy them to the project folder then launch Relion/Scipion on-the-fly processing
  5. ACL Linux commands are executed for the project folder (so that uid has *rwx* permissions), where uid is obtained from DEF_USER

Daemon mode
###########

From version 0.9.7 onwards it's possible to run the app in fully automatic mode. It will run in the background recursively watching for new directories (directory name should start with PREFIX, e.g. lmb_username_myEpuSession) inside METADATA_PATH.
Once an xml (EPU) or a mdoc (SerialEM) file is created in such folder, the default pipeline will launch. All subsequent steps are equivalent to the GUI mode.

Make sure you have set in *config.py*: DEF_USER, DEF_SOFTWARE, DEF_PIPELINE, DEF_PREFIX, METATADA_PATH.

Though all 3 pickers can be run fully automatically, Topaz and LogPicker will most likely require particle size / threshold adjustment, so crYOLO is preferred over other pickers.

It's probably useful to setup a daily cron job for `mdcatch --watch` to detect new EPU/SerialEM sessions.

Screenshots
-----------

.. image:: https://user-images.githubusercontent.com/6952870/93343573-8c08f900-f828-11ea-9554-65cebe8414ae.png
   :width: 640 px

.. image:: https://user-images.githubusercontent.com/6952870/93343678-afcc3f00-f828-11ea-9cc7-a5848f5d1ee6.png
   :width: 640 px
