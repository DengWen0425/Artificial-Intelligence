#  VCX testing
import time
width = 20
height = 20

def Is_win(board, player, move):
    ''' Whether the action taken kill the game?
        input: state, action
        output: an integer(player) denotes who won  '''
    x, y = move
    board[x][y] = player
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
                if x_tmp < 0 or y_tmp < 0 or x_tmp >= 20 or y_tmp >= 20:
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


def getLine(_board, x, y, dir_offset, mine, opponent):
    line = [0 for i in range(9)]
    tmp_x = x + (-5 * dir_offset[0])
    tmp_y = y + (-5 * dir_offset[1])
    for i in range(9):
        tmp_x += dir_offset[0]
        tmp_y += dir_offset[1]
        if (tmp_x < 0 or tmp_x >= 20 or
                tmp_y < 0 or tmp_y >= 20):
            line[i] = opponent  # set out of range as opponent chess
        else:
            line[i] = _board[tmp_x][tmp_y]
    return line


def check_vcx_moves(_board, x, y, mine, opponent):
    dir = [(1, 0), (0, 1), (1, 1), (-1, 1)]
    for i in dir:
        res = one_dir_check(_board, x, y, i, mine, opponent)
        if res > 0:
            return res, i
    return 0, None


def one_dir_check(_board, x, y, dir, mine, opponent):
    empty = 0
    left_idx, right_idx = 4, 4
    line = getLine(_board, x, y, dir, mine, opponent)

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
        return 0
    m_range = right_idx - left_idx + 1

    if m_range >= 5:
        return 5
    # Live Four : XMMMMX
    # Chong Four : XMMMMP, PMMMMX
    if m_range == 4:
        left_empty = right_empty = False
        if line[left_idx - 1] == empty:
            left_empty = True
        if line[right_idx + 1] == empty:
            right_empty = True
        if left_empty and right_empty:
            return 4
        elif left_empty or right_empty:
            return 4

    # Chong Four : MXMMM, MMMXM, the two types can both exist
    # Live Three : XMMMXX, XXMMMX
    if m_range == 3:
        left_empty = right_empty = False
        left_four = right_four = False
        if line[left_idx - 1] == empty:
            if line[left_idx - 2] == mine:  # MXMMM
                return 4
                left_four = True
            left_empty = True

        if line[right_idx + 1] == empty:
            if line[right_idx + 2] == mine:  # MMMXM
                return 4
                right_four = True
            right_empty = True

        if left_four or right_four:
            pass
        elif left_empty and right_empty:
            if chess_range > 5:  # XMMMXX, XXMMMX
                return 3
    # Chong Four: MMXMM, only check right direction
    # Live Three: XMXMMX, XMMXMX the two types can both exist
    if m_range == 2:
        left_empty = right_empty = False
        left_three = right_three = False
        if line[left_idx - 1] == empty:
            if line[left_idx - 2] == mine:
                if line[left_idx - 3] == empty:
                    if line[right_idx + 1] == empty:  # XMXMMX
                        return 3
            left_empty = True

        if line[right_idx + 1] == empty:
            if line[right_idx + 2] == mine:
                if line[right_idx + 3] == mine:  # MMXMM
                    return 4
                    right_three = True
                elif line[right_idx + 3] == empty:
                    if left_empty:  # XMMXMX
                        return 3
            right_empty = True
        if line[left_idx - 1] == empty:
            if line[left_idx - 2] == mine:
                if line[left_idx - 3] == mine:  # MMXMM left dir
                    return 4

    if m_range == 1:
        idx = left_idx
        if line[idx + 1] == empty:
            if line[idx + 2] == mine and line[idx + 3] == mine and line[idx + 4] == mine:
                return 4
            if line[idx - 1] == empty:
                if line[idx + 2] == mine and line[idx + 3] == mine and line[idx + 4] == empty:
                    return 3
        if line[idx - 1] == empty:
            if line[idx - 2] == mine and line[idx - 3] == mine and line[idx - 4] == mine:
                return 4
            if line[idx + 1] == empty:
                if line[idx - 2] == mine and line[idx - 3] == mine and line[idx - 4] == empty:
                    return 3
    return 0


def check_4_5(_board, x, y, mine, opponent):
    empty = 0
    dirs = [(1, 0), (0, 1), (1, 1), (-1, 1)]
    for dire in dirs:
        left_idx, right_idx = 4, 4
        line = getLine(_board, x, y, dire, mine, opponent)
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
            continue
        m_range = right_idx - left_idx + 1

        if m_range >= 5:
            return 5
        if m_range == 4:
            left_empty = right_empty = False
            if line[left_idx - 1] == empty:
                left_empty = True
            if line[right_idx + 1] == empty:
                right_empty = True
            if left_empty and right_empty:
                return 4
    return 0


def get_vcx_moves(_board, player, available_points):
    vcx_list = []
    for point in available_points:
        x, y = point
        score, direc = check_vcx_moves(_board, x, y, player, 3-player)
        if score == 5:                # win
            return [(point, score, direc)]
        if Is_win(_board, 3-player, point):   # have to block
            score = 4.9
        if score > 0:
            if (point, score, direc) not in vcx_list:
                vcx_list.append((point, score, direc))
    return sorted(vcx_list, key=lambda x : x[1], reverse=True)


