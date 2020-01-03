# MDCatch
## Still in development, but you are welcome to try!
A simple PyQt5 app to fetch metadata from EPU (tested versions 1.10.0.77, 2.0.13, 2.3.0.79) or SerialEM.
It parses the first EPU xml and SerialEM mdoc file it finds, associated with a data collection session. In case of SerialEM you need to enable saving mdoc file for each movie.

### Prerequisites / installation:
  - Python 3 and PyQt5. If you don't have PyQt5 module in your system python3 then create a virtual environment:
    ```
    python3 -m venv venv
    source venv/bin/activate
    pip install PyQt5
    ```
  - Relion 3.1 or Scipion 2.0 sourced in your `PATH` (at the moment Scipion option is disabled, sorry!)
  - Preprocessing templates: `Schedules` folder for Relion, `template.json` for Scipion
  - Edit `config.py` to adjust it to your settings
 
### Running
 Simply `python3 run.py`. User only needs to provide: 
  - path to EPU session folder or path to folder with SerialEM movies/mdoc files
  - particle size
  - username

### Working principle
The idea is to launch the app on a separate OTF machine as soon as EPU/SerialEM starts data collection and the first movie is acquired.

  1. check if username exists in the NIS database (`ypmatch username passwd`)
  2. find and parse the xml/mdoc file
  3. create a Relion/Scipion project folder `username_microscope_date_time` inside PROJECT_PATH
  4. create symlinks for movies, gain reference, defects file, MTF in the project folder
  5. modify existing Schedules/Scipion template then launch Relion/Scipion on-the-fly processing

### Screenshots

![Screenshot_20200103_182047](https://user-images.githubusercontent.com/6952870/71741099-e2c6d200-2e55-11ea-9c98-66a14dc8cb2e.png)
![Screenshot_20200103_182116](https://user-images.githubusercontent.com/6952870/71741103-e5292c00-2e55-11ea-95c3-4cf51de7382c.png)

### TODO
  - beam tilt is parsed but not used since we parse only a single xml/mdoc for the whole session
  - EPU 2.3+ support (not tested yet)
  - Scipion 2.0 support (incomplete)
  - relion_scheduler should stay running in the background even when the app is closed
  