# MDCatch
A simple app to fetch metadata from EPU (tested versions 1.10.0.77, 2.3.0.79, 2.0.13) or SerialEM. Requires python3 and PyQt5.
It parses EPU xml and SerialEM mdoc files, associated with a data collection session. In case of SerialEM you need to enable saving mdoc file for each movie.

* To run: python3 run.py
* Parameters: edit config.py
* If you want to use Relion 3.1 scheduling you will need Schedules folder with a predefined template. For Scipion, template.json is used as a starting point. Both Relion or Scipion should be in PATH so the app can launch them.
* Extra: header.py can parse tif movie header directly, without libtiff. At the moment it's not used by the app.

If you don't have PyQt5 in your system python3 then create a virtual env:
```
python3 -m venv venv
source venv/bin/activate
pip install PyQt5
python3 run.py
```

## Screenshots

![Screenshot_20190921_105346](https://user-images.githubusercontent.com/6952870/65371692-1d697d80-dc5e-11e9-84c6-4e8353d87a75.png)
![Screenshot_20190921_105304](https://user-images.githubusercontent.com/6952870/65371695-1fcbd780-dc5e-11e9-8a92-4eed96976cf5.png)
