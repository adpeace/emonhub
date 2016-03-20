"""

  This code is released under the GNU Affero General Public License.
  
  OpenEnergyMonitor project:
  http://openenergymonitor.org

"""

import logging
from configobj import ConfigObj

class EmonHubFileSetup(object):
    """Interface to setup the hub.

    The settings attribute stores the settings of the hub. It is a
    dictionary with the following keys:

        'hub': a dictionary containing the hub settings
        'interfacers': a dictionary containing the interfacers

        The hub settings are:
        'loglevel': the logging level
        
        interfacers are dictionaries with the following keys:
        'Type': class name
        'init_settings': dictionary with initialization settings
        'runtimesettings': dictionary with runtime settings
        Initialization and runtime settings depend on the interfacer type.
    """
    def __init__(self, filename):
        # Initialization
        super(EmonHubFileSetup, self).__init__()

        self._log = logging.getLogger(__name__)
        self._filename = filename
        self.settings = ConfigObj(filename, file_error=True)

        self.check_settings()

    def check_settings(self):
        """Load settings file into self.settings.."""
        # Get settings from file
        try:
            self.settings.reload()
        except:
            import traceback
            self._log.error("Couldn't get settings", exc_info=True)
            return
        
        if not 'hub' in self.settings or not 'interfacers' in self.settings:
            self._log.warning("Configuration file missing section - required hub and interfacers")
        return True

class EmonHubSetupInitError(Exception):
    """"Raise this when init fails."""
    pass
