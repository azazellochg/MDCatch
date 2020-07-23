MDCatch
=======

A simple PyQt5 app to fetch acquisition metadata from EPU session or SerialEM.
It parses the first found xml/mrc (EPU) or mdoc file (SerialEM) associated with a data collection session and launches Relion or Scipion pipeline.
In case of SerialEM you need to enable saving mdoc file for each movie.

Installation
------------

The app requires python3, numpy (only if you parse mrc files) and PyQt5 to run.

  1) From pypi: **pip install MDCatch** (recommended)
  2) From sources - you have two options:

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


Configure
---------

  - Relion 3.1 or Scipion 3.0 is in in your *PATH*
  - Preprocessing templates: *Schedules* folder for Relion, *template.json* for Scipion
  - Edit *config.py* to adjust it to your setup
 
Running
-------

 Simply type **mdcatch**

Working principle
-----------------

The idea is to launch the app on a processing server as soon as EPU/SerialEM starts data collection and the first movie is acquired.
The server has to have access to both EPU session folder and movies folder, or to SerialEM movie folder.

  1. check if username exists in the NIS database (``ypmatch username passwd``)
  2. find and parse the first xml/mdoc file, getting all acquisition metadata
  3. create a Relion/Scipion project folder ``username_microscope_date_time`` inside PROJECT_PATH (or inside Scipion default projects folder)
  4. create symlinks for movies, gain reference, defects file, MTF in the project folder
  5. modify existing Relion Schedules/Scipion templates then launch Relion/Scipion on-the-fly processing

Screenshots
-----------

.. image:: https://user-images.githubusercontent.com/6952870/71741099-e2c6d200-2e55-11ea-9c98-66a14dc8cb2e.png
   :width: 600 px

.. image:: https://user-images.githubusercontent.com/6952870/71741103-e5292c00-2e55-11ea-95c3-4cf51de7382c.png
   :width: 800 px

TODO
----

  - Add defects file to config (only relevant for SerialEM)
  - Add class2d job to Scipion workflow. Replace Relion logpicker by crYOLO protocol