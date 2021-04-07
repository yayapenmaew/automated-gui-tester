import numpy as np
import random


class BaseGeneticOptimizer:
    def __init__(self, rules, random_state=None):
        self.rules = rules
        self.random_state = random_state
        if random_state:
            random.seed(random_state)
            np.random.seed(random_state)

    def fitness(self, agent):
        return sum(agent)

    def __calc_finess(self, agents):
        return sorted([(self.fitness(agent), agent) for agent in agents], reverse=True)

    def __initialization(self, size):
        n_feature = len(self.rules)
        return [np.random.randint(2, size=n_feature).tolist() for i in range(size)]

    def __selection(self, ranked_agents, n_parents):
        assert n_parents <= len(ranked_agents)
        parents = []
        for i in range(n_parents):
            parents.append(ranked_agents[i])
        return parents

    def __crossover(self, ranked_parents, n_offsprings):
        n_parents = len(ranked_parents)
        parents_agent = [agent for _, agent in ranked_parents]
        random.shuffle(parents_agent)

        crossover_point = len(ranked_parents[0][1]) // 2

        offsprings = []
        for i in range(n_offsprings):
            parent_1 = parents_agent[i % n_parents]
            parent_2 = parents_agent[(i + 1) % n_parents]
            offsprings.append(
                list(parent_1[:crossover_point] + parent_2[crossover_point:]))

        return offsprings

    def __mutation(self, agents, mutation_rate):
        for agent in agents:
            for i in range(len(agent)):
                if random.random() < mutation_rate:
                    agent[i] = 1 - agent[i]

    def __show_ranking(self, ranked_agents):
        for score, agent in ranked_agents:
            print(agent, score)

    def __show_pop(self, agents):
        for agent in agents:
            print(agent)

    def optimize(self, pop_size=8, n_gen=5, n_parents=4, r_mut=0.05):
        population = self.__initialization(pop_size)
        best_score = float("-inf")
        best_agent = None

        for i in range(n_gen):
            ranked_agents = self.__calc_finess(population)
            print('Ranking')
            self.__show_ranking(ranked_agents)

            if ranked_agents[0][0] > best_score:
                best_score, best_agent = ranked_agents[0]

            parents = self.__selection(ranked_agents, n_parents)

            offsprings = self.__crossover(parents, n_offsprings=pop_size)
            self.__mutation(offsprings, r_mut)

            population = offsprings

        print()
        print('Best score:', best_score)
        print('Agent:', best_agent)


if __name__ == '__main__':
    optimizer = BaseGeneticOptimizer([0] * 30)
    optimizer.optimize()
