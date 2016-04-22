# -*- coding: utf-8 -*-
"""
This model contains all components to be used in models.

They should inherit from <BaseModelClass>.

"""
import logging
import copy
import sys
sys.path.append("/home/dolf/Documents/Projects/Software ontwikkeling/")
from PyElectronics.timers import AStable555
log = logging.getLogger("aquaponics.model")


class _PARAM_TYPES:

    """Constant holding the different parameter types."""

    MODEL = 'Model Component Parameter'
    INTEGER = 'Integer Parameter'
    FLOAT = 'Float Parameter'
    TEXT = 'Text Parameter'


class BaseModelClass(object):

    """A base class for the model that other objects inherit from."""

    _PARAMS = {}

    def __init__(self):
        """Init the model instance."""
        self.state = None

    def __str__(self):
        return self.__class__.__name__

    def get_state(self):
        """
        Get the current contents of this container.

        Args:
            returns: current state value

        """
        return self.state

    @classmethod
    def getParameters(cls):
        """Return the model parameters."""
        log.debug('Getting parameters for class %s: %s' % (cls, cls._PARAMS))
        return cls._PARAMS

    def step(self):
        """Step into the next iteration of the model."""
        raise NotImplementedError("Please implement a step instance method")


class Container(BaseModelClass):

    """
    A container in the aquaponics loop.

    Each container is connected to a
    previous container. The inflow speed of each container is determined by the
    outflow speed of the previous container. The outflow of each container only
    starts when in the treshold has been reached, and only if the contents of
    the container > 0 liters.

    """

    _PARAMS = {
        'previous': (_PARAM_TYPES.MODEL, 'previous'),
        'outflow': (_PARAM_TYPES.FLOAT, 'outflow (l/min)'),
        'threshold': (_PARAM_TYPES.INTEGER,  'dump threshold (l)'),
        'start_content': (_PARAM_TYPES.INTEGER, 'start content (l)')
    }

    def __init__(self, previous, outflow, threshold, start_content=0):
        """
        Init this container.

        Args:
            previous (Container): The previous Container in the chain.
            outflow (float): The outflow speed of this container.
            threshold (int): The threshold contents after which the container
                outflow speed starts.
            start_content (int): The starting contents of the container.

        """
        self.previous = previous
        self.outflow = outflow
        self.threshold = threshold
        self.state = self.start_content = start_content

    def get_current_outflow_speed(self):
        """
        Determine the current flow speed of water from this container.

        Args:
            returns (int): The current outflow speed.

        """
        if self.state >= self.threshold:
            return self.outflow
        else:
            return 0

    def get_current_inflow_speed(self):
        """
        Determine the current speed of water flowing into this container.

        This is determined by the outflow speed of the previous container.

        Args:
            returns (int): The current inflow speed.

        """
        return self.previous.get_current_outflow_speed()

    def step(self, time=10):
        """
        Go through the next step of the simulation of this container.

        Args:
            time(int): The length of the next step in seconds.

        """
        inflow = self.get_current_inflow_speed()
        outflow = self.get_current_outflow_speed()
        self.state += time / 60 * inflow - time / 60 * outflow


class FloodDrainContainer(Container):

    """
    This container will drain fully when the threshold has been reached.

    This works for instance with a U-siphon or bell siphon design.

    """

    def __init__(self, *args, **kwargs):
        super(FloodDrainContainer, self).__init__(*args, **kwargs)
        self.flooding = False

    def get_current_outflow_speed(self):
        """
        Return the current outlflow speed.

        Outflow starts when self.threshold has been reached and will continue
        at self.outflow speed until the container is empty.

        """
        if (self.flooding is True and self.state > 0)\
                or self.state >= self.threshold:
            self.flooding = True
            return self.outflow
        else:
            self.flooding = False
            return 0


class Pump(BaseModelClass):

    """
    A general Pump object.

    It pumps water into the system (from an unlimited source) and has a
    constant outflow speed. It doesn't have contents (lunike containers for
    instance). The self.state attribute contains the on (1) or off (0) state
    of the pump.

    """

    _PARAMS = {
        'outflow': (_PARAM_TYPES.FLOAT, 'outflow (l/min)'),
    }

    def __init__(self, outflow):
        """
        Init the Pump.

        Args:
            outflow (float): The speed at which the pump pumps.

        """
        self.outflow = outflow
        self.state = 1

    def get_current_outflow_speed(self):
        """Return the pump speed of this pump."""
        return self.outflow

    def step(self, time=10):
        """
        Go through the next step of the pump state and return that state.

        Args:
            time (int): The time in seconds for which the pump state should be
                returned.

        """
        return


