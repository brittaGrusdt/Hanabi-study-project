import tensorflow as tf

import random
import numpy as np

from hanabi_learning_environment import rl_env

class PolicyGradientNetwork(tf.keras.Model):
    """Policy gradien network model"""
    def __init__(self, n_action):
        super(PolicyGradientNetwork, self).__init__()
        self.hidden1 = tf.keras.layers.Dense(128, activation='relu')
        self.hidden2 = tf.keras.layers.Dense(128, activation='relu')
        self.output_layer = tf.keras.layers.Dense(n_action, activation = 'softmax')
        
    def call(self, inputs):
        x = self.hidden1(inputs)
        x = self.hidden2(x)
        x = self.output_layer(x)
        return x

GAMMA = 0.8
LEARNING_RATE = 0.01
EPISODES_TO_TRAIN = 5

class PgReinforceAgent():
    """Agent using Poicy Gradient using Reinforcement Algorithm"""
    def __init__(self, config):
        """Initialize the agent."""
        self.config = config
        self.state_size = config['state_size']
        self.action_size = config['action_size']
        
        self.env = config['env']
        
        self.model = PolicyGradientNetwork(self.action_size)
        self.model.build((1,self.state_size))
        self.optimizer = tf.keras.optimizers.Adam(learning_rate = LEARNING_RATE)
        self.cross_entropy = tf.keras.losses.SparseCategoricalCrossentropy(from_logits=True)
        
        self.grad_buffer = self.model.trainable_variables
        for idx, grad in enumerate(self.grad_buffer):
            self.grad_buffer[idx] = grad * 0
            
        self.episode_mem = []
        self.update_mem = False
        
    @staticmethod
    def calc_vals(rewards):
        """returns the list of G_t i.e. discounted rewards at time t"""
        res = []
        sum_r = 0.0
        for r in reversed(rewards):
            sum_r *= GAMMA
            sum_r += r
            res.append(sum_r)
        return list(reversed(res))
    def get_prob_action(self, legal_moves, action_dist):
        actions = [x if i in legal_moves else 0 for i, x in enumerate(action_dist)]
        if sum(actions)!=0:
            actions = [x/sum(actions) for x in actions]
            action = np.random.choice(list(range(self.action_size)), p=actions)
        else:
            action = None
            logging.error("No legal move.")
        return action
        
        
    def act(self, observation):
        if observation['current_player_offset'] != 0:
            return None
        
        state = np.array(observation['vectorized']).reshape(1,self.state_size)
        
        with tf.GradientTape() as tape:
            # forward pass
            logits = self.model(state)
            action_dist = logits.numpy()
            
            # list of legal moves
            legal_moves = observation['legal_moves_as_int']
            action = self.get_prob_action(legal_moves, action_dist[0])
            if action is not None:
                loss = self.cross_entropy([action], logits)
        if action is not None:
            self.grads = tape.gradient(loss, self.model.trainable_variables)
        return action  
    
    def store_memory(self, reward):
        self.update_mem = True
        self.episode_mem.append([self.grads, reward])
    
    def update_memory(self):
        self.update_mem = False
        self.episode_mem = np.array(self.episode_mem)
#         print(self.episode_mem.shape)
        self.episode_mem[:,1] = PgReinforceAgent.calc_vals(self.episode_mem[:,1])
       
    def update_grad_buffer(self):
        for grads, reward in self.episode_mem:
            for idx, grad in enumerate(grads):
                self.grad_buffer[idx] += grad * reward
        
    def apply_gradients(self):
        self.optimizer.apply_gradients(zip(self.grad_buffer, self.model.trainable_variables))
        
        for idx, grad in enumerate(self.grad_buffer):
            self.grad_buffer[idx] = grad * 0
            

AGENT_CLASSES = {"PgReinforceAgent": PgReinforceAgent}

class Runner(object):
    """Runner class"""
    
    def __init__(self, flags):
        """Initialize runner"""
        self.flags = flags
        self.environment = rl_env.make('Hanabi-Very-Small', num_players=self.flags['players'])
        self.agent_config = {"players": flags['players'],
                             'state_size':self.environment.vectorized_observation_shape()[0],
                             'action_size': self.environment.num_moves(),
                             'env': self.environment}
        self.agent_class = AGENT_CLASSES[flags['agent_class']]
        
    def run(self):
        """Run episodes"""
        rewards = []
        agents = [self.agent_class(self.agent_config) 
                  for _ in range(self.flags['players'])]
        for episode in range(self.flags['num_episodes']):
            observations = self.environment.reset()
            done = False
            episode_reward = 0
            while not done:
                for agent_id, agent in enumerate(agents):
                    observation = observations['player_observations'][agent_id]
                    action = agent.act(observation)
                    # convert action from uid to dict
                    if action is not None:
                        action = self.environment.game.get_move(action).to_dict()
                    if observation['current_player'] == agent_id:
                        assert action is not None
                        current_player_action = action
                        break
                    else:
                        assert action is None
                # Make an envirnment step:
#                 print('Agent: {} action: {}'.format(observation['current_player'],
#                                                    current_player_action))
                observations, reward, done, _ = self.environment.step(current_player_action)
                episode_reward+=reward
                
                # store episode memory for the agent
                agent.store_memory(reward)
                
            rewards.append(episode_reward)
            
            # for each agent update gradients
            for agent in agents:
                if agent.update_mem:
                    agent.update_memory() # update reward with discounted reward
                
                # update grad by adding multiple of policy gradient and discounted return for each step
                agent.update_grad_buffer()

                # clear episode memory:
                agent.episode_mem = []
            
            # apply gradient descent using ADAM after every N episodes for each agent:
            if episode % EPISODES_TO_TRAIN == 0:
                for agent in agents:
                    agent.apply_gradients()
            if episode % 50 == 0:
                logging.info("Episode: {}, Max reward:{}, Avg Reward:{}"
                .format(episode, max(rewards[-50:]), sum(rewards[-50:])/50))
#                 print("Episode: {}, Max reward:{}, Avg Reward:{}".format(episode, max(rewards[-50:]), sum(rewards[-50:])/50))
#                 print('Max Reward: {}'.format(max(rewards)))
#                 print("Average for last 10 episodes: {}".format(sum(rewards[-10:])/10))
                print(".", end="")
        print()
        return rewards


def main(num_players=2, num_episodes = 1):
    flags = {'players':num_players, 'num_episodes': num_episodes, 'agent_class':'PgReinforceAgent'}
    
    runner = Runner(flags)
    rewards = runner.run()
    return rewards


if __name__ == "__main__":
    num_players = 2
    num_episodes = 10000

    # logging setup
    import logging
    from datetime import datetime
    now = datetime.now()
    now_str = now.strftime('%d-%m-%Y-%H_%M_%S')
    logname = f"player-{num_players}eps-{num_episodes}hanabi"
    logging.basicConfig(filename = "./" + logname + now_str+ '.log',
                        filemode='a',
                        format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                        datefmt='%d-%m-%Y-%H:%M:%S',
                        level=logging.DEBUG)
    

    rewards = main(num_players=num_players, num_episodes = num_episodes)

    avg_reward = [sum(rewards[i:i+50])/50 for i in range(len(rewards)-50)]


    import matplotlib.pyplot as plt
    plt.figure(figsize=(15, 5))
    plt.plot(list(range(len(avg_reward))), avg_reward)
    plt.xlabel("Episodes")
    plt.ylabel("Avg. Rewards")
    plt.savefig(logname)
    
    logging.info("Completed.")
    
