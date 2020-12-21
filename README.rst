MDCatch
=======

A simple app to fetch acquisition metadata from a running EPU session or SerialEM.
It parses the first found xml/mrc (EPU) or mdoc/tif file (SerialEM) associated with a
data collection session and launches Relion or Scipion pipeline.

Installation
------------

You can install either using pip (recommended) or from sources.

.. raw:: html

   <details>
   <summary><a>Dependencies</a></summary>

Dependencies are installed by pip automatically:

 * python3
 * pyqt5 (GUI)
 * numpy (to parse MRC header)
 * emtable (for Relion schedules scripts)
 * watchdog (watch a folder when running in daemon mode)

.. raw:: html

   </details>
   <details>
   <summary><a>Install from pip</a></summary>

.. code-block:: python

   pip install --user MDCatch

.. raw:: html

   </details>
   <details>
   <summary><a>Install from sources</a></summary>

You have two options:

    a) create python virtualenv:

        .. code-block:: python

            python3 -m venv mdcatch
            source mdcatch/bin/activate
            git clone https://github.com/azazellochg/MDCatch.git
            cd MDCatch
            pip install -e .

    b) create conda virtualenv (requires miniconda3 installed):

        .. code-block:: python

            conda create -n mdcatch python=3.8
            conda activate mdcatch
            git clone https://github.com/azazellochg/MDCatch.git
            cd MDCatch
            pip install -e .

.. raw:: html

   </details>

Screenshots
-----------

.. image:: https://user-images.githubusercontent.com/6952870/93343573-8c08f900-f828-11ea-9554-65cebe8414ae.png
   :width: 640 px

.. image:: https://user-images.githubusercontent.com/6952870/93343678-afcc3f00-f828-11ea-9cc7-a5848f5d1ee6.png
   :width: 640 px


Running
-------

To run with a GUI simply type **mdcatch**.
If you want to run in daemon mode, run **mdcatch --watch** (see the details in the user guide below)

User guide
----------

Here you can find information about how the app works and how to configure it for your setup.

.. raw:: html

   <details>
   <summary><a>General information</a></summary>

The app is installed on a pre-processing server with GPU(s).
The server requires the following software installed:

    - `RELION 3.1 <https://www3.mrc-lmb.cam.ac.uk/relion//index.php/Main_Page>`_ or/and `Scipion 3 <http://scipion.i2pc.es/>`_
    - `CTFFIND4 <https://grigoriefflab.umassmed.edu/ctffind4>`_
    - `crYOLO <https://cryolo.readthedocs.io/>`_ or/and `Topaz <https://github.com/tbepler/topaz>`_ (installed in a conda environment)
    - `2dassess <https://github.com/cianfrocco-lab/Automatic-cryoEM-preprocessing>`_ or/and `Cinderella <https://sphire.mpg.de/wiki/doku.php?id=auto_2d_class_selection>`_ (installed in a conda environment)
    - ypmatch (part of NIS client, only used to match a folder name with username from a NIS database)

Relion and Scipion should be available from your shell **PATH**. For Ctffind make sure you have **RELION_CTFFIND_EXECUTABLE** variable defined.
Also, this server needs access to both EPU session folder (with metadata files) and
raw movies folder. In our case both storage systems are mounted via NFSv4.

.. raw:: html

   </details>
   <details>
   <summary><a>Configuration</a></summary>

Most of configuration is done in **config.py**. As explained in the next section, the app can run in either interactive (GUI) or daemon mode.
For the very first run it is useful to set **DEBUG=1** to see additional output and make sure it all works as expected.

Important points to mention:

    * camera names in the SCOPE_DICT must match the names in EPU_MOVIES_DICT, GAIN_DICT and MTF_DICT
    * since in EPU Falcon cameras are called "BM-Falcon" and Gatan cameras are called "EF-CCD", MOVIE_PATH_DICT keys should not be changed, only the values
    * you will also need to modify **Schedules/external_job_....py**, updating the path to conda environments and training models
    * Relion schedules use **/work** as the scratch (SSD) folder, you might want to change this
    * Relion schedules also use two GPUs: 0 and 1

Below is an example of folders setup on our server. Data points to movies storage, while Metadata is for EPU sessions.

.. code-block:: bash

    /mnt
    ├── Data
    │   ├── Krios1
    │   │   ├── Falcon
    │   │   └── K2
    │   ├── Krios2
    │   │   ├── Falcon
    │   │   └── K2
    │   └── Krios3
    │       ├── Falcon
    │       └── K3
    └── MetaData
        ├── Krios1
        ├── Krios2
        └── Krios3

