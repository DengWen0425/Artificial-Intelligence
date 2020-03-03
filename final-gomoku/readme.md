# Gomoku AI
This project was done by me and my parter Hongou Liu.

## Description
We have designed three versions of agents in this project by using Monte Carlo Tree Search and Minimax Search with Alpha-Beta pruning.

* MCTS
In MCTS, the naive algorithm works badly in playing gomoku, and there is little improvement after we optimized it several times, so we only
keeps a base version.

* Minimax
  A lot of effort was put into this algorithm by us. And it turned out that our agent had achieved good results. It got the highest score 
  in the class.
  <br>
  We mainly optimized the algorithm in the following aspects:
  * Alpha-beta Pruning
  * Ordering
  * More reasonable heuristic function
  * Design a dynamic board and evaluation method.
  * VCX
  <br>
  Check the code or documentation or report files for detailed information.
