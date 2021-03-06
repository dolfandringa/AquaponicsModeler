# -*- coding: utf-8 -*-
"""
The :mod:`AquaponicsModeler.model` module contains all components to be used in
models.

All model components are classes that should inherit from
:class:`BaseModelClass`. So far there are two groups of component types:
containers and pumps.

:class:`Containers <Container>` are compents that contain water and have water
flowing in or out. They need to have another component before them in the
model, so water can flow from one container to the other.

As :class:`Containers <Container>` always need a source of water, the first
component in the model is a :class:`Pump`. There are several types of pumps,
but they all assume an infinite water source that they can pump from, and they
pump into a :class:`Container`.

"""
import logging
import collections
import copy
from PyElectronics.timers import AStable555
log = logging.getLogger("aquaponics.model")


class _PARAM_TYPES:

    """Constant holding the different parameter types."""

    MODEL = 'Model Component Parameter'
    INTEGER = 'Integer Parameter'
    FLOAT = 'Float Parameter'
    TEXT = 'Text Parameter'


class BaseModelClass(object):

    """
    A base class for the model that other objects inherit from.

    The BaseModelClass doesn't implement much except for general methods to
    get the parameters for a component and to manage the state while stepping
    through the model. The state is the main variable manipulated by the model.
    For :class:`Pump` it contains the on/off state, while for
    :class:`Containers <Container>` it contains the water volume of the
    container.

    """

    _PARAMS = collections.OrderedDict()

    def __init__(self):
        self.state = None

    def __str__(self):
        return self.__class__.__name__

    def get_state(self):
        """
        Get the current contents of this container.

        Returns:
            float: current state value

        """
        return self.state

    @classmethod
    def getParameters(cls):
        """
        Return the model parameters.

        Returns:
            collections.OrderedDict: The parameters for this class.
        """
        log.debug('Getting parameters for class %s: %s' % (cls, cls._PARAMS))
        return cls._PARAMS

    def step(self):
        """Step into the next iteration of the model."""
        raise NotImplementedError("Please implement a step instance method")

class SimpleContainer(BaseModelClass):

    """
    A container in the aquaponics loop.

    Each container is a container/tank/basin/growbed/etc containing a volume
    of water, with possibly water flowing out into the next component and
    flowing into it from the previous container in the loop.
    The inflow speed of each container is determined by the outflow speed of
    the previous container. The outflow of each container only starts when in
    the treshold has been reached, and only if the contents of the
    container > 0 liters.

    """

    _PARAMS = {
        'previous': (_PARAM_TYPES.MODEL, 'previous'),
        'outflow': (_PARAM_TYPES.FLOAT, 'outflow (l/min)'),
        'start_content': (_PARAM_TYPES.INTEGER, 'start content (l)')
    }

    def __init__(self, previous, outflow, start_content=0):
        """
        Args:
            previous (Container): The previous Container in the chain.
            outflow (float): The outflow speed of this container.
            threshold (int): The threshold contents after which the container
                outflow speed starts.
            start_content (int): The starting contents of the container.

        """
        self.previous = previous
        self.outflow = outflow
        self.state = self.start_content = start_content

    def get_current_outflow_speed(self):
        """
        Determine the current flow speed of water from this container.

        Returns:
            float: The current outflow speed.

        """
        return self.outflow

    def get_current_inflow_speed(self):
        """
        Determine the current speed of water flowing into this container.

        This is determined by the outflow speed of the previous container.


        Returns:
            float: The current inflow speed.

        """
        return self.previous.get_current_outflow_speed()

    def step(self, time=10):
        """
        Go through the next step of the simulation of this container.

        Args:
            time (int): The length of the next step in seconds.

        """
        inflow = self.get_current_inflow_speed()
        outflow = self.get_current_outflow_speed()
        self.state += time / 60 * inflow - time / 60 * outflow

class Container(SimpleContainer):
    _PARAMS = copy.deepcopy(SimpleContainer._PARAMS)
    _PARAMS['threshold']= (_PARAM_TYPES.INTEGER,  'dump threshold (l)')

    def __init__(self, previous, outflow, threshold, start_content=0):
        """
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

        Returns:
            float: The current outflow speed.

        """
        if self.state >= self.threshold:
            return self.outflow
        else:
            return 0

class FloodDrainContainer(Container):

    """
    This :class:`Container` will drain fully when the threshold has been
    reached.

    In other respects it works like other :class:`Containers <Container>` but
    for the way it drains. A container with a U-siphon or bell siphon at the
    end will only start draining when the waterlevel has reached a maximum.
    When that happens, suction makes sure that all water is drained from the
    container at the speed specified in outflow.

    """

    def __init__(self, *args, **kwargs):
        super(FloodDrainContainer, self).__init__(*args, **kwargs)
        self.flooding = False

    def get_current_outflow_speed(self):
        """
        Return the current outlflow speed.

        Outflow starts when self.threshold has been reached and will continue
        at self.outflow speed until the container is empty.

        Returns:
            float: The outflow speed of this :class:`Container`

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
    constant outflow speed. It doesn't have contents (unlike containers for
    instance). The state attribute contains the on (1) or off (0) state
    of the pump, which is also what is plotted in the resulting graphs.

    """

    _PARAMS = {
        'outflow': (_PARAM_TYPES.FLOAT, 'outflow (l/min)'),
    }

    def __init__(self, outflow):
        """
        Args:
            outflow (float): The speed at which the pump pumps.

        """
        self.outflow = outflow
        self.state = 1

    def get_current_outflow_speed(self):
        """
        Return the pump speed of this pump.

        Returns:
            float: The outflow speed of this pump in L/min.

        """
        return self.outflow

    def step(self, time=10):
        """
        Go through the next step of the pump state and return that state.

        Args:
            time (int): The time in seconds for which the pump state should be
                returned.

        Returns:
            int: The state of the pump. 1=on 0=off.

        """
        return self.state

