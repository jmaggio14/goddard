'''
ark9719
6/17/2016
'''
import re
import time
import logging
import sys

class Mars(object):
    """
    Mars is in control of pulling data from the arduino and generating relevant telemetry statistics. This includes
    stats on time, battery, distance, power, and more.
    """

    def __init__(self, arduino, config):
        self._arduino = arduino
        self._config = config
        self._integTime = time.time()
        self._currentBattery = self._config.constants.totalBattery

        statistics = {}
        self._statistics = statistics
        statistics.setdefault('Total Distance', 0)
        statistics.setdefault('Interval Distance', 0)
        statistics.setdefault('Interval Displacement', 0)
        statistics.setdefault('Total Displacement', 0)
        statistics.setdefault('Battery Remaining', self._config.battery.remaining)




    def generateStatistics(self):
        """
        Through raw data and the work of helper functions, this method populates a dictionary stored attribute of Mars,
        statistics, with telemetry data.
        :param integTime:
        :return:
        """

        serialData = self._arduino.serial_readline()
        rawArray = re.split(",", serialData)

        #Assign integ time for use of helper functions
        copy = self._integTime
        currenttime = time.time()
        self._integTime = currenttime - copy

        #print(rawArray)
        rpm = rawArray[0]
        self._statistics['RPM'] = rpm
        sysV = rawArray[1]
        self._statistics['System Voltage'] = sysV
        sysI = rawArray[2]
        sysI = sysI[0:len(sysI)-4]
        self._statistics['System Current'] = sysI

        speed = self.estimatedSpeed() #speed in m/s
        self._statistics['Speed'] = speed
        power = self.estimatedPower(sysV, sysI) #power in Watts
        self._statistics['Power'] = power


        intDistance, totDistanceTraveled = self.distanceTraveled() #in Meters
        self._statistics['Interval Distance'] = intDistance
        self._statistics['Total Distance'] = totDistanceTraveled

        displacement, totalDisplacement = self.displacement() #in Meters
        self._statistics['Interval Displacement'] = displacement
        self._statistics['Total Displacement'] = totalDisplacement

        batteryRemaining = self.batteryRemaining(power)
        self._statistics['Battery Remaining'] = batteryRemaining

        self.safteyCheck()

    def safteyCheck(self):
        """
        Function to check the statistics pulled for any alarming signs (IE low battery)
        :return:
        """

        #If recall is enabled
        if (self._config.autonomous_action.enableRecall):

            #If the battery remaining is less than or equal to the configuration recall percent
            #print('Battery remaining:' + str(self._statistics['Battery Remaining']))
            #print('Recall percent:' + str(self._config.autonomous_action.recallPercent))
            if (float(self._statistics['Battery Remaining']) <= float(self._config.autonomous_action.recallPercent)):
                print("Recalling")
                self.recall()


    def recall(self):
        """
        Recall Mars when the battery is below the configuration threshhold
        :return:
        """
        midpoint = self._config.constants.trackLength / 2

        #If Mars is at or past the midpoint
        if (self._statistics['Total Distance'] >= midpoint):
            print("Past halfway, moving forward")
            #Move forward at full speed
            self._arduino.write('M1104')
        else:
            print("Not halfway, moving back")
            #Otherwise go back at full speed
            self._arduino.write('M1004')


    def estimatedSpeed(self):
        """
        This function guesses how fast Mars is going based on the lastest RPM
        data from the DAQ.

        It does not take into account any other factors or forces, as a result
        this is an ESTIMATED SPEED, not a real speed

        this conversion is will only work for the current generation of MARS and
        is a function of this equation
            speed in mph ~= rpm/221
            speed in m/s ~= (rpm/221)*0.44704

        :param rpm:
        :return:
        """

        rpm = float(self._statistics['RPM']) #rpm must be a float
        estMps = (rpm/221.0)*0.44704 #estimated SPEED in M/S

        returnEstMps = round(estMps, 1)
        self._statistics['Speed'] = returnEstMps
        return self._statistics['Speed']

    def estimatedPower(self, sysVoltage, sysCurrent):
        """
        estimates the current power usage of mars based off of voltage and current data.
            P = V * I
        :param sysVoltage:
        :param sysCurrent:
        :return:
        """
        sysVoltage = float(self._statistics['System Voltage'])
        sysCurrent = float(self._statistics['System Current'])
        estPower = sysVoltage * sysCurrent

        powerReturned = round(estPower, 2)
        return powerReturned

    def distanceTraveled(self, time=None):
        """
        returns the estimated distance traveled by mars. If the user feed this function a time parameter, then this will
        calculate the new distance based on the current speed and time given. Otherwise it will return the last
        calculated distance traveled by Mars.
        :param speed:
        :param time:
        :return:
        """
        if time == None:
            time = self._integTime

        intervalDistance = abs(self._statistics['Speed']) * time
        travAdded = self._statistics['Total Distance'] + intervalDistance
        self._statistics['Total Distance'] = travAdded
        #totalDistance = self._statistics['distanceTraveled']

        intervalDistanceRounded = round(intervalDistance,1)
        totalDistanceRounded = round(self._statistics['Total Distance'], 1)

        return intervalDistanceRounded,totalDistanceRounded

    def displacement(self, time=None):
        """

        :param speed:
        :param time:
        :return:
        """
        if time == None:
            time = self._integTime

        intervalDisplacement = self._statistics['Speed'] * time
        self._statistics['Interval Displacement'] = self._statistics['Interval Displacement'] + intervalDisplacement
            # '--> updating the object attribute
        totalDisplacement = self._statistics['Total Displacement'] + intervalDisplacement

        intervalDisplacement = abs(round(intervalDisplacement,1)) #Rounding for readability
        totalDisplacement = abs(round(totalDisplacement, 1))

        return intervalDisplacement,totalDisplacement

    def batteryRemaining(self,power=None, time = None):
        """
        battery_remaining(power *optional*, time *optional*)::
        if the user inputs power or time data, then this function will calculate how much energy remains in the
        batteries. otherwise ths will return the last calculated battery status
        :param power:
        :param time:
        :return:
        """

        if time == None:
            time = self._integTime
        ########^^^^^^^^FIX THIS ONCE DEBUGGING IS COMPLETE^^^^^^^^###########

        if power != None:

            #print(power)
            #print(time)
            joulesUsed  = float(power) * time
            #print(joulesUsed)
            whrUsed = joulesUsed/3600.0 #converting Joules to Watt*hours
            #print(whrUsed)

            self._currentBattery = float(self._currentBattery) - whrUsed
            #subtracting energy used from battery total

        battPercent = float(self._currentBattery) / float(self._config.constants.totalBattery) * 100.0
        battPercentReturned = round(battPercent, 1)

        return battPercentReturned

