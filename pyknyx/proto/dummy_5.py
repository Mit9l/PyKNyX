# -*- coding: utf-8 -*-

from __future__ import print_function

from pyknyx.api import Device, FunctionalBlock
from pyknyx.core.ets import ETS

GAD_MAP = {1: {'root': "heating",
               1: {'root': "setpoint",
                   1: "living",
                   2: "bedroom 1",
                   3: "bedroom 2",
                   4: "bedroom 3"
                  },
               2: {'root': "temperature",
                   1: "living",
                   2: "bedroom 1",
                   3: "bedroom 2",
                   4: "bedroom 3"
                  }
              },
           2: {'root': "lights",
               1: {'root': None,
                   1: 'living',
                 },
               2: {'root': "etage",
                   1: None,
                   2: "bedroom 1"
                 }
              }
          }


class WeatherBlock(FunctionalBlock):

    # Datapoints definition
    DP_01 = dict(name="temperature", access="output", dptId="9.007", default=19.)
    DP_02 = dict(name="humidity", access="output", dptId="9.007", default=50.)
    DP_03 = dict(name="wind_speed", access="output", dptId="9.005", default=0.)
    DP_04 = dict(name="wind_alarm", access="output", dptId="1.005", default="No alarm")
    DP_05 = dict(name="wind_speed_limit", access="input", dptId="9.005", default=15.)
    DP_06 = dict(name="wind_alarm_enable", access="input", dptId="1.003", default="Disable")
    DP_07 = dict(name="lattitude", access="param", dptId="9.xxx", default=0.)
    DP_08 = dict(name="longitude", access="param", dptId="9.xxx", default=0.)
    DP_09 = dict(name="altitude", access="param", dptId="9.xxx", default=0.)

    # Group Objects datapoints definition (can (should?) be defined in subclass)
    GO_01 = dict(dp="temperature", flags="CRT", priority="low")
    GO_02 = dict(dp="humidity", flags="CRT", priority="low")
    GO_03 = dict(dp="wind_speed", flags="CRT", priority="low")
    GO_04 = dict(dp="wind_alarm", flags="CRT", priority="normal")
    GO_05 = dict(dp="wind_speed_limit", flags="CWTU", priority="low")
    GO_06 = dict(dp="wind_alarm_enable", flags="CWTU", priority="low")

    # Interface Object Properties datapoints definition (name will be "PID_<upper(dp.name)>")
    #PR_01 = dict(dp="lattitude")
    #PR_02 = dict(dp="longitude")
    #PR_03 = dict(dp="altitude")

    # Polling Values datapoints definition
    #PV_01 = dict(dp="temperature")

    # Memory Mapped datapoints definition
    #MM_01 = dict(dp="temperature")

    DESC = "Class-level description"

    #@Device.schedule.every(minute=5)
    def checkWindSpeed(self, event):

        # How we retrieve the speed is out of the scope of this proposal
        # speed = xxx

        # Now, write the new speed value to the Datapoint
        # This will trigger the bus notification, if a group object is associated
        self.dp["wind_speed"].value = speed

        # Check alarm speed
        if self.dp["wind_alarm_enable"].value == "Enable":
            if speed >= self.dp["wind_speed_limit"].value:
                self.dp["wind_alarm"].value = "Alarm"
            elif speed < self.dp["wind_speed_limit"].value - 5.:
                self.dp["wind_alarm"].value = "No alarm"

    #@Device.notify.datapoint(name="wind_speed")  # Single DP
    #@Device.notify.datapoint(name="temperature")  # Single DP
    #@Device.notify.datapoint(name=("wind_speed", "temperature"))  # Multiple DP
    #@Device.notify.datapoint()  # All DP
    #@Device.notify.datapoint(name="wind_speed", change=True)  # Only if value changed
    #@Device.notify.datapoint(name="wind_speed", condition="change")  # Only if value changed (could be "always")
    #@Device.notify.group(gad="1/1/1")  # Single group address
    #@Device.notify.groupObject(name="temperature")  # Single group object
    def doSomething(self, event):
        """
        event.type
        event.dp
        event.old
        event.new
        """
        pass


# Weather station class definition
class WeatherStation(Device):

    FB_01 = dict(cls=WeatherBlock, name="weather_block", desc="Instance-level description")

    LNK_01 = dict(fb="weather_block", dp="temperature", gad="1/1/1")
    LNK_02 = dict(fb="weather_block", dp="humidity", gad="1/1/2")
    LNK_03 = dict(fb="weather_block", dp="wind_speed", gad="1/1/3")
    LNK_04 = dict(fb="weather_block", dp="wind_alarm", gad="1/1/4")
    LNK_05 = dict(fb="weather_block", dp="wind_speed_limit", gad="1/1/5")
    LNK_06 = dict(fb="weather_block", dp="wind_alarm_enable", gad="1/1/6")

def main():

    ets = ETS("7.9.99")
    ets._gadMap = GAD_MAP

    # Instanciation of the weather station device object
    station = WeatherStation(ets, "1.2.3")

    ets.printGroat(by="gad")
    print()
    ets.printGroat(by="go")

if __name__ == "__main__":
    main()