class WaterSource(BaseModelClass):

    """
    A general Water Source object.

    Water flows at a static speed from a source (spring or other source).
    It doesn't have contents (unlike containers for instance).

    """

    _PARAMS = {
        'outflow': (_PARAM_TYPES.FLOAT, 'outflow (l/min)'),
    }

    def __init__(self, outflow):
        """
        Args:
            outflow (float): The speed at which the watersource flows.

        """
        self.outflow = outflow
        self.state = None

    def get_current_outflow_speed(self):
        """
        Return the pump speed of this pump.

        Returns:
            float: The outflow speed of this source in L/min.

        """
        return self.outflow

    def step(self, time=10):
        """
        Go through the next step of the source.

        Args:
            time (int): The time in seconds for which the pump state should be
                returned.

        """
        return


class TimedPump(Pump):

    """
    A pump like the Pump object.

    This pump has timing parameters which periodically switch it on and off.
    This way the outflow speed of the pump is controlled. If it is on, it
    equals the outflow speed parameter, else it is 0.

    """

    _PARAMS = copy.deepcopy(Pump._PARAMS)
    _PARAMS['ontime'] = (_PARAM_TYPES.FLOAT, 'on time (min)')
    _PARAMS['offtime'] = (_PARAM_TYPES.FLOAT, 'off time (min)')

    def __init__(self, ontime, offtime, outflow):
        """
        Args:
            ontime (float): The time in minutes the pump spends pumping.
            offtime (float): The time in minutes the pump is off.
            outflow (float): The speed at which the pump pumps in L/min.

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

        Returns:
            float: The outflow speed in L/min

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
    A pump like the :class:`TimedPump` object.

    This pump gets resistor and capacitor values as input parameters instead of
    the actual ontime and offtime. This object assumes a 555 timer circuit in
    a-stable mode is used to switch the pump on and off. A relay is used for
    the actual switching which is on when the timer is high.
    The resistor values of the timer determine the on and off time.

    """

    _PARAMS = copy.deepcopy(Pump._PARAMS)
    _PARAMS['r1'] = (_PARAM_TYPES.FLOAT, 'Resistor 1 value (KOhm)')
    _PARAMS['r2'] = (_PARAM_TYPES.FLOAT, 'Resistor 2 value (KOhm)')
    _PARAMS['c'] = (_PARAM_TYPES.INTEGER, 'The capacitor value (uF)')

    def __init__(self, r1, r2, c, outflow):
        """

        Args:
            r1 (int): The value in Ohm of resistor 1 for the 555 timer.
            r2 (int): The value in Ohm of resistor 2 for the 555 timer.
            c (int): The value of the capacitor in uF for the 555 timer
            outflow (float): The speed at which the pump pumps in L/min.

        """

        self.c = c
        self.r1 = r1
        self.r2 = r2
        ontime = AStable555.timeHigh(r1, r2, c)
        offtime = AStable555.timeLow(r2, c)
        log.debug("Got ontime %i" % ontime)
        log.debug("Got offtime %i" % offtime)
        self.ontime = ontime
        self.offtime = offtime
        self.outflow = outflow
        self.time_since_switch = 0
        self.state = 1


class InvTimed555Pump(TimedPump):

    """
    An inverted version of the :class:`Timed555Pump` object.

    It works very similar, but the relay is inverted. The normally-off side
    of the relay is used to switch the pump off when the timer is high.
    """

    _PARAMS = copy.deepcopy(Pump._PARAMS)
    _PARAMS['r1'] = (_PARAM_TYPES.FLOAT, 'Resistor 1 value (KOhm)')
    _PARAMS['r2'] = (_PARAM_TYPES.FLOAT, 'Resistor 2 value (KOhm)')
    _PARAMS['c'] = (_PARAM_TYPES.INTEGER, 'The capacitor value (uF)')

    def __init__(self, r1, r2, c, outflow):
        """

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

    Returns:
        list: Return a list of all component classes.

    """
    return [Container,  FloodDrainContainer,  Pump,  TimedPump,  Timed555Pump,
            InvTimed555Pump, WaterSource, SimpleContainer]

__all__ = ['BaseModelClass', 'Container', 'FloodDrainContainer', 'Pump',
           'TimedPump', 'Timed555Pump', 'InvTimed555Pump', 'WaterSource',
           'SimpleContainer', 'get_components', '_PARAM_TYPES']
