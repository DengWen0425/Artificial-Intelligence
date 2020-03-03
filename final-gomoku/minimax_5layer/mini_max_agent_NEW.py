from enum import IntEnum
from queue import PriorityQueue
import time
from copy import deepcopy

width = 20
height = 20
AI_SEARCH_DEPTH = 5


class CHESS_TYPE(IntEnum):
    NONE = 0,
    SLEEP_TWO = 1,
    LIVE_TWO = 2,
    SLEEP_THREE = 3
    LIVE_THREE = 4,
    CHONG_FOUR = 5,
    LIVE_FOUR = 6,
    LIVE_FIVE = 7,


CHESS_TYPE_NUM = 8

FIVE = CHESS_TYPE.LIVE_FIVE.value
FOUR, THREE, TWO = CHESS_TYPE.LIVE_FOUR.value, CHESS_TYPE.LIVE_THREE.value, CHESS_TYPE.LIVE_TWO.value
SFOUR, STHREE, STWO = CHESS_TYPE.CHONG_FOUR.value, CHESS_TYPE.SLEEP_THREE.value, CHESS_TYPE.SLEEP_TWO.value

SCORE_MAX = 0x7fffffff
SCORE_MIN = -1 * SCORE_MAX
SCORE_FIVE, SCORE_FOUR, SCORE_SFOUR = 100000, 10000, 2000
SCORE_THREE, SCORE_STHREE, SCORE_TWO, SCORE_STWO = 2000, 100, 100, 10


