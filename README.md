# MDCatch
A simple app to fetch metadata from EPU (tested versions 1.10.0.77, 2.3.0.79, 2.0.13) or SerialEM. Requires python3 and PyQt5.
It parses the first EPU xml and SerialEM mdoc file it finds, associated with a data collection session. In case of SerialEM you need to enable saving mdoc file for each movie.

* To run: `python3 run.py`. User only needs to provide: 
  - path to EPU session folder or path to folder with SerialEM movies/mdoc files
  - particle size
  - username
* Parameters: edit config.py
* Prerequisites: 
  - Relion 3.1 or Scipion 2.0 sourced in your PATH (at the moment Scipion option is disabled)
  - Schedules folder with a predefined Relion templates. For Scipion, template.json is used as a starting point.
* Working principle:
  1. check if username exists in the NIS database (`ypmatch username passwd`)
  2. parse the xml/mdoc file
  3. create a Relion project folder `username_microscope_date_time` inside PROJECT_PATH
  4. create symlinks for movies, gain reference etc in the project folder
  5. read and modify existing Schedules then launch Relion
* Extra: header.py can parse tif movie header directly, without libtiff. At the moment it's not used.

If you don't have PyQt5 in your system python3 then create a virtual env:
```
python3 -m venv venv
source venv/bin/activate
pip install PyQt5
python3 run.py
```

## Screenshots

![Screenshot_20200103_175240](https://user-images.githubusercontent.com/6952870/71739668-fc661a80-2e51-11ea-82de-583da59f6e69.png)
![Screenshot_20190921_105304](https://user-images.githubusercontent.com/6952870/65371695-1fcbd780-dc5e-11e9-8a92-4eed96976cf5.png)
