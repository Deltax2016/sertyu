import copy
import numpy as np

class HMM():

    def __init__(self, transmission_prob, emission_prob, obs=None):
     
        self.transmission_prob = transmission_prob
        self.emission_prob = emission_prob
        self.n = self.emission_prob.shape[1]
        self.m = self.emission_prob.shape[0]
        self.observations = None
        self.forward = []
        self.backward = []
        self.psi = []
        self.obs = obs
        self.emiss_ref = {}
        self.forward_final = [0 , 0]
        self.backward_final = [0 , 0]
        self.state_probs = []
        if obs is None and self.observations is not None:
            self.obs = self.assume_obs()

    def assume_obs(self):

        obs = list(set(list(self.observations)))
        obs.sort()
        for i in range(len(obs)):
            self.emiss_ref[obs[i]] = i
        return obs

    def train(self, observations, iterations = 10, verbose=True):

        self.observations = observations
        self.obs = self.assume_obs()
        self.psi = [[[0.0] * (len(self.observations)-1) for i in range(self.n)] for i in range(self.n)]
        self.gamma = [[0.0] * (len(self.observations)) for i in range(self.n)]
        for i in range(iterations):
            old_transmission = self.transmission_prob.copy()
            old_emission = self.emission_prob.copy()
            if verbose:
                print("Iteration: {}".format(i + 1))
            self.expectation()
            self.maximization()

    def expectation(self):

        self.forward = self.forward_recurse(len(self.observations))
        self.backward = self.backward_recurse(0)
        self.get_gamma()
        self.get_psi()

    def get_gamma(self):

        self.gamma = [[0, 0] for i in range(len(self.observations))]
        for i in range(len(self.observations)):
            self.gamma[i][0] = (float(self.forward[0][i] * self.backward[0][i]) /
                                float(self.forward[0][i] * self.backward[0][i] +
                                self.forward[1][i] * self.backward[1][i]))
            self.gamma[i][1] = (float(self.forward[1][i] * self.backward[1][i]) /
                                float(self.forward[0][i] * self.backward[0][i] +
                                self.forward[1][i] * self.backward[1][i]))

    def get_psi(self):

        for t in range(1, len(self.observations)):
            for j in range(self.n):
                for i in range(self.n):
                    self.psi[i][j][t-1] = self.calculate_psi(t, i, j)

    def calculate_psi(self, t, i, j):

        alpha_tminus1_i = self.forward[i][t-1]
        a_i_j = self.transmission_prob[j+1][i+1]
        beta_t_j = self.backward[j][t]
        observation = self.observations[t]
        b_j = self.emission_prob[self.emiss_ref[observation]][j]
        denom = float(self.forward[0][i] * self.backward[0][i] + self.forward[1][i] * self.backward[1][i])
        return (alpha_tminus1_i * a_i_j * beta_t_j * b_j) / denom

    def maximization(self):

        self.get_state_probs()
        for i in range(self.n):
            self.transmission_prob[i+1][0] = self.gamma[0][i]
            self.transmission_prob[-1][i+1] = self.gamma[-1][i] / self.state_probs[i]
            for j in range(self.n):
                self.transmission_prob[j+1][i+1] = self.estimate_transmission(i, j)
            for obs in range(self.m):
                self.emission_prob[obs][i] = self.estimate_emission(i, obs)

    def get_state_probs(self):

        self.state_probs = [0] * self.n
        for state in range(self.n):
            summ = 0
            for row in self.gamma:
                summ += row[state]
            self.state_probs[state] = summ

    def estimate_transmission(self, i, j):

        return sum(self.psi[i][j]) / self.state_probs[i]

    def estimate_emission(self, j, observation):

        observation = self.obs[observation]
        ts = [i for i in range(len(self.observations)) if self.observations[i] == observation]
        for i in range(len(ts)):
            ts[i] = self.gamma[ts[i]][j]
        return sum(ts) / self.state_probs[j]

    def backward_recurse(self, index):

        if index == (len(self.observations) - 1):
            backward = [[0.0] * (len(self.observations)) for i in range(self.n)]
            for state in range(self.n):
                backward[state][index] = self.backward_initial(state)
            return backward
        else:
            backward = self.backward_recurse(index+1)
            for state in range(self.n):
                if index >= 0:
                    backward[state][index] = self.backward_probability(index, backward, state)
                if index == 0:
                    self.backward_final[state] = self.backward_probability(index, backward, 0, final=True)
            return backward

    def backward_initial(self, state):

        return self.transmission_prob[self.n + 1][state + 1]

    def backward_probability(self, index, backward, state, final=False):

        p = [0] * self.n
        for j in range(self.n):
            observation = self.observations[index + 1]
            if not final:
                a = self.transmission_prob[j + 1][state + 1]
            else:
                a = self.transmission_prob[j + 1][0]
            b = self.emission_prob[self.emiss_ref[observation]][j]
            beta = backward[j][index + 1]
            p[j] = a * b * beta
        return sum(p)

    def forward_recurse(self, index):

        if index == 0:
            forward = [[0.0] * (len(self.observations)) for i in range(self.n)]
            for state in range(self.n):
                forward[state][index] = self.forward_initial(self.observations[index], state)
            return forward
        else:
            forward = self.forward_recurse(index-1)
            for state in range(self.n):
                if index != len(self.observations):
                    forward[state][index] = self.forward_probability(index, forward, state)
                else:
                    self.forward_final[state] = self.forward_probability(index, forward, state, final=True)
            return forward

    def forward_initial(self, observation, state):
        self.transmission_prob[state + 1][0]
        self.emission_prob[self.emiss_ref[observation]][state]
        return self.transmission_prob[state + 1][0] * self.emission_prob[self.emiss_ref[observation]][state]

    def forward_probability(self, index, forward, state, final=False):

        p = [0] * self.n
        for prev_state in range(self.n):
            if not final:
                obs_index = self.emiss_ref[self.observations[index]]
                p[prev_state] = forward[prev_state][index-1] * self.transmission_prob[state + 1][prev_state + 1] * self.emission_prob[obs_index][state]
            else:

                p[prev_state] = forward[prev_state][index-1] * self.transmission_prob[self.n][prev_state + 1]
        return sum(p)

    def likelihood(self, new_observations):

        new_hmm = HMM(self.transmission_prob, self.emission_prob)
        new_hmm.observations = new_observations
        new_hmm.obs = new_hmm.assume_obs()
        forward = new_hmm.forward_recurse(len(new_observations))
        return sum(new_hmm.forward_final)
