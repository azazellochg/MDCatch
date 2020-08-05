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

import os
import subprocess
# use polling as required for watchdog over NFS/CIFS
from watchdog.observers.polling import PollingObserver as Observer
from watchdog.events import RegexMatchingEventHandler

from .config import *
from .parser import Parser
from .schedule import setupRelion, setupScipion


class WatchDog:
    def __init__(self):
        self.observer = Observer()

    def start_daemon(self, path):
        """ Watch for new xml/mdoc files in METADATA_PATH. """
        if DEF_SOFTWARE == "EPU":
            regex = r".*/Images-Disc\d/GridSquare_.*/Data/FoilHole_.*_Data_.*.xml$"
        else:
            regex = r".*/.*.tif.mdoc$"
        event_handler = RegexMatchingEventHandler(regexes=[regex],
                                                  ignore_regexes=[],
                                                  ignore_directories=True,
                                                  case_sensitive=True)
        event_handler.on_created = self.on_created
        self.observer.schedule(event_handler, path, recursive=True)
        self.observer.start()
        self.observer.join()

    def on_created(self, event):
        mdFn = event.src_path
        mdFolder = mdFn.split("/")[-5]
        if mdFolder.startswith(DEF_PREFIX):  # check folder name
            self.observer.stop()
            start_app(mdFn)


def start_app(mdFn):
    """ Simulate GUI mode, setup acqDict and run parsers. """
    mdPath = "/".join(mdFn.split("/")[:-4])
    mdFolder = os.path.basename(mdPath)
    model = Parser()
    model.setSoftware(DEF_SOFTWARE)
    model.setPipeline(DEF_PIPELINE)
    model.setMdPath(mdPath)
    model.setFn(mdFn)

    username = mdFolder.split("_")[1]
    uid = mapUserid(username)
    model.setUser(username, uid)
    model.acqDict['User'] = model.getUser()

    if DEBUG:
        print("\n\nInput params: ",
              model.getSoftware(),
              model.getMdPath(),
              model.getUser(),
              model.getPipeline())
        print("\nFiles found: %s\n" % mdFn) if DEBUG else ""

    if DEF_SOFTWARE == 'EPU':
        model.parseImgEpu(mdFn)
    else:  # SerialEM
        model.parseImgMdoc(mdFn)

    model.calcDose()
    model.guessDataDir()

    if DEBUG:
        print("\nFinal parameters:\n")
        for k, v in sorted(model.acqDict.items()):
            print(k, v)
        print('\n')

    if DEF_PIPELINE == 'Relion':
        setupRelion(model.acqDict)
    else:
        setupScipion(model.acqDict)


def mapUserid(login):
    # match username with YP/NIS database
    cmd = "/usr/bin/ypmatch %s passwd" % login
    try:
        res = subprocess.check_output(cmd.split())
    except subprocess.CalledProcessError:
        print("ERROR: username %s not found! Using default uid: %s" % (
            login, DEF_USER[1]))
        return DEF_USER[1]
    except FileNotFoundError:
        print("ERROR: command %s not found! Using default uid: %s" % (
            cmd.split()[0], DEF_USER[1]))
        return DEF_USER[1]
    else:
        return str(res).split(":")[2]