.. raw:: html

   </details>
   <details>
   <summary><a>Working principle</a></summary>

The app can be run interactively via GUI or can be started in the background.

GUI mode
########

  1. find and parse the first metadata file, getting all acquisition metadata
  2. create a Relion/Scipion project folder ``username_microscope_date_time`` inside PROJECT_PATH (or inside Scipion default projects folder)
  3. create symlink for movies folder; copy gain reference, defects file, MTF into the project folder
  4. modify existing Relion Schedules/Scipion templates, copy them to the project folder then launch Relion/Scipion on-the-fly processing
  5. ACL Linux commands (setfacl) are executed for the project folder (so that uid has *rwx* permissions), where uid is obtained from DEF_USER

Daemon mode
###########

From version 0.9.7 onwards it's possible to run the app in fully automatic mode. It will run in the background recursively watching for new directories (directory name should start with PREFIX, e.g. lmb_username_myEpuSession) inside METADATA_PATH.
Once an xml/mrc (EPU) or a mdoc/tif (SerialEM) file is created in such folder, the default pipeline will launch. All subsequent steps are equivalent to the GUI mode (except uid which is obtained from username).

Make sure you have set in **config.py**: DEF_USER, DEF_PICKER, DEF_SOFTWARE, DEF_PIPELINE, DEF_PREFIX, METATADA_PATH.

Though all three pickers can be run fully automatically, Topaz and LogPicker will most likely require particle size / threshold adjustment, so crYOLO is preferred over other pickers.

We usually setup a daily cron job for **mdcatch --watch** that starts only if mdcatch and Relion/Scipion are not already running.
This prevents launching pre-processing on the data twice and/or concurrently.

EPU vs SerialEM
###############

When choosing EPU option, the user must browse to the EPU session folder (that contains Images-Disc folder) with the GUI.
The app will search and parse the first found xml or mrc file from that folder (see PATTERN_EPU).
The metadata folder name (EPU session name) matches the folder name with movies on a storage server.

In case of SerialEM, the movies and metadata (mdoc file) are expected to be in the same folder, so here user must select a folder with movies in the GUI.

RELION vs Scipion
#################

So far RELION cases are more tested than Scipion. With the app we only provide a single **template.json**,
so irrespective of particle picker choice crYOLO will always be used. Particle size is also ignored.
Have a look into the json file to see what pipeline will be launched.

Scipion project will be created in the default Scipion projects folder.

.. raw:: html

   </details>
   <details>
   <summary><a>Relion schedules description</a></summary>

There are two schedules: *preprocess-xxx* (where xxx is cryolo, topaz or logpicker) and *class2d*. Both are launched at the same time.

    1. Preprocess includes 5 jobs that run in a loop, processing batches of 5 movies:

        * import movies
        * motion correction (relion motioncor)
        * ctffind4-4.1.14
        * picking (crYOLO, Topaz or Relion LogPicker)
        * extraction

        The schedule will terminate if no new mics were processed by Ctffind for 240 consecutive (!) loops (~ 4h in our case).
        This helps in case a user pauses EPU session for some reason and then continues.

        .. tip:: Picking results from crYOLO or Topaz can be visualized immediately (without saving settings for Manual picking job).

    2. Class2D includes 2 jobs:

        * 2D classification
        * sorting 2D class averages (cryoassess)

        Classification starts (with 20 classes) once 5000 particles have been extracted. This class2d job will be repeated continuously, overwriting the results each time until 20000 particles is reached. Once this threshold is reached, a separate class2d job is launched with 50 classes. Then cryoassess is launched. Once that job is finished, the schedule stops.

        .. tip:: You can display the selected classes by opening the last iteration's results of the Class2D/job007 (with 20000 particles).

        .. important:: Both schedules produce output log files: *schedules_preprocess.log* and *schedules_class2d.log*

.. raw:: html

   </details>
   <details>
   <summary><a>Testing installation</a></summary>

The test only checks if the parsers are working correctly using files from *Metadata-examples* folder.
You need to define PATTERN_EPU and PATTERN_SEM in the **config.py** and then run:

.. code-block:: python

    python -m unittest mdcatch.tests

.. raw:: html

   </details>

How to cite
-----------

Please cite the code repository DOI: `10.5281/zenodo.4319193 <https://zenodo.org/record/4319193>`_

Feedback
--------

Please report bugs and suggestions for improvements as a `Github issue <https://github.com/azazellochg/MDCatch/issues/new/choose>`_.
