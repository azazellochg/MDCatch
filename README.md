# MDCatch
A simple app to fetch metadata from EPU (tested versions 1.10.0.77, 2.3.0.79, 2.0.13) or SerialEM. Requires python3 and PyQt5.
It parses EPU xml and SerialEM mdoc files, associated with a data collection session. In case of SerialEM you need to enable saving mdoc file for each movie.

* To run: python3 run.py
* Parameters: edit config.py
* Extra: header.py can parse tif movie header directly, without libtiff. At the moment it's not used by the app.

If you don't have PyQt5 in your system python3 and then run:
```
python3 -m venv venv
source venv/bin/activate
pip install PyQt5
```
