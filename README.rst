MDCatch
=======

A simple app to fetch acquisition metadata from a EPU session or SerialEM.
It parses the first found xml/mdoc/mrc/tif/eer file (from EPU/SerialEM) associated with a
data collection session and launches Relion 4 or Scipion 3 pipeline.

Installation
------------

You can install either using pip (recommended) or from sources.

.. raw:: html

   <details>
   <summary><a>Dependencies</a></summary>

Dependencies are installed by pip automatically:

 * python3
 * pyqt5 (GUI)
 * mrcfile (to parse MRC header)
 * tifffile (to parse TIF header)
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

    - `RELION 4.0 <https://www3.mrc-lmb.cam.ac.uk/relion//index.php/Main_Page>`_ or/and `Scipion 3 <http://scipion.i2pc.es/>`_
    - `CTFFIND4 <https://grigoriefflab.umassmed.edu/ctffind4>`_
    - `Topaz <https://github.com/tbepler/topaz>`_ (installed in a conda environment)

Relion and/or Scipion should be available from your shell **PATH**. For Ctffind make sure you have **RELION_CTFFIND_EXECUTABLE** variable defined.
For Topaz define e.g. **RELION_TOPAZ_EXECUTABLE=topaz** variable, where *topaz* is a bash script like this:

.. code-block:: bash

    #!/bin/bash
    source /home/gsharov/soft/miniconda3/bin/activate topaz-0.2.4
    topaz $@

Also, this server needs access to both EPU session folder (with metadata files) and
raw movies folder. In our case both storage systems are mounted via NFSv4.

.. raw:: html

   </details>
   <details>
   <summary><a>Configuration</a></summary>

Most of the configuration is done in **config.py**. As explained in the next section, the app can run in either interactive (GUI) or daemon mode.
For the very first run it is useful to set **DEBUG=1** to see additional output and make sure it all works as expected.

Important points to mention:

    * camera names in the SCOPE_DICT must match the names in EPU_MOVIES_DICT, GAIN_DICT and MTF_DICT
    * since in EPU Falcon cameras are called "BM-Falcon" and Gatan cameras are called "EF-CCD", MOVIE_PATH_DICT keys should not be changed, only the values
    * Relion schedules use **/ssd** as the scratch (SSD) folder, you might want to change this
    * Relion schedules also use two GPUs: 0 and 1

Below is an example of the folders setup on our server. Data points to movies storage, while Metadata is for EPU sessions.

.. code-block:: bash

    /mnt
    ├── Data
    │   ├── Krios1
    │   │   ├── Falcon3
    │   │   └── K2
    │   ├── Krios2
    │   │   ├── Falcon4
    │   │   └── K2
    │   └── Krios3
    │       ├── Falcon3
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
  4. save found acquisition params in a text file (e.g. ``EPU_session_params``), save Relion params in ``relion_it_options.py``
  5. modify existing Relion Schedules/Scipion templates, copy them to the project folder then launch Relion/Scipion on-the-fly processing

Daemon mode
###########

From version 0.9.7 onwards it's possible to run the app in fully automatic mode. It will run in the background recursively watching for new directories (directory name should start with PREFIX, e.g. lmb_username_myEpuSession) inside METADATA_PATH.
Once an xml/mrc (EPU) or a mdoc/tif (SerialEM) file is created in such folder, the default pipeline will launch. All subsequent steps are equivalent to the GUI mode.

Make sure you have set in **config.py**: DEF_SOFTWARE, DEF_PIPELINE, DEF_PREFIX, METATADA_PATH.

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

So far RELION cases are more tested than Scipion. In the latter case, the app provides a single **template.json**,
so irrespective of particle picker choice crYOLO will always be used. Particle size is also ignored.
Have a look into the json file to see what pipeline will be launched.

Scipion project will be created in the default Scipion projects folder.

.. raw:: html

   </details>
   <details>
   <summary><a>Relion schedules description</a></summary>

There are two schedules: *prep* and *proc*. Both are launched at the same time.

    1. Prep includes 3 jobs that run in a loop, processing batches of 5 movies:

        * import movies
        * motion correction (relion motioncor)
        * ctffind4-4.1.14

        The schedule will terminate if no new mics were imported for ~ 4h.
        This helps in case a user pauses EPU session for some reason and then continues.

    2. Proc includes multiple jobs:

        * micrograph selection (CTF res < 6A)
        * particle picking (Topaz)
        * particle extration
        * 2D classification
        * subset selections for particles/classes, auto-selection of good 2D classes
        * 3D initial model and refinement

        The proc schedule starts once ctffind results are available. The first 2D classification starts (with 25 classes) once 10000 particles have been extracted. After the classification, the best class averages are auto-selected and the corresponding particles are used for Topaz model training. Then all micrographs are picked again with the new model followed by extraction and another 2D classification (with 50 classes).

.. raw:: html

   </details>
   <details>
   <summary><a>Testing installation</a></summary>

The test only checks if the parsers are working correctly using files from *tests/testdata* folder.

.. code-block:: python

    python -m unittest mdcatch.tests

.. raw:: html

   </details>

How to cite
-----------

Please cite the code repository DOI: `10.5281/zenodo.4383190 <http://doi.org/10.5281/zenodo.4383190>`_

Feedback
--------

Please report bugs and suggestions for improvements as a `Github issue <https://github.com/azazellochg/MDCatch/issues/new/choose>`_.
