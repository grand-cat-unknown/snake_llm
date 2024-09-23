import numpy as np

class QLearningAgent:
    def __init__(self, state_size, action_size, learning_rate=0.1, discount_factor=0.95, exploration_rate=1.0, exploration_decay=0.995):
        self.state_size = state_size
        self.action_size = action_size
        self.learning_rate = learning_rate
        self.discount_factor = discount_factor
        self.exploration_rate = exploration_rate
        self.exploration_min = 0.01
        self.exploration_decay = exploration_decay
        self.q_table = {}

    def get_action(self, state):
        state_key = self._get_state_key(state)
        if np.random.rand() <= self.exploration_rate:
            return np.random.randint(self.action_size)
        return np.argmax(self._get_q_values(state_key))

    def update(self, state, action, reward, next_state, done):
        state_key = self._get_state_key(state)
        next_state_key = self._get_state_key(next_state)
        
        current_q = self._get_q_values(state_key)[action]
        if done:
            target_q = reward
        else:
            target_q = reward + self.discount_factor * np.max(self._get_q_values(next_state_key))
        
        new_q = current_q + self.learning_rate * (target_q - current_q)
        self.q_table[state_key][action] = new_q

        if self.exploration_rate > self.exploration_min:
            self.exploration_rate *= self.exploration_decay

    def _get_state_key(self, state):
        return tuple(map(tuple, state))

    def _get_q_values(self, state_key):
        if state_key not in self.q_table:
            self.q_table[state_key] = np.zeros(self.action_size)
        return self.q_table[state_key]