class TimedPump(Pump):

    """
    A pump like the Pump object.

    This pump has timing parameters which periodically switch it on and off.

    """

    _PARAMS = copy.deepcopy(Pump._PARAMS)
    _PARAMS['ontime'] = (_PARAM_TYPES.FLOAT, 'on time (min)')
    _PARAMS['offtime'] = (_PARAM_TYPES.FLOAT, 'off time (min)')

    def __init__(self, ontime, offtime, outflow):
        """
        Init the TimedPump.

        Args:
            ontime (int): The time period in minutes the pump spends pumping.
            offtime (int): The time period in minutes the pump is off.
            outflow (foat): The speed at which the pump pumps in L/min.

        """
        self.ontime = ontime * 60
        self.offtime = offtime * 60
        self.outflow = outflow
        self.time_since_switch = 0
        self.state = 1

    def get_current_outflow_speed(self):
        """
        Return the current outflow (pump) speed.

        It is determined by a timed switch that toggles the pump on and off.

        Args:
            returns (float): The outflow speed in L/min

        """
        log.debug("state %i, time since switch %i, ontime %i, offtime %i" %
                  (self.state, self.time_since_switch, self.ontime,
                   self.offtime))
        if self.state == 1 and self.time_since_switch < self.ontime:
            outflow = self.outflow
        elif self.state == 0 and self.time_since_switch >= self.offtime:
            outflow = self.outflow
        elif self.state == 0 and self.time_since_switch < self.offtime:
            outflow = 0
        elif self.state == 1 and self.time_since_switch >= self.ontime:
            outflow = 0
        logging.debug("Returning outflow %0.2f" % outflow)
        return outflow

    def step(self, time=10):
        """
        Go through the next step of the pump state and return that state.

        Args:
            time (int): The time in seconds for which the pump state should be
                returned.

        """
        if (self.state == 0 and self.time_since_switch >= self.offtime) or\
                (self.state == 1 and self.time_since_switch >= self.ontime):
            log.debug("Switching pump state to %i " % (self.state ^ 1))
            self.state = self.state ^ 1
            self.time_since_switch = 0
        else:
            log.debug("Keeping pump state at %i " % self.state)
            self.time_since_switch += time
        log.debug("Pump at state %i for %i sec" %
                  (self.state, self.time_since_switch))


class Timed555Pump(TimedPump):

    """
    A pump like the L{model.TimedPump} object.

    This pump gets resistor and capacitor values as input parameters instead of
    the actual ontime and offtime. This object assumes a 555 timer circtui in
    a-stable mode is used to switch the pump on and off.
    The resistor values of the timer determine the on and off time.

    """

    _PARAMS = copy.deepcopy(Pump._PARAMS)
    _PARAMS['r1'] = (_PARAM_TYPES.FLOAT, 'Resistor 1 value (Ohm)')
    _PARAMS['r2'] = (_PARAM_TYPES.FLOAT, 'Resistor 2 value (Ohm)')
    _PARAMS['c'] = (_PARAM_TYPES.INTEGER, 'The capacitor value (uF)')

    def __init__(self, r1, r2, c, outflow):
        """
        Init the TimedPump.

        Args:

            r1 (int): The value in Ohm of resistor 1 for the 555 timer.
            r2 (int): The value in Ohm of resistor 2 for the 555 timer.
            c (int): The value of the capacitor in uF for the 555 timer
            outflow (float): The speed at which the pump pumps in L/min.

        """

        self.c = c
        self.r1 = r1
        self.r2 = r2
        ontime = AStable555.timeLow(r2, c)
        offtime = AStable555.timeHigh(r1, r2, c)
        log.debug("Got ontime %i" % ontime)
        log.debug("Got offtime %i" % offtime)
        self.ontime = ontime
        self.offtime = offtime
        self.outflow = outflow
        self.time_since_switch = 0
        self.state = 1


def get_components():
    """
    Get all available component types.

    Args:
        returns (list): Return a list of all component classes.

    """
    return [Container,  FloodDrainContainer,  Pump,  TimedPump,  Timed555Pump]

__all__ = [BaseModelClass,  Container,  FloodDrainContainer,  Pump,  TimedPump,
           Timed555Pump, get_components,  _PARAM_TYPES]
