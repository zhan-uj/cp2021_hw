# coding: utf-8
# https://github.com/GlobalCooling/snake-BFS
import pygame,sys,time,random
from pygame.locals import *
# 定義顏色變量
redColour = pygame.Color(255,0,0)
blackColour = pygame.Color(0,0,0)
whiteColour = pygame.Color(255,255,255)
greenColour = pygame.Color(0,255,0)
headColour = pygame.Color(0,119,255)

#注意：在下面所有的除法中，為了防止pygame輸出偏差，必須取除數(//)而不是單純除法(/)

# 蛇運動的場地長寬，因為第0行，HEIGHT行，第0列，WIDTH列為圍牆，所以實際是13*13
HEIGHT = 15
WIDTH = 15
FIELD_SIZE = HEIGHT * WIDTH
# 蛇頭位於snake數組的第一個元素
HEAD = 0

# 用數字代表不同的對象，由於運動時矩陣上每個格子會處理成到達食物的路徑長度，
# 因此這三個變量間需要有足夠大的間隔(>HEIGHT*WIDTH)來互相區分
# 小寫一般是坐標，大寫代表常量
FOOD = 0
UNDEFINED = (HEIGHT + 1) * (WIDTH + 1)
SNAKE = 2 * UNDEFINED

# 由於snake是一維數組，所以對應元素直接加上以下值就表示向四個方向移動
LEFT = -1
RIGHT = 1
UP = -WIDTH#一維數組，所以需要整個寬度都加上才能表示上下移動
DOWN = WIDTH 

# 錯誤碼
ERR = -2333

# 用一維數組來表示二維的東西
# board表示蛇運動的矩形場地
# 初始化蛇頭在(1,1)的地方
# 初始蛇長度為1
board = [0] * FIELD_SIZE #[0,0,0,……]
snake = [0] * (FIELD_SIZE+1)
snake[HEAD] = 1*WIDTH+1
snake_size = 1
# 與上面變量對應的臨時變量，蛇試探性地移動時使用
tmpboard = [0] * FIELD_SIZE
tmpsnake = [0] * (FIELD_SIZE+1)
tmpsnake[HEAD] = 1*WIDTH+1
tmpsnake_size = 1

# food:食物位置初始在(4, 7)
# best_move: 運動方向
food = 4 * WIDTH + 7
best_move = ERR

# 運動方向數組，游戲分數(蛇長)
mov = [LEFT, RIGHT, UP, DOWN]                                           
score = 1 

# 檢查一個cell有沒有被蛇身覆蓋，沒有覆蓋則為free，返回true
def is_cell_free(idx, psize, psnake):
    return not (idx in psnake[:psize]) 

# 檢查某個位置idx是否可向move方向運動
def is_move_possible(idx, move):
    flag = False
    if move == LEFT:
        #因為實際范圍是13*13,[1,13]*[1,13],所以idx為1時不能往左跑，此時取餘為1所以>1
        flag = True if idx%WIDTH > 1 else False
    elif move == RIGHT:
        #這裡的<WIDTH-2跟上面是一樣的道理
        flag = True if idx%WIDTH < (WIDTH-2) else False
    elif move == UP:
        #這裡向上的判斷畫圖很好理解，因為在[1,13]*[1,13]的實際運動范圍外，還有個
        #大框是圍牆，就是之前說的那幾個行列，下面判斷向下運動的條件也是類似的
        flag = True if idx > (2*WIDTH-1) else False
    elif move == DOWN:
        flag = True if idx < (FIELD_SIZE-2*WIDTH) else False
    return flag
# 重置board
# board_BFS後，UNDEFINED值都變為了到達食物的路徑長度
# 如需要還原，則要重置它
def board_reset(psnake, psize, pboard):
    for i in range(FIELD_SIZE):
        if i == food:
            pboard[i] = FOOD
        elif is_cell_free(i, psize, psnake): # 該位置為空
            pboard[i] = UNDEFINED
        else: # 該位置為蛇身
            pboard[i] = SNAKE
    
# 廣度優先搜索遍歷整個board，
# 計算出board中每個非SNAKE元素到達食物的路徑長度
def board_BFS(pfood, psnake, pboard):
    queue = []
    queue.append(pfood)
    inqueue = [0] * FIELD_SIZE
    found = False
    # while循環結束後，除了蛇的身體，
    # 其它每個方格中的數字為從它到食物的曼哈頓間距
    while len(queue)!=0: 
        idx = queue.pop(0)#初始時idx是食物的坐標 
        if inqueue[idx] == 1: continue
        inqueue[idx] = 1
        for i in range(4):#左右上下
            if is_move_possible(idx, mov[i]):
                if idx + mov[i] == psnake[HEAD]:
                    found = True
                if pboard[idx+mov[i]] < SNAKE: # 如果該點不是蛇的身體
                    if pboard[idx+mov[i]] > pboard[idx]+1:#小於的時候不管，不然會覆蓋已有的路徑數據
                        pboard[idx+mov[i]] = pboard[idx] + 1
                    if inqueue[idx+mov[i]] == 0:
                        queue.append(idx+mov[i])
    return found

