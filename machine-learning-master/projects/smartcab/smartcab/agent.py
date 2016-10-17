import random
from environment import Agent, Environment
from planner import RoutePlanner
from simulator import Simulator

class LearningAgent(Agent):
    """An agent that learns to drive in the smartcab world."""

    def __init__(self, env):
        super(LearningAgent, self).__init__(env)  # sets self.env = env, state = None, next_waypoint = None, and a default color
        self.color = 'red'  # override color
        self.planner = RoutePlanner(self.env, self)  # simple route planner to get next_waypoint
        self.valid_directions = [None, 'forward', 'left', 'right']
        self.q_table = {}
        self.alpha = 0.5
        self.gamma = 0.6
        self.previous_state = None
        self.goal_reached_counter = 0
        self.trials = 100
        self.trial_counter = 0
        # TODO: Initialize any additional variables here

    def reset(self, destination=None):
        self.planner.route_to(destination)
        self.trial_counter += 1
        # TODO: Prepare for a new trip; reset any variables here, if required

    def keywithmaxval(self, d):
        #create a list of the dict's keys and values; 
        #return the key with the max value 

        v=list(d.values())
        k=list(d.keys())
        return k[v.index(max(v))]

    def update(self, t):
        # Gather inputs
        self.next_waypoint = self.planner.next_waypoint()  # from route planner, also displayed by simulator
        inputs = self.env.sense(self)
        deadline = self.env.get_deadline(self)
        epsilon = 0.001/(1+t)
        

        # TODO: Update state
        self.state = [('light',inputs['light']),('oncoming',inputs['oncoming']),('right',inputs['right']),('left',inputs['left']),('next_waypoint',self.next_waypoint)]
        
        # TODO: Select action according to your policy
        def keywithmaxval(d):
        #create a list of the dict's keys and values; 
        #return the key with the max value 
            v=list(d.values())
            k=list(d.keys())
            return k[v.index(max(v))]

        #Create keys for possible actions
        state_action_keys = [(str(self.state),direction) for direction in self.valid_directions]

        #Create list of q_table values of possible actions according to current state
        state_action_values = [self.q_table.get((state_action_key),0) for state_action_key in state_action_keys]

        #Create Dictionary witht he above keys and values to extract the action
        dictionary_next_actions = {key: value for key, value in zip(state_action_keys,state_action_values)}
        
        #Take action
        if random.random() < epsilon:
            action = random.choice(self.valid_directions)
        else:
            action = keywithmaxval(dictionary_next_actions)[1]
        
        
        # Execute action and get reward
        reward = self.env.act(self, action)

        # TODO: Learn policy based on state, action, reward
        if self.previous_state != None:
            self.q_table[(str(self.previous_state),self.previous_action)] = (1 - self.alpha) * (self.q_table.get((str(self.previous_state),self.previous_action),0)) + self.alpha * (reward + (self.gamma * (max([self.q_table.get((str(self.state),direction),0) for direction in self.valid_directions]))))                


        self.previous_state = self.state
        self.previous_action = action

        print "LearningAgent.update(): deadline = {}, inputs = {}, action = {}, reward = {}, next_waypoint = {}".format(deadline, inputs, action, reward, self.next_waypoint) # [debug]

        if reward >= 9:
            self.goal_reached_counter += 1

        #Store results in external file out.txt
        if (self.trial_counter == self.trials and deadline <= 0) or (self.trial_counter == self.trials and reward >= 9):
            with open('out.txt','a') as file:
                file.write(str(self.goal_reached_counter)+', ') 
            print 'Achieved destination '+str(self.goal_reached_counter)+' times'



def run():
    """Run the agent for a finite number of trials."""

    # Set up environment and agent
    e = Environment()  # create environment (also adds some dummy traffic)
    a = e.create_agent(LearningAgent)  # create agent
    e.set_primary_agent(a, enforce_deadline=True)  # specify agent to track
    # NOTE: You can set enforce_deadline=False while debugging to allow longer trials

    # Now simulate it
    sim = Simulator(e, update_delay=0, display=False)  # create simulator (uses pygame when display=True, if available)
    # NOTE: To speed up simulation, reduce update_delay and/or set display=False

    sim.run(n_trials=a.trials)  # run for a specified number of trials
    # NOTE: To quit midway, press Esc or close pygame window, or hit Ctrl+C on the command-line

    

if __name__ == '__main__':
    run()