class niubiAI():
    def __init__(self, chess_len=20):
        self.len = chess_len
        # [horizon, vertical, left diagonal, right diagonal]
        self.record = [[[0, 0, 0, 0] for x in range(chess_len)] for y in range(chess_len)]
        self.count = [[0 for x in range(CHESS_TYPE_NUM)] for i in range(2)]
        self.time = time.time()

    def initialize(self, _board):
        self.evaluate(_board=_board, player=1, checkWin=False)

    def Alpha_Beta_Search(self, state, a=float("-inf"), b=float("inf"), depth=AI_SEARCH_DEPTH):
        if sum([sum(x) for x in state[0]]) == 0:
            return 10, 10
        best = None
        max_eval = float("-inf")
        origin_count = [[y for y in x] for x in self.count]
        actions = self.weighted_actions(state)
        cut = max(actions.qsize()*4/5, actions.qsize() - 15)
        while actions.qsize() > cut:
            # while not actions.empty():
            action = actions.get()
            if action[0] <= 200 - SCORE_FIVE:
                return action[1]
            action = action[1]
            try:
                v = self.mini_max(self.state_transition(state, action), a, b, depth - 1)
            except TypeError:
                return best
            board = state[0]
            board[action[0]][action[1]] = 0
            self.count = deepcopy(origin_count)
            if v > max_eval:
                max_eval = v
                best = action
        return best

        # return max([(self.mini_max(self.state_transition(state, action), a, b, depth - 1), action) for action in
        #            self.get_action(state)])[1]

    def mini_max(self, state, a=500 - SCORE_FIVE, b=SCORE_FIVE - 500, depth=AI_SEARCH_DEPTH):
        _board, flag, player = state
        origin_count = [[y for y in x] for x in self.count]
        if (time.time() - self.time) > 4.0:
            return None
        if flag == 1:
            return SCORE_FIVE
        if flag == 2:
            return -SCORE_FIVE
        if depth == 0:
            mscore, oscore = self.getScore(self.count[0], self.count[1], player=player)
            return mscore - oscore
        if player == 1:  # our turn
            v = float("-inf")
            actions = self.weighted_actions(state)
            cut = max(actions.qsize()*4/5, actions.qsize() - 15)
            while actions.qsize() > cut:
                # while not actions.empty():
                action = actions.get()[1]
                v = max(v, self.mini_max(self.state_transition(state, action), a, b, depth - 1))
                board = state[0]
                board[action[0]][action[1]] = 0
                self.count = deepcopy(origin_count)
                if v >= b:
                    return v
                a = max(a, v)
            return v
        else:
            v = float("inf")
            actions = self.weighted_actions(state)
            cut = max(actions.qsize()*4/5, actions.qsize() - 15)
            while actions.qsize() > cut:
                # while not actions.empty():
                action = actions.get()[1]
                v = min(v, self.mini_max(self.state_transition(state, action), a, b, depth - 1))
                board = state[0]
                board[action[0]][action[1]] = 0
                self.count = deepcopy(origin_count)
                if v <= a:
                    return v
                b = min(b, v)
            return v

    def reset(self):
        for y in range(self.len):
            for x in range(self.len):
                for i in range(4):
                    self.record[y][x][i] = 0

        for i in range(len(self.count)):
            for j in range(len(self.count[0])):
                self.count[i][j] = 0

    def Is_kill(self, state, move):
        ''' Whether the action taken kill the game?
            input: state, action
            output: an integer(player) denotes who won  '''
        player = state[2]
        board = state[0]
        board[move[0]][move[1]] = player
        x, y = move
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
                    if x_tmp < 0 or y_tmp < 0 or x_tmp >= width or y_tmp >= height:
                        five_line = 0
                        break
                    if board[x_tmp][y_tmp] != board[pre_x][pre_y]:
                        five_line = 0
                        break
                    pre_x = x_tmp
                    pre_y = y_tmp
                if five_line:
                    board[move[0]][move[1]] = 0
                    return player
        board[move[0]][move[1]] = 0
        return 0

    def weighted_actions(self, state):
        """ :returns a List of moves """
        Board = state[0]
        player = state[2]
        available_actions = PriorityQueue()
        visited = set()
        indicator = -1
        if player == 2:
            indicator = 1
        for i in range(len(Board)):
            for j in range(len(Board)):
                if Board[i][j]:
                    for move in self.get_radius_moves(Board, (i, j), 1):
                        if move not in visited:
                            visited.add(move)
                            available_actions.put((indicator * self.getPointscore(Board, move, player), move))
        return available_actions

    def get_radius_moves(self, _board, position, radius):
        ''' :returns a List of moves '''
        x, y = position
        x_s, y_s = (x - radius, y - radius)
        moves = []
        for i in range(2 * radius + 1):
            for j in range(2 * radius + 1):
                x_0 = x_s + i
                y_0 = y_s + j
                if width > x_0 >= 0 and height > y_0 >= 0 == _board[x_0][y_0]:
                    moves.append((x_0, y_0))
        return moves

    def state_transition(self, state, action):
        x, y = action
        player = state[2]
        new_board = state[0]
        flag = 0
        mine_change, op_chcange = self.dynamic_evaluate(new_board, player, x, y)
        self.count[0] = [i + j for i, j in zip(self.count[0], mine_change)]
        self.count[1] = [i + j for i, j in zip(self.count[1], op_chcange)]
        if self.Is_kill(state, action):
            flag = player
        new_board[x][y] = player
        next_player = 3 - player
        return new_board, flag, next_player

    def getScore(self, mine_count, opponent_count, player):
        mscore, oscore = 0, 0
        mine = 1
        opponent = 2
        # if mine_count[FIVE] > 0:
        #    return SCORE_FIVE, 0
        # if opponent_count[FIVE] > 0:
        #    return 0, SCORE_FIVE
        if mine_count[SFOUR] > 1:
            mine_count[FOUR] += 1
        if opponent_count[SFOUR] > 1:
            opponent_count[FOUR] += 1

        if player == mine:
            if mine_count[FOUR] > 0:
                return SCORE_FIVE - 100, 0
            if mine_count[SFOUR] > 0:
                return SCORE_FIVE - 100, 0
            if opponent_count[FOUR] > 0:
                return 0, SCORE_FIVE - 200
            if mine_count[THREE] > 0 and opponent_count[SFOUR] == 0:
                return SCORE_FIVE - 300, 0
            if opponent_count[SFOUR] > 0 and opponent_count[THREE] > 0:
                return 0, SCORE_FOUR - 100
            if opponent_count[THREE] > 1:
                return 0, SCORE_FOUR - 300

            mscore += 300 * mine_count[THREE]
            mscore += 120 * mine_count[STHREE]
            mscore += 120 * mine_count[TWO]

            oscore += 300 * opponent_count[SFOUR]
            oscore += 300 * 0.9 * opponent_count[THREE]
            oscore += 120 * 0.9 * opponent_count[STHREE]
            oscore += 120 * 0.9 * opponent_count[TWO]
            return mscore, oscore

        if player == opponent:
            if opponent_count[FOUR] > 0:
                return 0, SCORE_FIVE - 100
            if opponent_count[SFOUR] > 0:
                return 0, SCORE_FIVE - 100
            if mine_count[FOUR] > 0:
                return SCORE_FIVE - 200, 0
            if opponent_count[THREE] > 0 and mine_count[SFOUR] == 0:
                return 0, SCORE_FIVE - 300
            if mine_count[SFOUR] > 0 and mine_count[THREE] > 0:
                return SCORE_FOUR - 100, 0
            if mine_count[THREE] > 1:
                return SCORE_FOUR - 300, 0

            oscore += 300 * opponent_count[THREE]
            oscore += 120 * opponent_count[STHREE]
            oscore += 120 * opponent_count[TWO]

            mscore += 300 * mine_count[SFOUR]
            mscore += 300 * 0.9 * mine_count[THREE]
            mscore += 120 * 0.9 * mine_count[STHREE]
            mscore += 120 * 0.9 * mine_count[TWO]
            return mscore, oscore

    def evaluate(self, _board, player, checkWin=False):
        mine = 1
        opponent = 2
        self.reset()
        for x in range(self.len):
            for y in range(self.len):
                if _board[x][y] == mine:
                    self.evaluatePoint(_board, x, y, mine, opponent)
                elif _board[x][y] == opponent:
                    self.evaluatePoint(_board, x, y, opponent, mine)

        # mine_count = self.count[mine - 1]
        # opponent_count = self.count[opponent - 1]
        # if checkWin:
        #    return mine_count[FIVE] > 0
        # else:
        #    mscore, oscore = self.getScore(mine_count, opponent_count, player)
        #    return (mscore - oscore)

    def dynamic_evaluate(self, _board, player, x, y):
        dir_offset = [(1, 0), (0, 1), (1, 1), (1, -1)]
        dir_idx = [-1, 1]
        mine_tmp = [0 for x in range(CHESS_TYPE_NUM)]
        op_tmp = [0 for x in range(CHESS_TYPE_NUM)]
        # player's circumstance change
        _board[x][y] = player
        self.evaluatePoint(_board, x, y, player, 3 - player, count=mine_tmp)
        three_off = -mine_tmp[FOUR]
        sthree_off = -mine_tmp[SFOUR]
        two_off = -mine_tmp[THREE]
        stwo_off = -mine_tmp[STHREE]
        mine_tmp[THREE] += three_off
        mine_tmp[STHREE] += sthree_off
        mine_tmp[TWO] += two_off
        mine_tmp[stwo_off] += stwo_off
        for dir in dir_offset:
            for idx in dir_idx:
                dx, dy = idx * dir[0], idx * dir[1]
                if width > x + 2 * dx >= 0 and height > y + 2 * dy >= 0:
                    if _board[x + 2 * dx][y + 2 * dy] == player and _board[x + dx][y + dy] == 0:
                        new_type = [0 for x in range(CHESS_TYPE_NUM)]
                        old_type = [0 for x in range(CHESS_TYPE_NUM)]
                        self.analysisLine(_board, x + 2 * dx, y + 2 * dy, 0, dir, player, 3 - player, count=new_type)
                        _board[x][y] = 0
                        self.analysisLine(_board, x + 2 * dx, y + 2 * dy, 0, dir, player, 3 - player, count=old_type)
                        offset = [i - j for i, j in zip(new_type, old_type)]
                        mine_tmp = [i + j for i, j in zip(mine_tmp, offset)]
                        _board[x][y] = player
        # opponent 's change
        for dir in dir_offset:
            for idx in dir_idx:
                _board[x][y] = player
                dx, dy = idx * dir[0], idx * dir[1]
                if width > x + dx >= 0 and height > y + dy >= 0 and _board[x + dx][y + dy] == 3 - player:
                    new_type = [0 for x in range(CHESS_TYPE_NUM)]
                    old_type = [0 for x in range(CHESS_TYPE_NUM)]
                    self.analysisLine(_board, x + dx, y + dy, 0, dir, 3 - player, player, count=new_type)
                    _board[x][y] = 0
                    self.analysisLine(_board, x + dx, y + dy, 0, dir, 3 - player, player, count=old_type)
                    offset = [i - j for i, j in zip(new_type, old_type)]
                    op_tmp = [i + j for i, j in zip(op_tmp, offset)]
                else:
                    if x + dx <= 19 and y + dy <= 19 and _board[x + dx][y + dy] == 0 and width > x + 2 * dx >= 0 and height > y + 2 * dy >= 0 and _board[x + 2 * dx][y + 2 * dy] == 3 - player:
                        new_type = [0 for x in range(CHESS_TYPE_NUM)]
                        old_type = [0 for x in range(CHESS_TYPE_NUM)]
                        self.analysisLine(_board, x + 2 * dx, y + 2 * dy, 0, dir, 3 - player, player, count=new_type)
                        _board[x][y] = 0
                        self.analysisLine(_board, x + 2 * dx, y + 2 * dy, 0, dir, 3 - player, player, count=old_type)
                        offset = [i - j for i, j in zip(new_type, old_type)]
                        op_tmp = [i + j for i, j in zip(op_tmp, offset)]
        _board[x][y] = 0
        if player == 1:
            return mine_tmp, op_tmp
        else:
            return op_tmp, mine_tmp
        # self.count[player - 1] = [i + j for i, j in zip(self.count[player - 1], mine_tmp)]
        # self.count[2 - player] = [i + j for i, j in zip(self.count[2 - player], op_tmp)]

    def getPointscore_3(self, _board, pos, player):
        x, y = pos
        mine_count = [x for x in self.count[0]]
        op_count = [x for x in self.count[1]]
        mine_change = self.dynamic_evaluate(_board, player=1, x=x, y=y)[0]
        op_change = self.dynamic_evaluate(_board, player=2, x=x, y=y)[1]
        mine_count = [i + j for i, j in zip(mine_count, mine_change)]
        op_count = [i + j for i, j in zip(op_count, op_change)]

        if mine_count[SFOUR] > 1:
            mine_count[FOUR] += 1
        if op_count[SFOUR] > 1:
            op_count[FOUR] += 1
        if player == 1:
            res = 0
            if mine_count[FIVE] > 0:
                return SCORE_FIVE
            if op_count[FIVE] > 0:
                return SCORE_FIVE - 100
            if mine_count[SFOUR] > 0 and mine_count[THREE] > 0:
                return SCORE_FOUR
            if mine_count[FOUR] > 0:
                return SCORE_FOUR
            if op_count[FOUR] > 0:
                return SCORE_FOUR - 100
            if op_count[SFOUR] > 0 and op_count[THREE] > 0:
                return SCORE_FOUR - 100
            if mine_count[THREE] > 1:
                return SCORE_FOUR - 200
            if op_count[THREE] > 1:
                return SCORE_FOUR - 200
            res = (mine_count[SFOUR] + mine_count[THREE])*300 + (mine_count[STHREE] + mine_count[TWO])*120 \
            + (op_count[SFOUR] + op_count[THREE])*290 + (op_count[STHREE] + op_count[TWO])*100
            return res
        if player == 2:
            res = 0
            if op_count[FIVE] > 0:
                return -SCORE_FIVE
            if mine_count[FIVE] > 0:
                return -SCORE_FIVE + 100
            if op_count[SFOUR] > 0 and op_count[THREE] > 0:
                return -SCORE_FOUR
            if op_count[FOUR] > 0:
                return -SCORE_FOUR
            if op_count[THREE] > 1:
                return -SCORE_FOUR + 100
            if mine_count[SFOUR] > 0 and mine_count[THREE] > 0:
                return -SCORE_FOUR + 100
            if mine_count[FOUR] > 0:
                return -SCORE_FOUR + 200
            res = (mine_count[SFOUR] + mine_count[THREE]) * 290 + (mine_count[STHREE] + mine_count[TWO]) * 100 \
                  + (op_count[SFOUR] + op_count[THREE]) * 300 + (op_count[STHREE] + op_count[TWO]) * 120
            return -res

    def getPointscore_2(self, _board, pos, player):
        x, y = pos
        dir_offset = [(1, 0), (0, 1), (1, 1), (1, -1)]
        mine_count = [0 for x in range(8)]
        op_count = [0 for x in range(8)]
        _board[x][y] = player
        for i in range(4):
            self.analysisLine(_board, y, x, i, dir_offset[i], 1, 2, mine_count)

        _board[x][y] = 3 - player
        for i in range(4):
            self.analysisLine(_board, y, x, i, dir_offset[i], 2, 1, op_count)
        _board[x][y] = 0

        if mine_count[SFOUR] > 1:
            mine_count[FOUR] += 1
        if op_count[SFOUR] > 1:
            op_count[FOUR] += 1
        if player == 1:
            res = 0
            if mine_count[FIVE] > 0:
                return SCORE_FIVE
            if op_count[FIVE] > 0:
                return SCORE_FIVE - 100
            if mine_count[SFOUR] > 0 and mine_count[THREE] > 0:
                return SCORE_FOUR
            if mine_count[FOUR] > 0:
                return SCORE_FOUR
            if op_count[FOUR] > 0:
                return SCORE_FOUR - 100
            if op_count[SFOUR] > 0 and op_count[THREE] > 0:
                return SCORE_FOUR - 100
            if mine_count[THREE] > 1:
                return SCORE_FOUR - 300
            res = mine_count[SFOUR] * SCORE_SFOUR + mine_count[THREE] * SCORE_THREE + mine_count[TWO] * SCORE_TWO \
                  + mine_count[STHREE] * SCORE_STHREE + op_count[SFOUR] * (2 * SCORE_TWO - 10)
            return res
        if player == 2:
            res = 0
            if op_count[FIVE] > 0:
                return -SCORE_FIVE
            if mine_count[FIVE] > 0:
                return -SCORE_FIVE + 100
            if op_count[SFOUR] > 0 and op_count[THREE] > 0:
                return -SCORE_FOUR
            if op_count[FOUR] > 0:
                return -SCORE_FOUR
            if op_count[THREE] > 1:
                return -SCORE_FOUR + 100
            if mine_count[SFOUR] > 0 and mine_count[THREE] > 0:
                return -SCORE_FOUR + 100
            if mine_count[FOUR] > 0:
                return -SCORE_FOUR + 200
            res = op_count[SFOUR] * SCORE_SFOUR + op_count[THREE] * SCORE_THREE + op_count[TWO] * SCORE_TWO \
                  + op_count[STHREE] * SCORE_STHREE + mine_count[SFOUR] * (2 * SCORE_TWO - 10)
            return -res

    def getPointscore(self, _board, pos, player):
        x, y = pos
        mine_count, op_count = self.dynamic_evaluate(_board, player=player, x=x, y=y)
        if player == 1:
            if mine_count[FIVE] > 0:
                return SCORE_FIVE
            if op_count[SFOUR] < 0:
                return SCORE_FIVE - 100
            if mine_count[FOUR] > 0:
                return SCORE_FOUR
            if mine_count[SFOUR] > 0 and mine_count[THREE] > 0:
                return SCORE_FOUR
            if op_count[THREE] < 0:
                return SCORE_FOUR - 500 - op_count[THREE] * 100
            if mine_count[THREE] > 1:
                return SCORE_FOUR - 1000
            res = (mine_count[SFOUR] + mine_count[THREE]) * 360 + (mine_count[STHREE] + mine_count[TWO]) * 100 \
                  + (-op_count[STHREE] - op_count[TWO]) * 100
            return res
        if player == 2:
            if op_count[FIVE] > 0:
                return -SCORE_FIVE
            if mine_count[SFOUR] < 0:
                return -SCORE_FIVE + 100
            if op_count[FOUR] > 0:
                return -SCORE_FOUR
            if op_count[SFOUR] > 0 and op_count[THREE] > 0:
                return -SCORE_FOUR
            if mine_count[THREE] < 0:
                return -SCORE_FOUR + 500 + mine_count[THREE] * 100
            if op_count[THREE] > 1:
                return -SCORE_FOUR + 1000
            res = (op_count[SFOUR] + op_count[THREE]) * 360 + (op_count[STHREE] + op_count[TWO]) * 100 \
                  + (-mine_count[STHREE] - mine_count[TWO]) * 100
            return -res

    def evaluatePoint(self, _board, x, y, mine, opponent, count=None):
        dir_offset = [(1, 0), (0, 1), (1, 1), (1, -1)]  # direction from left to right
        ignore_record = True
        if count is None:
            count = self.count[mine - 1]
            ignore_record = False
        for i in range(4):
            if self.record[x][y][i] == 0 or ignore_record:
                self.analysisLine(_board, x, y, i, dir_offset[i], mine, opponent, count)

    # line is fixed len 9: XXXXMXXXX
    def getLine(self, _board, x, y, dir_offset, mine, opponent):
        line = [0 for i in range(9)]

        tmp_x = x + (-5 * dir_offset[0])
        tmp_y = y + (-5 * dir_offset[1])
        for i in range(9):
            tmp_x += dir_offset[0]
            tmp_y += dir_offset[1]
            if (tmp_x < 0 or tmp_x >= self.len or
                    tmp_y < 0 or tmp_y >= self.len):
                line[i] = opponent  # set out of range as opponent chess
            else:
                line[i] = _board[tmp_x][tmp_y]

        return line

    def analysisLine(self, _board, x, y, dir_index, dir, mine, opponent, count):
        # record line range[left, right] as analysized
        def setRecord(self, x, y, left, right, dir_index, dir_offset):
            tmp_x = x + (-5 + left) * dir_offset[0]
            tmp_y = y + (-5 + left) * dir_offset[1]
            for i in range(left, right + 1):
                tmp_x += dir_offset[0]
                tmp_y += dir_offset[1]
                self.record[tmp_x][tmp_y][dir_index] = 1

        empty = 0
        left_idx, right_idx = 4, 4

        line = self.getLine(_board, x, y, dir, mine, opponent)

        while right_idx < 8:
            if line[right_idx + 1] != mine:
                break
            right_idx += 1
        while left_idx > 0:
            if line[left_idx - 1] != mine:
                break
            left_idx -= 1

        left_range, right_range = left_idx, right_idx
        while right_range < 8:
            if line[right_range + 1] == opponent:
                break
            right_range += 1
        while left_range > 0:
            if line[left_range - 1] == opponent:
                break
            left_range -= 1

        chess_range = right_range - left_range + 1
        if chess_range < 5:
            setRecord(self, x, y, left_range, right_range, dir_index, dir)
            return CHESS_TYPE.NONE

        setRecord(self, x, y, left_idx, right_idx, dir_index, dir)

        m_range = right_idx - left_idx + 1

        # M:mine chess, P:opponent chess or out of range, X: empty
        if m_range >= 5:
            count[FIVE] += 1

        # Live Four : XMMMMX
        # Chong Four : XMMMMP, PMMMMX
        if m_range == 4:
            left_empty = right_empty = False
            if line[left_idx - 1] == empty:
                left_empty = True
            if line[right_idx + 1] == empty:
                right_empty = True
            if left_empty and right_empty:
                count[FOUR] += 1
            elif left_empty or right_empty:
                count[SFOUR] += 1

        # Chong Four : MXMMM, MMMXM, the two types can both exist
        # Live Three : XMMMXX, XXMMMX
        # Sleep Three : PMMMX, XMMMP, PXMMMXP
        if m_range == 3:
            left_empty = right_empty = False
            left_four = right_four = False
            if line[left_idx - 1] == empty:
                if line[left_idx - 2] == mine:  # MXMMM
                    setRecord(self, x, y, left_idx - 2, left_idx - 1, dir_index, dir)
                    count[SFOUR] += 1
                    left_four = True
                left_empty = True

            if line[right_idx + 1] == empty:
                if line[right_idx + 2] == mine:  # MMMXM
                    setRecord(self, x, y, right_idx + 1, right_idx + 2, dir_index, dir)
                    count[SFOUR] += 1
                    right_four = True
                right_empty = True

            if left_four or right_four:
                pass
            elif left_empty and right_empty:
                if chess_range > 5:  # XMMMXX, XXMMMX
                    count[THREE] += 1
                else:  # PXMMMXP
                    count[STHREE] += 1
            elif left_empty or right_empty:  # PMMMX, XMMMP
                count[STHREE] += 1

        # Chong Four: MMXMM, only check right direction
        # Live Three: XMXMMX, XMMXMX the two types can both exist
        # Sleep Three: PMXMMX, XMXMMP, PMMXMX, XMMXMP
        # Live Two: XMMX
        # Sleep Two: PMMX, XMMP
        if m_range == 2:
            left_empty = right_empty = False
            left_three = right_three = False
            if line[left_idx - 1] == empty:
                if line[left_idx - 2] == mine:
                    setRecord(self, x, y, left_idx - 2, left_idx - 1, dir_index, dir)
                    if line[left_idx - 3] == empty:
                        if line[right_idx + 1] == empty:  # XMXMMX
                            count[THREE] += 1
                        else:  # XMXMMP
                            count[STHREE] += 1
                        left_three = True
                    elif line[left_idx - 3] == opponent:  # PMXMMX
                        if line[right_idx + 1] == empty:
                            count[STHREE] += 1
                            left_three = True
                    elif line[left_idx - 3] == mine:     #MMXMM left
                        setRecord(self, x, y, left_idx - 3, left_idx - 2, dir_index, dir)
                        count[SFOUR] += 1

                left_empty = True

            if line[right_idx + 1] == empty:
                if line[right_idx + 2] == mine:
                    if line[right_idx + 3] == mine:  # MMXMM right
                        setRecord(self, x, y, right_idx + 1, right_idx + 2, dir_index, dir)
                        count[SFOUR] += 1
                        right_three = True
                    elif line[right_idx + 3] == empty:
                        setRecord(self, x, y, right_idx + 1, right_idx + 2, dir_index, dir)
                        if left_empty:  # XMMXMX
                            count[THREE] += 1
                        else:  # PMMXMX
                            count[STHREE] += 1
                        right_three = True
                    elif left_empty:  # XMMXMP
                        count[STHREE] += 1
                        right_three = True

                right_empty = True

            if left_three or right_three:
                pass
            elif left_empty and right_empty:  # XMMX
                count[TWO] += 1
            elif left_empty or right_empty:  # PMMX, XMMP
                count[STWO] += 1

        # Live Two: XMXMX, XMXXMX only check right direction
        # Sleep Two: PMXMX, XMXMP
        if m_range == 1:
            left_empty = right_empty = False
            if line[left_idx - 1] == empty:
                if line[left_idx - 2] == mine:
                    if line[left_idx - 3] == empty:
                        if line[right_idx + 1] == opponent:  # XMXMP
                            count[STWO] += 1
                left_empty = True

            if line[right_idx + 1] == empty:
                if line[right_idx + 2] == mine:
                    if line[right_idx + 3] == empty:
                        if left_empty:  # XMXMX
                            # setRecord(self, x, y, left_idx, right_idx+2, dir_index, dir)
                            count[TWO] += 1
                        else:  # PMXMX
                            count[STWO] += 1
                elif line[right_idx + 2] == empty:
                    if line[right_idx + 3] == mine and line[right_idx + 4] == empty:  # XMXXMX
                        count[TWO] += 1

        return CHESS_TYPE.NONE


"""case_2 = [[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
          [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
          [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
          [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
          [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
          [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
          [0, 0, 0, 0, 0, 0, 2, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
          [0, 0, 2, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
          [0, 0, 0, 0, 0, 2, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
          [0, 0, 0, 0, 0, 0, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
          [0, 0, 0, 0, 0, 0, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
          [0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
          [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
          [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
          [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
          [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
          [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
          [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
          [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
          [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]]


agent = niubiAI()"""

# move = agent.Alpha_Beta_Search(state=state)
# print(move)
# t2 = time.clock()
# gpscr = agent.getPointscore(_board=case_2, pos=(8, 14), player=1)
# print(gpscr)
