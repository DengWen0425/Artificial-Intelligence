# search.py
# ---------
# Licensing Information:  You are free to use or extend these projects for
# educational purposes provided that (1) you do not distribute or publish
# solutions, (2) you retain this notice, and (3) you provide clear
# attribution to UC Berkeley, including a link to http://ai.berkeley.edu.
# 
# Attribution Information: The Pacman AI projects were developed at UC Berkeley.
# The core projects and autograders were primarily created by John DeNero
# (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# Student side autograding was added by Brad Miller, Nick Hay, and
# Pieter Abbeel (pabbeel@cs.berkeley.edu).


"""
In search.py, you will implement generic search algorithms which are called by
Pacman agents (in searchAgents.py).
"""

import util

class SearchProblem:
    """
    This class outlines the structure of a search problem, but doesn't implement
    any of the methods (in object-oriented terminology: an abstract class).

    You do not need to change anything in this class, ever.
    """

    def getStartState(self):
        """
        Returns the start state for the search problem.
        """
        util.raiseNotDefined()

    def isGoalState(self, state):
        """
          state: Search state

        Returns True if and only if the state is a valid goal state.
        """
        util.raiseNotDefined()

    def getSuccessors(self, state):
        """
          state: Search state

        For a given state, this should return a list of triples, (successor,
        action, stepCost), where 'successor' is a successor to the current
        state, 'action' is the action required to get there, and 'stepCost' is
        the incremental cost of expanding to that successor.
        """
        util.raiseNotDefined()

    def getCostOfActions(self, actions):
        """
         actions: A list of actions to take

        This method returns the total cost of a particular sequence of actions.
        The sequence must be composed of legal moves.
        """
        util.raiseNotDefined()


def tinyMazeSearch(problem):
    """
    Returns a sequence of moves that solves tinyMaze.  For any other maze, the
    sequence of moves will be incorrect, so only use this for tinyMaze.
    """
    from game import Directions
    s = Directions.SOUTH
    w = Directions.WEST
    return  [s, s, w, s, w, w, s, w]

def depthFirstSearch(problem):
    """
    Search the deepest nodes in the search tree first.

    Your search algorithm needs to return a list of actions that reaches the
    goal. Make sure to implement a graph search algorithm.

    To get started, you might want to try some of these simple commands to
    understand the search problem that is being passed in:

    print "Start:", problem.getStartState()
    print "Is the start a goal?", problem.isGoalState(problem.getStartState())
    print "Start's successors:", problem.getSuccessors(problem.getStartState())
    """
    "*** YOUR CODE HERE ***"
    # initializing
    node = (problem.getStartState(), [], 0)

    # Define a lifo stack
    frontier = util.Stack()
    frontier.push(node)

    # Define an explored set
    explored = {}

    # DFS search
    while not frontier.isEmpty():
        (node) = frontier.pop()
        if problem.isGoalState(node[0]):
            return node[1]
        explored[node[0]] = node[0]
        for successor, action, cost in problem.getSuccessors(node[0]):
            if successor not in explored:
                frontier.push((successor, node[1]+[action], node[2]+cost))
    return False

    util.raiseNotDefined()

def breadthFirstSearch(problem):
    """Search the shallowest nodes in the search tree first."""
    "*** YOUR CODE HERE ***"
    # initializing
    node = (problem.getStartState(), [], 0)
    if problem.isGoalState(node[0]):
        return node[1]

    # Define a fifo queue
    frontier = util.Queue()
    frontier.push(node)

    # Define an explored set
    explored = {}

    # BFS search
    while not frontier.isEmpty():
        (node) = frontier.pop()
        explored[node[0]] = node[0]
        for successor, action, cost in problem.getSuccessors(node[0]):
            if successor not in explored and successor not in [x[0] for x in frontier.list]:
                if problem.isGoalState(successor):
                    return node[1]+[action]
                frontier.push((successor, node[1]+[action], node[2]+cost))
    return False

    util.raiseNotDefined()

def uniformCostSearch(problem):
    """Search the node of least total cost first."""
    "*** YOUR CODE HERE ***"
    # initializing
    node = (problem.getStartState(), [], 0)

    # Define a PriorityQueue with path cost
    frontier = util.PriorityQueue()
    frontier.push(node, 0)

    # Define an explored set
    explored = []

    # UCS
    while not frontier.isEmpty():
        item = frontier.pop()
        if problem.isGoalState(item[0]):
            return item[1]
        explored.append(item[0])
        successors = problem.getSuccessors(item[0])
        for successor, action, cost in successors:
            if successor not in explored:
                priority = problem.getCostOfActions(item[1]) + cost
                is_seen = False
                for x in frontier.heap:
                    if successor == x[2][0]:
                        is_seen = True
                        if priority < x[0]:
                            frontier.update((successor, item[1] + [action]), priority)
                        break
                if not is_seen:
                    frontier.push((successor, item[1] + [action]), priority)

    return False

    util.raiseNotDefined()

def nullHeuristic(state, problem=None):
    """
    A heuristic function estimates the cost from the current state to the nearest
    goal in the provided SearchProblem.  This heuristic is trivial.
    """
    return 0

def aStarSearch(problem, heuristic=nullHeuristic):
    """Search the node that has the lowest combined cost and heuristic first."""
    "*** YOUR CODE HERE ***"
    # initializing
    start_state = problem.getStartState()
    node = (start_state, [])

    # Define a PriorityQueue with path cost
    frontier = util.PriorityQueue()
    frontier.push(node, heuristic(start_state, problem))

    # Define an explored set
    explored = {}

    # A* Search
    while not frontier.isEmpty():
        item = frontier.pop()
        if problem.isGoalState(item[0]):
            return item[1]
        explored[item[0]] = item[0]
        successors = problem.getSuccessors(item[0])
        for successor, action, cost in successors:
            if successor not in explored:
                priority = problem.getCostOfActions(item[1]) + cost + heuristic(successor, problem)
                is_seen = False
                for x in frontier.heap:
                    if successor == x[2][0]:
                        is_seen = True
                        if priority < x[0]:
                            frontier.update((successor, item[1] + [action]), priority)
                        break
                if not is_seen:
                    frontier.push((successor, item[1] + [action]), priority)

    return False

    util.raiseNotDefined()


# Abbreviations
bfs = breadthFirstSearch
dfs = depthFirstSearch
astar = aStarSearch
ucs = uniformCostSearch
