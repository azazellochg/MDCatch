MDCatch
=======

A simple app to fetch acquisition metadata from a EPU session or SerialEM.
It parses the first found xml/mdoc/mrc/tif file (from EPU/SerialEM) associated with a
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
 * emtable (STAR file parser)

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

.. image:: https://user-images.githubusercontent.com/6952870/126645233-5a40e5df-49bb-45ca-9612-060201d1a618.png
   :width: 640 px

.. image:: https://user-images.githubusercontent.com/6952870/126645242-651d8b1f-40fe-412c-a681-13c860e0046b.png
   :width: 640 px


Running
-------

To run with a GUI simply type **mdcatch**.
If you want to run in daemon mode, run **mdcatch --watch** (see the details in the user guide below)

.. important:: Make sure the dose per frame is correct! The reported dose is measured directly from an image (at the camera level), so it is usually lower due to sample thickness, obj. aperture and energy filtering. If you are using EER, the reported dose is per EER frame! EER movies will be fractionated such that final frames will have 1 e/A\ :sup:`2`.

User guide
----------

Here you can find information about how the app works and how to configure it for your setup.

.. raw:: html

   <details>
   <summary><a>General information</a></summary>

The app is installed on a pre-processing server with GPU(s).
The server requires the following software installed:

    - `RELION 4.0 <https://relion.readthedocs.io/en/release-4.0/>`_ or/and `Scipion 3 <http://scipion.i2pc.es/>`_
    - `CTFFIND4 <https://grigoriefflab.umassmed.edu/ctffind4>`_
    - `Topaz <https://github.com/tbepler/topaz>`_ or `crYOLO <https://cryolo.readthedocs.io/>`_ (installed in a conda environment)

Relion and/or Scipion should be available from your shell **PATH**. You also need to define the following variables:

.. code-block:: bash

    export RELION_SCRATCH_DIR="/ssd/$USER"
    export RELION_CTFFIND_EXECUTABLE=/home/gsharov/soft/ctffind
    export RELION_TOPAZ_EXECUTABLE=/home/gsharov/soft/topaz
    export RELION_PYTHON=/home/gsharov/soft/miniconda3/envs/topaz-0.2.4/bin/python  # is used by Relion's PyTorch for 2D cls sorting

*/home/gsharov/soft/topaz* is a bash script like this:

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
For the very first time it is useful to set **DEBUG=1** to see additional output and make sure it all works as expected.

Important points to mention:

    * camera names in the SCOPE_DICT must match the names in EPU_MOVIES_DICT, GAIN_DICT and MTF_DICT
    * since in EPU Falcon cameras are called "BM-Falcon" and Gatan cameras are called "EF-CCD", MOVIE_PATH_DICT keys should not be changed, only the values
    * Relion schemes use **/ssd** as the scratch (SSD) folder, you might want to change this
    * Relion schemes use two GPUs: 0-1

Below is an example of the folders setup on our server. Data points to movies storage, while Metadata is for EPU sessions.

.. code-block:: bash

    /mnt
    ├── Data
    │   ├── Krios1
    │   │   ├── Falcon3
    │   │   └── K2 (with DoseFractions folder inside)
    │   ├── Krios2
    │   │   ├── Falcon4
    │   │   └── K2 (with DoseFractions folder inside)
    │   └── Krios3
    │       ├── Falcon3
    │       └── K3 (with DoseFractions folder inside)
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
  5. modify existing Relion Schemes/Scipion template, copy them to the project folder then launch Relion/Scipion on-the-fly processing

Daemon mode
###########

From version 0.9.7 onwards it's possible to run the app in fully automatic mode. It will run in the background recursively watching for new directories (directory name should start with PREFIX, e.g. lmb_username_myEpuSession) inside METADATA_PATH.
Once an xml/mrc (EPU) or a mdoc/tif (SerialEM) file is created in such folder, the default pipeline will launch. All subsequent steps are equivalent to the GUI mode.

Make sure you have set in **config.py**: DEF_SOFTWARE, DEF_PIPELINE, DEF_PICKER, DEF_PARTICLE_SIZES, DEF_PREFIX, METATADA_PATH, BATCH_SIZE.

You could setup a daily cron job for **mdcatch --watch** that starts only if mdcatch and Relion/Scipion are not already running.
This prevents launching pre-processing on the data twice and/or concurrently.

Metadata formats
################

While EPU xml files are most rich in terms of needed metadata, other formats can be used as well. If you set PATTERN_EPU to mrc format, the app will try to parse MRC header of unaligned movie sums in the EPU session folder.
However we cannot detect number of movie frames and super-resolution mode from such a header, so you would need to check and input correct pixel size and/or fluence per frame.

In case of SerialEM, mdoc file is expected to contain a microscope D-number (see example in *tests/testdata*). If you set PATTERN_SEM to tif, the TIF header of a movie will be parsed.
Unfortunately SerialEM does not save much metadata in such header, so a lot of values will be missing. Default values will be used for microscope ID, detector, voltage and binning (see *utils/tiff.py*). So, parsing tif is not recommended.
EER header parsing is also possible, but again, it's just a special kind of TIF format.

EPU vs SerialEM
###############

When choosing EPU option, the user must browse to the EPU session folder (that contains Images-Disc folder) with the GUI.
The app will search and parse the first found xml or mrc file from that folder (depending on PATTERN_EPU).
The metadata folder name (EPU session name) matches the folder name with movies on a storage server.

In case of SerialEM, the movies and metadata (mdoc file) are expected to be in the same folder, so here user must select a folder with movies in the GUI.

RELION vs Scipion
#################

So far RELION runs are more tested than Scipion. In the latter case, the app provides a single **template.json**,
so irrespective of particle picker choice crYOLO will always be used.
Have a look into the json file to see what pipeline will be launched.

Scipion project will be created in the default Scipion projects folder.

.. raw:: html

   </details>
   <details>
   <summary><a>Relion schemes description</a></summary>

There are two schemes: *prep* and *proc-cryolo* (or *proc-topaz*). Proc is available in 3 variants: cryolo, topaz and log. Both schemes launched at the same time and will run for 12 hours

1. The *prep* scheme includes 3 jobs that run in a loop, processing batches of 50 movies each time:

    a) import movies
    b) motion correction (relion motioncor)
    c) ctffind4-4.1.14

.. important:: The movie frames will be grouped if the dose per frame is < 0.8 e/A\ :sup:`2`. EER movies are fractionated such that final frames have 1 e/A\ :sup:`2`.

2. The *proc* scheme starts once ctffind results are available. Proc includes multiple jobs:

    a) micrograph selection (CTF resolution < 6A)
    b) particle picking: Cryolo (proc-cryolo) or Topaz/Logpicker (proc-topaz)
    c) particle extraction
    d) 2D classification with 50 classes
    e) auto-selection of good 2D classes (thr=0.35)
    f) 3D initial model if number of good particles from e) is > 1500
    g) 3D refinement

The last four steps are always executed as new jobs (not overwriting previous results).

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