# 從蛇頭開始，根據board中元素值，
# 從蛇頭周圍4個領域點中選擇最短路徑
def choose_shortest_safe_move(psnake, pboard):
    best_move = ERR
    min = SNAKE
    for i in range(4):
        if is_move_possible(psnake[HEAD], mov[i]) and pboard[psnake[HEAD]+mov[i]]<min:
        	#這裡判斷最小和下面的函數判斷最大，都是先賦值，再循環互相比較
            min = pboard[psnake[HEAD]+mov[i]]
            best_move = mov[i]
    return best_move

# 從蛇頭開始，根據board中元素值，
# 從蛇頭周圍4個領域點中選擇最遠路徑
def choose_longest_safe_move(psnake, pboard):
    best_move = ERR
    max = -1
    for i in range(4):
        if is_move_possible(psnake[HEAD], mov[i]) and pboard[psnake[HEAD]+mov[i]]<UNDEFINED and pboard[psnake[HEAD]+mov[i]]>max:
            max = pboard[psnake[HEAD]+mov[i]]
            best_move = mov[i]
    return best_move

# 檢查是否可以追著蛇尾運動，即蛇頭和蛇尾間是有路徑的
# 為的是避免蛇頭陷入死路
# 虛擬操作，在tmpboard,tmpsnake中進行
def is_tail_inside():
    global tmpboard, tmpsnake, food, tmpsnake_size
    tmpboard[tmpsnake[tmpsnake_size-1]] = 0 # 虛擬地將蛇尾變為食物(因為是虛擬的，所以在tmpsnake,tmpboard中進行)
    tmpboard[food] = SNAKE # 放置食物的地方，看成蛇身
    result = board_BFS(tmpsnake[tmpsnake_size-1], tmpsnake, tmpboard) # 求得每個位置到蛇尾的路徑長度
    for i in range(4): # 如果蛇頭和蛇尾緊挨著，則返回False。即不能follow_tail，追著蛇尾運動了
        if is_move_possible(tmpsnake[HEAD], mov[i]) and tmpsnake[HEAD]+mov[i]==tmpsnake[tmpsnake_size-1] and tmpsnake_size>3:
            result = False
    return result

# 讓蛇頭朝著蛇尾運行一步
# 不管蛇身阻擋，朝蛇尾方向運行
def follow_tail():
    global tmpboard, tmpsnake, food, tmpsnake_size
    tmpsnake_size = snake_size
    tmpsnake = snake[:]
    board_reset(tmpsnake, tmpsnake_size, tmpboard) # 重置虛擬board
    tmpboard[tmpsnake[tmpsnake_size-1]] = FOOD # 讓蛇尾成為食物
    tmpboard[food] = SNAKE # 讓食物的地方變成蛇身
    board_BFS(tmpsnake[tmpsnake_size-1], tmpsnake, tmpboard) # 求得各個位置到達蛇尾的路徑長度
    tmpboard[tmpsnake[tmpsnake_size-1]] = SNAKE # 還原蛇尾
    return choose_longest_safe_move(tmpsnake, tmpboard) # 返回運行方向(讓蛇頭運動1步)

# 在各種方案都不行時，隨便找一個可行的方向來走(1步),
def any_possible_move():
    global food , snake, snake_size, board
    best_move = ERR
    board_reset(snake, snake_size, board)
    board_BFS(food, snake, board)
    min = SNAKE

    for i in range(4):
        if is_move_possible(snake[HEAD], mov[i]) and board[snake[HEAD]+mov[i]]<min:
            min = board[snake[HEAD]+mov[i]]
            best_move = mov[i]
    return best_move
    
#轉換數組函數
def shift_array(arr, size):
    for i in range(size, 0, -1):
        arr[i] = arr[i-1]