def get_radius_moves(_board, position, radius):
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


def change_action_list(_board, availables, popped):
    moves = [x for x in availables]
    for move in get_radius_moves(_board, position=popped, radius=2):
        if move not in availables:
            moves.append(move)
    moves.remove(popped)
    return moves


def find_kill(_board, player, available_points, depth):
    start_time = time.time()
    moves_ok = get_vcx_moves(_board, player, available_points)
    if not moves_ok:
        return None

    for depth in range(2, 10, 2):
        for move in moves_ok:
            if (time.time() - start_time) > 5.0:
                return None
            if move[1] > 4:    #win or have to block
                return move[0]
            x, y = move[0]
            _board[x][y] = player
            keep_availables = [x for x in available_points]
            if move[1] == 4:
                availables = Has2blks(_board, move[0], move[2], player=1)
            else:
                availables = change_action_list(_board=_board, availables=available_points, popped=(x, y))
            m = min_kill(_board, move, depth - 1, availables)
            _board[x][y] = 0
            available_points = keep_availables
            if not m:
                continue
            else:
                return move[0]
    return None


def moves_for_min(_board, availables):
    move_list = []
    for move in availables:
        x, y = move
        _board[x][y] = 1
        if check_4_5(_board, x, y, 1, 2):
            move_list.append((x, y))
        _board[x][y] = 2
        if find_s4(_board, move=(x, y), mine=2, opponent=1):
            _board[x][y] = 0
            return []
        _board[x][y] = 0
    return move_list


def Has2blks(_board, pos, dir, player):
    x, y = pos
    dx, dy = dir
    x0, y0 = x-4*dx, y-4*dy
    res = []
    for i in range(9):
        tmpx, tmpy = x0 + i*dx, y0 + i*dy
        if tmpx >= 0 and tmpx < 20 and tmpy >= 0 and tmpy < 20:
            if _board[tmpx][tmpy] == 0:
                _board[tmpx][tmpy] = player
                test = one_dir_check(_board, tmpx, tmpy, dir, player, 3-player)
                _board[tmpx][tmpy] = 0
                if test == 5:
                    res.append((tmpx, tmpy))
    return res


def find_s4(_board, move, mine, opponent):
    x, y = move
    empty = 0
    for dir in [(0, 1), (1, 0), (1, 1), (1, -1)]:
        left_idx, right_idx = 4, 4
        line = getLine(_board, x, y, dir, mine, opponent)
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
            return 0
        m_range = right_idx - left_idx + 1
        if m_range >= 5:
            return 5
        if m_range == 4:
            left_empty = right_empty = False
            if line[left_idx - 1] == empty:
                left_empty = True
            if line[right_idx + 1] == empty:
                right_empty = True
            if left_empty or right_empty:
                return 4
        if m_range == 3:
            if line[left_idx - 1] == empty:
                if line[left_idx - 2] == mine:  # MXMMM
                    return 4
            if line[right_idx + 1] == empty:
                if line[right_idx + 2] == mine:  # MMMXM
                    return 4
        if m_range == 2:
            if line[right_idx + 1] == empty:
                if line[right_idx + 2] == mine:
                    if line[right_idx + 3] == mine:  # MMXMM
                        return 4
            if line[left_idx - 1] == empty:
                if line[left_idx - 2] == mine:
                    if line[left_idx - 3] == mine:  # MMXMM left dir
                        return 4
        if m_range == 1:
            idx = left_idx
            if line[idx + 1] == empty:
                if line[idx + 2] == mine and line[idx + 3] == mine and line[idx + 4] == mine:
                    return 4
            if line[idx - 1] == empty:
                if line[idx - 2] == mine and line[idx - 3] == mine and line[idx - 4] == mine:
                    return 4
    return 0


def min_kill(_board, move, depth, available_points):
    #if Is_win(_board, 1, move=move[0]):
        #return True
    if depth < 0:
        return False
    move_list = []
    if move[1] == 4:
        for pos in available_points:
            if Is_win(_board, 1, pos):
                move_list.append(pos)
    else:
        move_list = moves_for_min(_board, availables=available_points)

    if not move_list:
        return False
    for move in move_list:
        x, y = move
        keep_availables = [x for x in available_points]
        availables = change_action_list(_board=_board, availables=available_points, popped=(x, y))
        _board[x][y] = 2
        m = max_kill(_board, player=1, depth=depth-1, available_points=availables)
        _board[x][y] = 0
        available_points = keep_availables
        if not m:
            return False
    return True


def max_kill(_board, player, depth, available_points):
    if depth < 0:
        return False
    moves_ok = get_vcx_moves(_board, player, available_points)
    if not moves_ok:
        return False

    for move in moves_ok:
        if move[1] == 5:    #win
            return True
        if move[1] == 4.9:  # have to block
            return False
        x, y = move[0]
        keep_availables = [x for x in available_points]
        availables = change_action_list(_board=_board, availables=available_points, popped=(x, y))
        _board[x][y] = player
        m = min_kill(_board, move, depth - 1, availables)
        _board[x][y] = 0
        available_points = keep_availables
        if not m:
            continue
        else:
            return True
    return False







