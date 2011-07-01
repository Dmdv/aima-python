from abc import ABCMeta

__author__ = 'Ivan Mushketik'
__docformat__ = 'restructuredtext en'

class AgentProgram(metaclass=ABCMeta):
    def execute(self, percept):
        raise NotImplementedError()

class Agent:
    def __init__(self, program=None):
        self.program = program
        self.alive = True

    def execute(self, percept):
        if self.program:
            return self.program.execute(percept)
        return NoOpAction()


class EnvironmentView(metaclass=ABCMeta):
    def notify(self, msg):
        raise NotImplementedError()

    def agent_added(self, agent, resulting_state):
        raise NotImplementedError()

    def agent_acted(self, agent, action, resulting_state):
        raise NotImplementedError()


class Environment(metaclass=ABCMeta):

    def __init__(self):
        self.environment_objects = set()
        self.agents = set()
        self.views = set()
        self.performance_measures = {}

    def get_current_state(self):
        raise NotImplementedError()

    def execute_action(self, agent, action):
        raise NotImplementedError()

    def get_percept_seen_by(self, agent):
        raise NotImplementedError()

    def create_exogenous_change(self):
        pass

    def get_agents(self):
        return list(self.agents)

    def add_agent(self, agent):
        if not agent is self.agents:
            self.agents.add(agent)
            self._notify_agent_added(agent)
        self.environment_objects.add(agent)

    def remove_agent(self, agent):
        self.agents.discard(agent)
        self.environment_objects.discard(agent)

    def get_environment_objects(self):
        return list(self.environment_objects)

    def add_environment_object(self, environment_object):
        self.environment_objects.add(environment_object)

    def remove_environment_object(self, environment_object):
        self.environment_objects.discard(environment_object)

    def step_once(self):
        for agent in self.agents:
            if agent.alive:
                action = agent.execute(self.get_percept_seen_by(agent))
                environment_state = self.execute_action(agent, action)
                self._notify_agent_acted(agent, action, environment_state)

        self.create_exogenous_change()

    def step(self, n):
        for i in range(n):
            self.step_once()

    def step_until_done(self):
        while not self.is_done():
            self.step_once()

    def is_done(self):
        for agent in self.agents:
            if agent.alive:
                return False
        return True

    def get_performance_measure_for(self, agent):
        return self.performance_measures.setdefault(agent, 0)

    def _update_performance_measure(self, agent, add_to):
        self.performance_measures[agent] += add_to

    def add_environment_view(self, environment_view):
        self.views.add(environment_view)

    def remove_environment_view(self, environment_view):
        self.views.discard(environment_view)

    def notify_views(self, msg):
        for view in self.views:
            view.notify(msg)

    def _notify_agent_added(self, agent):
        for view in self.views:
            view.agent_added(agent, self.get_current_state())

    def _notify_agent_acted(self, agent, action, state):
        for view in self.views:
            view.agent_acted(agent, action, state)


class Action(metaclass=ABCMeta):
    def __init__(self, name):
        self.name = name

    def is_noop(self):
        raise NotImplementedError()


class CutOffIndicatorAction(Action):
    def __init__(self):
        super().__init__("CufOff")

    def is_noop(self):
        return True

    def __eq__(self, other):
        return isinstance(other, CutOffIndicatorAction)


class NoOpAction(Action):
    def __init__(self):
        super().__init__("NoOp")

    def is_noop(self):
        return True

    def __eq__(self, other):
        return isinstance(other, NoOpAction)

class DynamicAttributes:
    def __init__(self):
        self.table = {}

    def set_attribute(self, key, value):
        self.table[key] = value

    def get_attribute(self, key):
        return self.table[key]

class Percept(metaclass=ABCMeta):
    pass

class DynamicPercept(DynamicAttributes, Percept):
    def __init__(self):
        super().__init__()

    def set_percept(self, key, value):
        self.set_attribute(key, value)

    def set_percepts(self, keys, values):
        assert len(keys) == len(values)

        for i in range(len(keys)):
            self.set_attribute(keys[i], values[i])


class PerceptToStateFunction(metaclass=ABCMeta):
    def get_state(self, percept):
        raise NotImplementedError()