import matplotlib
import matplotlib.pyplot as plt

class PandemicGroup:
    def __init__(self, N, I, beta, gamma, iota = 0.00):
        self.data = []
        self.N = N
        self.s = float(N - I) / float(N) # Probability of being susceptible
        self.i = float(I) / float(N)     # Probability of being infectious
        self.r = 0.0                     # Probability of being recovered

        self.beta = beta                 # Probability of becoming infectious
        self.gamma = gamma               # Probability of becoming recovered
        self.iota = iota                 # Probability of becoming susceptible again

    def iteration(self, time=1.0):
        # Compute changes in the system
        delta_s = (-self.beta * self.s * self.i + self.iota * self.r) * time
        delta_i = (self.beta * self.s * self.i - self.gamma * self.i) * time
        delta_r = (self.gamma * self.i - self.iota * self.r) * time

        self.s += delta_s
        self.i += delta_i
        self.r += delta_r

        return {
            's': self.s,
            'i': self.i,
            'r': self.r
        }
    
    @staticmethod
    def plot_advancement(group, t_limit):
        s_results = []
        i_results = []
        r_results = []
        t_axis = []

        # Run the simulation for t_limit iterations
        for t in range(t_limit):
            result = group.iteration()
            s_results.append(result['s'])
            i_results.append(result['i'])
            r_results.append(result['r'])
            t_axis.append(t)

        # Build the chart
        _, ax = plt.subplots()
        ax.plot(t_axis, s_results)
        ax.plot(t_axis, i_results)
        ax.plot(t_axis, r_results)
        ax.set(xlabel='time (s)', ylabel='persons (%)', title='Group pandemic')
        ax.grid()
        plt.show()
