import time
from copy import deepcopy
from math import log, sqrt
from random import choice


class Board:

    def __init__(self, _board):
        self.length = 20
        self.board = deepcopy(_board)
        self.available_actions = set(
            [(i, j) for i in range(self.length) for j in range(self.length) if _board[i][j] == 0])
        self.winner = 0  # 0 means there is no winner.

    def is_board_full(self):
        return 1 if len(self.available_actions) == 0 else 0

    def is_kill(self, player, action):
        """
        check if a action can make the player win
        :param player
        :param action
        :return: 0 for not end yet while 1 for player 1 and 2 for player 2
        """
        board = self.board
        board[action[0]][action[1]] = player
        x, y = action
        direction = [(1, 0), (0, 1), (1, 1), (-1, 1)]
        # dir_idx = (1, -1)
        for dir in direction:
            dx = dir[0]  # moving direction
            dy = dir[1]
            start = (x - 4 * dx, y - 4 * dy)  # define starting point
            for i in range(5):
                pre_x = next_start_x = start[0] + i * dx
                pre_y = next_start_y = start[1] + i * dy
                five_line = player
                for j in range(5):
                    x_tmp = next_start_x + j * dx
                    y_tmp = next_start_y + j * dy
                    if x_tmp < 0 or y_tmp < 0 or x_tmp >= self.length or y_tmp >= self.length:
                        five_line = 0
                        break
                    if board[x_tmp][y_tmp] != board[pre_x][pre_y]:
                        five_line = 0
                        break
                    pre_x = x_tmp
                    pre_y = y_tmp
                if five_line:
                    board[action[0]][action[1]] = 0
                    return player
        board[action[0]][action[1]] = 0
        return 0

    def do_action(self, player, action):
        """
        a player makes a action on the board
        :param player:
        :param action:
        :return: None
        """
        self.board[action[0]][action[1]] = player
        self.available_actions.remove(action)


def get_radius_moves(_board, position, radius=1):
    x, y = position
    x_s, y_s = (x - radius, y - radius)
    actions = []
    for i in range(2 * radius + 1):
        for j in range(2 * radius + 1):
            x_0 = x_s + i
            y_0 = y_s + j
            if 20 > x_0 >= 0 and 20 > y_0 >= 0:
                actions.append((x_0, y_0))
    return actions


class TreeNode:

    def __init__(self, action, player=None, ucb=0, parent=None,
                 child_num=-1, child_actions=None, expand_actions=None):
        self.action = action
        self.ucb = ucb  # not used yet
        self.parent = parent
        self.children = []
        self.sim_num = 0
        self.win_num = 0
        self.max_child_length = child_num
        self.child_actions = deepcopy(child_actions)
        self.expand_actions = deepcopy(expand_actions)
        if parent is not None:
            parent.children.append(self)
            if parent.max_child_length > 0:
                self.max_child_length = parent.max_child_length - 1
            parent.expand_actions.remove(action)
            self.child_actions = deepcopy(parent.child_actions)
            self.child_actions.remove(action)
            self.expand_actions = deepcopy(self.child_actions)

            self.opponent = parent.player
            self.player = parent.opponent
        else:
            self.player = 3-player
            self.opponent = player


class MCTS:

    def __init__(self, _board, player, confidence=1.96, time_cons=7.0, max_simulation_num=12, max_simulation_1play=50):
        self.time_cons = float(time_cons)
        self.max_simulation_num = max_simulation_num
        self.max_simulation_1play = max_simulation_1play
        self.board = Board(_board)
        self.confidence = confidence
        self.player = player
        neighbor_actions = []
        for i in range(20):
            for j in range(20):
                if self.board.board[i][j]:
                    for tmp_action in get_radius_moves(self.board.board, (i, j)):
                        if tmp_action not in neighbor_actions and tmp_action in self.board.available_actions:
                            neighbor_actions.append(tmp_action)
        self.root = TreeNode(None, player, child_num=len(neighbor_actions), child_actions=neighbor_actions,
                             expand_actions=neighbor_actions)

    def get_player(self, player):
        return 3-player

    def get_best_action(self):
        if sum([sum(x) for x in self.board.board]) == 0:
            return 10, 10
        node_num = 0
        for action in self.root.expand_actions:
            if self.board.is_kill(1, action) > 0:
                return action
        for action in self.root.expand_actions:
            if self.board.is_kill(2, action) > 0:
                return action
        start_time = time.time()
        while time.time() - start_time < self.time_cons:
            expand_nodes = self.select_expand()
            for _ in range(self.max_simulation_num):
                board_copy = deepcopy(self.board)
                self.simulate_back_prop(board_copy, expand_nodes)

            node_num += 1
        # print(node_num)
        win_rate, action = max((child.win_num / child.sim_num, child.action) for child in self.root.children)
        return action

    def select_expand(self):
        node = self.root
        while node.children:
            if len(node.children) < node.max_child_length:
                break
            ucb, tar_node = 0, None
            for child in node.children:
                ucb_child = child.win_num / child.sim_num + sqrt(2 * log(node.sim_num) / child.sim_num)
                if ucb_child >= ucb:
                    ucb, tar_node = ucb_child, child
            node = tar_node
        expand_action = choice(list(node.expand_actions))
        expand_node = TreeNode(expand_action, parent=node)
        parent_action = [expand_action]
        tmp_node = expand_node
        while tmp_node.parent.action:
            tmp_node = tmp_node.parent
            parent_action.append(tmp_node.action)
        for tmp in get_radius_moves(self.board.board, expand_action):
            if tmp not in expand_node.child_actions and tmp in self.board.available_actions and tmp not in parent_action:
                expand_node.child_actions.append(tmp)
                expand_node.expand_actions.append(tmp)
        return expand_node

    def simulate_back_prop(self, board, expand_node):
        node = expand_node
        available_actions = deepcopy(expand_node.expand_actions)
        while node.parent.action:
            node = node.parent
            board.do_action(node.player, node.action)
            if node.action in available_actions:
                available_actions.remove(node.action)
        for tmp in available_actions:
            if tmp not in board.available_actions:
                available_actions.remove(tmp)
        if len(available_actions) == 0:
            return
        player = expand_node.player
        is_win = board.is_kill(player, expand_node.action)
        board.do_action(player, expand_node.action)
        if expand_node.action in available_actions:
            available_actions.remove(expand_node.action)
        for t in range(1, self.max_simulation_1play + 1):
            is_full = board.is_board_full()
            if is_win or is_full:
                break
            player = self.get_player(player)
            action = choice(list(available_actions))
            is_win = board.is_kill(player, action)
            board.do_action(player, action)
            available_actions.remove(action)
            for tmp in get_radius_moves(board.board, action):
                if tmp not in available_actions and tmp in board.available_actions:
                    available_actions.append(tmp)
        cur_node = expand_node
        while cur_node:
            cur_node.sim_num += 1
            if is_win and cur_node.player == player:
                cur_node.win_num += 1
            cur_node = cur_node.parent



