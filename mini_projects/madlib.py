with open("story.txt", "r") as f:
    story = f.read() # read the file in f and store it in the variable story

words = set()
start_of_word = -1
target_start = "<"
target_end = ">"

for i, char in enumerate(story):
    if char == target_start: 
        start_of_word = i # Store the position of `<`
        
    if char == target_end and start_of_word != -1:
        word = story[start_of_word: i + 1] # EX: story[13:24] → "<adjective>"
        words.add(word) # Add "<adjective>" to the set
        start_of_word = -1 # Reset

answers = {}
    
for word in words:
    answer = input("Enter a word for " + word + ": ")
    answers[word] = answer

for word in words:
    story = story.replace(word, answers[word])
    
print(story)