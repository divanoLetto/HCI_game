import gym
import numpy as np
from deepcrawl.environment.game import Game
from BoatGame import BoatGame


class BoatGameEnvironment(Game):

    def __init__(self, state, num_actions, _max_episode_timesteps, game_name="BoatGameEnvironment",
                 input_mode='dense_embedding', no_graphics=False, seed=False, verbose=False, manual_input=False):
        """
        :param state: (State, *required*) the State of the game, one of DenseEmbeddingState or TransformerState;
        :param num_actions: (int > 0, *required*) the number of discrete action NPC has;
        :param _max_episode_timesteps: (int > 0, required) the number of timesteps within an episode of the game;
        :param no_graphics: (bool, default False) if true, you can see the game while npc is training;
        :param seed: (int >= 0, default None) the seed used to reset the game;
        :param input_mode: (string, one of ['dense_embedding', 'transformer'], *required*) the input mode of NPC.
        """

        self.game_name = game_name
        self.game = BoatGame()
        self.inpute_mode = input_mode
        self.no_graphics = no_graphics
        self.seed = seed

        super(BoatGameEnvironment, self).__init__(state, num_actions, _max_episode_timesteps,
                                                    use_double_agent=False, double_agent=None,
                                                    verbose=verbose, manual_input=manual_input)

    # Method that closes the game
    def close(self):
        self.game.close()

    # Method that resets the game to a new episode. It returns a state dict.
    def reset(self):
        game_info = self.game.reset()

        observation = self.get_input_observation(game_info)

        if self.verbose:
            print(game_info['glyphs'])
            #print(np.sum(observation['global_view'], axis=2))
            print(observation['property_view_0'])

        return observation

    # Method that make a step in the game. It takes an action and returns (state, done, reward).
    def execute(self, actions):

        actions = self.get_manual_input(actions)
        game_info, reward, done, _ = self.game.step(actions)

        observation = self.get_input_observation(game_info, prev_action=actions)

        if self.verbose:
            print(game_info['glyphs'])
            print(observation['property_view_0'])

        return (observation, done, reward)

    def get_input_observation(self, game_info, prev_action = None) -> dict:

        global_view_one_hot = self.to_one_hot(game_info['glyphs'], 10)

        prev_action_vector = np.zeros(self.num_actions)
        if prev_action is not None:
            prev_action_vector[prev_action] = 1

        observation = {
            'global_view': global_view_one_hot,
            'property_view_0': game_info['blstats'],
            'prev_action': prev_action_vector
        }

        return observation

    def command_to_action(self, command):
        print(command)
        return int(command)