def new_food():#隨機函數生成新的食物
    global food, snake_size
    cell_free = False
    while not cell_free:
        w = random.randint(1, WIDTH-2)
        h = random.randint(1, HEIGHT-2)
        food = WIDTH*h + w
        cell_free = is_cell_free(food, snake_size, snake)
    pygame.draw.rect(playSurface,redColour,Rect(18*(food//WIDTH), 18*(food%WIDTH),18,18))

# 真正的蛇在這個函數中，朝pbest_move走1步
def make_move(pbest_move):
    global snake, board, snake_size, score
    shift_array(snake, snake_size)
    snake[HEAD] += pbest_move
    p = snake[HEAD]
    for body in snake:#畫蛇，身體，頭，尾
    	pygame.draw.rect(playSurface,whiteColour,Rect(18*(body//WIDTH), 18*(body%WIDTH),18,18))
    pygame.draw.rect(playSurface,greenColour,Rect(18*(snake[snake_size-1]//WIDTH),18*(snake[snake_size-1]%WIDTH),18,18))
    pygame.draw.rect(playSurface,headColour,Rect(18*(p//WIDTH), 18*(p%WIDTH),18,18))
    #下面一行是把初始情況會出現的第一個白塊bug填掉
    pygame.draw.rect(playSurface,(255,255,0),Rect(0,0,18,18))
    # 刷新pygame顯示層
    pygame.display.flip() 
    
    # 如果新加入的蛇頭就是食物的位置
    # 蛇長加1，產生新的食物，重置board(因為原來那些路徑長度已經用不上了)
    if snake[HEAD] == food:
        board[snake[HEAD]] = SNAKE # 新的蛇頭
        snake_size += 1
        score += 1
        if snake_size < FIELD_SIZE: new_food()
    else: # 如果新加入的蛇頭不是食物的位置
        board[snake[HEAD]] = SNAKE # 新的蛇頭
        board[snake[snake_size]] = UNDEFINED # 蛇尾變為UNDEFINED，黑色
        pygame.draw.rect(playSurface,blackColour,Rect(18*(snake[snake_size]//WIDTH),18*(snake[snake_size]%WIDTH),18,18))
        # 刷新pygame顯示層
        pygame.display.flip() 

# 虛擬地運行一次，然後在調用處檢查這次運行可否可行
# 可行才真實運行。
# 虛擬運行吃到食物後，得到虛擬下蛇在board的位置
def virtual_shortest_move():
    global snake, board, snake_size, tmpsnake, tmpboard, tmpsnake_size, food
    tmpsnake_size = snake_size
    tmpsnake = snake[:] # 如果直接tmpsnake=snake，則兩者指向同一處內存
    tmpboard = board[:] # board中已經是各位置到達食物的路徑長度了，不用再計算
    board_reset(tmpsnake, tmpsnake_size, tmpboard)
    
    food_eated = False
    while not food_eated:
        board_BFS(food, tmpsnake, tmpboard)    
        move = choose_shortest_safe_move(tmpsnake, tmpboard)
        shift_array(tmpsnake, tmpsnake_size)
        tmpsnake[HEAD] += move # 在蛇頭前加入一個新的位置
        # 如果新加入的蛇頭的位置正好是食物的位置
        # 則長度加1，重置board，食物那個位置變為蛇的一部分(SNAKE)
        if tmpsnake[HEAD] == food:
            tmpsnake_size += 1
            board_reset(tmpsnake, tmpsnake_size, tmpboard) # 虛擬運行後，蛇在board的位置
            tmpboard[food] = SNAKE
            food_eated = True
        else: # 如果蛇頭不是食物的位置，則新加入的位置為蛇頭，最後一個變為空格
            tmpboard[tmpsnake[HEAD]] = SNAKE
            tmpboard[tmpsnake[tmpsnake_size]] = UNDEFINED

# 如果蛇與食物間有路徑，則調用本函數
def find_safe_way():
    global snake, board
    safe_move = ERR
    # 虛擬地運行一次，因為已經確保蛇與食物間有路徑，所以執行有效
    # 運行後得到虛擬下蛇在board中的位置，即tmpboard
    virtual_shortest_move() # 該函數唯一調用處
    if is_tail_inside(): # 如果虛擬運行後，蛇頭蛇尾間有通路，則選最短路運行(1步)
        return choose_shortest_safe_move(snake, board)
    safe_move = follow_tail() # 否則虛擬地follow_tail 1步，如果可以做到，返回true
    return safe_move


#初始化pygame
pygame.init()
#定義一個變量用來控制游戲速度
fpsClock = pygame.time.Clock()
# 創建pygame顯示層
playSurface = pygame.display.set_mode((270,270))
pygame.display.set_caption('貪吃蛇')
# 繪制pygame顯示層
playSurface.fill(blackColour)
#初始化食物
pygame.draw.rect(playSurface,redColour,Rect(18*(food//WIDTH), 18*(food%WIDTH),18,18))

while True:
    for event in pygame.event.get():#循環監聽鍵盤和退出事件
        if event.type == QUIT:#如果點了關閉
            print(score)#游戲結束後打印分數
            pygame.quit()
            sys.exit()
        elif event.type == KEYDOWN:#如果esc鍵被按下
            if event.key==K_ESCAPE:
                print(score)#游戲結束後打印分數
                pygame.quit()
                sys.exit()
    # 刷新pygame顯示層
    pygame.display.flip()  
    #畫圍牆，255,255,0是黃色，邊框是36是因為，pygame矩形是以邊為初始，向四周填充邊框
    pygame.draw.rect(playSurface,(255,255,0),Rect(0,0,270,270),36)
    # 重置距離
    board_reset(snake, snake_size, board)
    # 如果蛇可以吃到食物，board_BFS返回true
    # 並且board中除了蛇身(=SNAKE)，其它的元素值表示從該點運動到食物的最短路徑長
    if board_BFS(food, snake, board):
        best_move  = find_safe_way() # find_safe_way的唯一調用處
    else:
        best_move = follow_tail()
    if best_move == ERR:
        best_move = any_possible_move()
    # 上面一次思考，只得出一個方向，運行一步
    if best_move != ERR: make_move(best_move)
    else:
        print(score)#游戲結束後打印分數
        break
    # 控制游戲速度
    fpsClock.tick(20)#20看上去速度正好