# MDCatch
## Still in development, but you are welcome to try!
A simple app to fetch metadata from EPU (tested versions 1.10.0.77, 2.3.0.79, 2.0.13) or SerialEM. Requires python3 and PyQt5.
It parses the first EPU xml and SerialEM mdoc file it finds, associated with a data collection session. In case of SerialEM you need to enable saving mdoc file for each movie.

* Prerequisites / installation:
  - Python 3 and PyQt5. If you don't have PyQt5 in your system python3 then create a virtual env:
    ```
    python3 -m venv venv
    source venv/bin/activate
    pip install PyQt5
    python3 run.py
    ```
  - Relion 3.1 or Scipion 2.0 sourced in your PATH (at the moment Scipion option is disabled, sorry!)
  - Schedules folder with predefined Relion templates. For Scipion, template.json is used as a starting point.
  - Edit config.py to adjust it to your settings
* Running: `python3 run.py`. User only needs to provide: 
  - path to EPU session folder or path to folder with SerialEM movies/mdoc files
  - particle size
  - username
* Working principle:
  1. check if username exists in the NIS database (`ypmatch username passwd`)
  2. parse the xml/mdoc file
  3. create a Relion project folder `username_microscope_date_time` inside PROJECT_PATH
  4. create symlinks for movies, gain reference etc in the project folder
  5. read and modify existing Schedules then launch Relion


## Screenshots

![Screenshot_20200103_182047](https://user-images.githubusercontent.com/6952870/71741099-e2c6d200-2e55-11ea-9c98-66a14dc8cb2e.png)
![Screenshot_20200103_182116](https://user-images.githubusercontent.com/6952870/71741103-e5292c00-2e55-11ea-95c3-4cf51de7382c.png)
