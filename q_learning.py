import numpy as np

q_table = {}
alpha = 1
epsilon = 1
gamma = 1

def q_lookup(state):
    return q_table.get(state)

def q_new_entry(state):
    q_table[state] = [0,0,0,0]
    return

def q_update(actionlist, newstate, reward):
    for state, action in actionlist.items():
        if q_lookup(state) is None:
            q_new_entry(state)
        else:
            print("Test")

        q_table[state][action] = reward
        print(q_table)
    return