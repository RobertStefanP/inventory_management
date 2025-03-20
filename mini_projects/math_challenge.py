import random
from re import S
import sys
import time

OPERATORS = ["+", "-", "*"]
MATH_PROBLEMS = 10

def operand():
    return random.randint(3, 12)

def generate_problem():
    left = operand()
    right = operand()
    operator = random.choice(OPERATORS)
    
    problem = str(left) + " " + operator + " " + str(right)
    answer = eval(problem)    
    return problem, answer

while True:    
    end_round = False    
    wrong = 0
    
    while not end_round:        
        print("------------------------")
        press = input("Press s to start or q to quit: ").lower()  
        if press == 's':
            start_time = time.time()            
            for i in range(MATH_PROBLEMS): 
                problem, answer = generate_problem() 
                              
                while True:
                    guess = input("Problem #" + str(i + 1) + ": " + problem + " = ")
                    if guess == str(answer):
                        break               
                    else:
                        wrong += 1
                        print(f"You have {wrong} error(s), {3 - wrong} left!")                                    
                    if wrong == 3:
                        end_round = True
                        print("Go learn math. The game ended!")
                        break                                
                if end_round:
                    break                
            if wrong != 3:    
                end_time = time.time()                      
                total_time = round(end_time - start_time, 2)    
                print("------------------------")
                print(f"Good job, you finished in {total_time} seconds.")                                                                                               
        elif press == 'q':
            print("Exiting game!")
            sys.exit()            
        else:
            print("Error! Try again pressing 's' or 'q'.")  


         