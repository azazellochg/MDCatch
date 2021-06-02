# **************************************************************************
# *
# * Authors:     Grigory Sharov (gsharov@mrc-lmb.cam.ac.uk) [1]
# *
# * [1] MRC Laboratory of Molecular Biology, MRC-LMB
# *
# * This program is free software; you can redistribute it and/or modify
# * it under the terms of the GNU General Public License as published by
# * the Free Software Foundation; either version 3 of the License, or
# * (at your option) any later version.
# *
# * This program is distributed in the hope that it will be useful,
# * but WITHOUT ANY WARRANTY; without even the implied warranty of
# * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# * GNU General Public License for more details.
# *
# * You should have received a copy of the GNU General Public License
# * along with this program; if not, write to the Free Software
# * Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA
# * 02111-1307  USA
# *
# *  All comments concerning this program package may be sent to the
# *  e-mail address 'gsharov@mrc-lmb.cam.ac.uk'
# *
# **************************************************************************

# use polling as required for watchdog over NFS/CIFS
from watchdog.observers.polling import PollingObserver as Observer
from watchdog.events import RegexMatchingEventHandler

from .config import *
from .utils.misc import getUsername
from .parser import Parser
from .schedule import setupRelion, setupScipion


class WatchDog:
    def __init__(self):
        self.observer = Observer()

    def start_daemon(self, path):
        """ Watch for new xml/mdoc files in METADATA_PATH. """
        if DEF_SOFTWARE == "EPU":
            regex = r".*/%s.*/Images-Disc\d/GridSquare_.*/Data/FoilHole_.*_Data_.*.xml$" % DEF_PREFIX
        else:
            regex = r".*/%s.*/.*.tif.mdoc$" % DEF_PREFIX
        event_handler = RegexMatchingEventHandler(regexes=[regex],
                                                  ignore_regexes=[],
                                                  ignore_directories=True,
                                                  case_sensitive=True)
        event_handler.on_created = self.on_created

        print("Watchdog started for: %s\n\tregex: %s" %
              (path, regex))

        self.observer.schedule(event_handler, path, recursive=True)
        self.observer.start()
        self.observer.join()

    def on_created(self, event):
        mdFn = event.src_path
        print("File creation detected: %s" % mdFn)
        self.observer.stop()
        start_app(mdFn)


def start_app(mdFn):
    """ Simulate GUI mode, setup acqDict and run parsers. """
    if DEF_SOFTWARE == "EPU":
        mdPath = "/".join(mdFn.split("/")[:-4])
    else:
        mdPath = "/".join(mdFn.split("/")[:-1])
    model = Parser()
    model.setSoftware(DEF_SOFTWARE)
    model.setPipeline(DEF_PIPELINE)
    model.setSize(DEF_PARTICLE_SIZES)
    model.setSymmetry(DEF_SYMMETRY)
    model.setMdPath(mdPath)
    model.setFn(mdFn)

    username, uid = getUsername()
    model.setUser(username, uid)
    model.acqDict['User'] = username

    if DEBUG:
        print("\n\nInput params: ",
              model.getSoftware(),
              model.getMdPath(),
              model.getUser(),
              model.getPipeline(),
              model.getSymmetry(),
              model.getSize())

    print("\nFile found: %s\n" % mdFn)

    model.parseMetadata(mdFn)
    model.calcDose()
    model.guessDataDir(wait=True)
    model.acqDict['PtclSizes'] = DEF_PARTICLE_SIZES
    model.calcBox()

    print("\nFinal parameters:\n")
    for k, v in sorted(model.acqDict.items()):
        print(k, v)
    print('\n')

    if DEF_PIPELINE == 'Relion':
        setupRelion(model.acqDict)
    else:
        setupScipion(model.acqDict)
