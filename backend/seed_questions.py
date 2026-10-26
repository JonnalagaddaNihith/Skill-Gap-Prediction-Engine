import sys
from pathlib import Path

# Add the parent directory to path to import app modules
sys.path.append(str(Path(__file__).parent))

from sqlalchemy.orm import Session
from app.db.database import engine, SessionLocal, Base
from app.models.question import Question
from app.models.user import User
from app.services.auth import get_password_hash

# Skill definitions from catalog
SKILLS = {
    "SK001": "Python Basics",
    "SK002": "Python Loops",
    "SK003": "Functions",
    "SK004": "Data Structures",
    "SK005": "SQL Queries",
    "SK006": "SQL Joins",
    "SK007": "Debugging",
    "SK008": "Algorithms"
}

DIFFICULTIES = ["Easy", "Medium", "Hard"]
PROBLEM_TYPES = ["Multiple Choice", "Conceptual", "Coding", "Debugging"]

# Skill to Course mapping
SKILL_TO_COURSE = {
    "SK001": "COURSE_PY",  # Python Basics
    "SK002": "COURSE_PY",  # Python Loops
    "SK003": "COURSE_PY",  # Functions
    "SK004": "COURSE_DS",  # Data Structures
    "SK005": "COURSE_SQL", # SQL Queries
    "SK006": "COURSE_SQL", # SQL Joins
    "SK007": "COURSE_CS",  # Debugging
    "SK008": "COURSE_ALGO" # Algorithms
}

# Sample questions database - 10 questions per skill (80 total)
SAMPLE_QUESTIONS = [
    # ========== Python Basics (SK001) - 10 questions ==========
    {
        "skill_id": "SK001",
        "skill_name": "Python Basics",
        "difficulty": "Easy",
        "problem_type": "Multiple Choice",
        "question_text": "What is the correct way to create a variable in Python?",
        "options": '["var x = 5", "int x = 5", "x = 5", "declare x = 5"]',
        "correct_answer": "x = 5",
        "explanation": "In Python, variables are created by simply assigning a value using the = operator.",
        "hints": "Python doesn't require type declarations or keywords like 'var'. Just use the variable name, equals sign, and value.",
        "course_id": SKILL_TO_COURSE["SK001"]
    },
    {
        "skill_id": "SK001",
        "skill_name": "Python Basics",
        "difficulty": "Easy",
        "problem_type": "Coding",
        "question_text": "Write a Python statement to print 'Hello, World!'",
        "options": None,
        "correct_answer": "print('Hello, World!')",
        "explanation": "The print() function is used to output text in Python.",
        "hints": "Use the print() function with the string in quotes. Remember the parentheses!",
        "course_id": SKILL_TO_COURSE["SK001"]
    },
    {
        "skill_id": "SK001",
        "skill_name": "Python Basics",
        "difficulty": "Easy",
        "problem_type": "Multiple Choice",
        "question_text": "Which of the following is a valid Python variable name?",
        "options": '["2var", "var-name", "var_name", "class"]',
        "correct_answer": "var_name",
        "explanation": "Variable names must start with a letter or underscore, not a number or hyphen. 'class' is a reserved keyword.",
        "hints": "Variable names can't start with numbers or contain hyphens. Also, avoid Python keywords like 'class', 'def', 'if'.",
        "course_id": SKILL_TO_COURSE["SK001"]
    },
    {
        "skill_id": "SK001",
        "skill_name": "Python Basics",
        "difficulty": "Easy",
        "problem_type": "Coding",
        "question_text": "Assign the value 42 to a variable named 'answer'",
        "options": None,
        "correct_answer": "answer = 42",
        "explanation": "Variable assignment in Python uses the = operator with the variable name on the left and value on the right.",
        "hints": "Use the assignment operator =. The variable name goes on the left, the value on the right.",
        "course_id": SKILL_TO_COURSE["SK001"]
    },
    {
        "skill_id": "SK001",
        "skill_name": "Python Basics",
        "difficulty": "Medium",
        "problem_type": "Conceptual",
        "question_text": "What is the difference between list and tuple in Python?",
        "options": '["Lists are mutable, tuples are immutable", "Tuples are mutable, lists are immutable", "Both are mutable", "Both are immutable"]',
        "correct_answer": "Lists are mutable, tuples are immutable",
        "explanation": "Lists can be modified after creation (mutable), while tuples cannot be changed (immutable).",
        "hints": "Mutable means you can change it after creation (add, remove, modify). Immutable means once created, it cannot be changed.",
        "course_id": SKILL_TO_COURSE["SK001"]
    },
    {
        "skill_id": "SK001",
        "skill_name": "Python Basics",
        "difficulty": "Medium",
        "problem_type": "Multiple Choice",
        "question_text": "What is the output of: print(type(3.14))?",
        "options": "[\"<class 'int'>\", \"<class 'float'>\", \"<class 'str'>\", \"<class 'double'>\"]",
        "correct_answer": "<class 'float'>",
        "explanation": "3.14 is a floating-point number, so its type is float.",
        "hints": "Numbers with decimal points are floats. Whole numbers are integers. The type() function returns the data type.",
        "course_id": SKILL_TO_COURSE["SK001"]
    },
    {
        "skill_id": "SK001",
        "skill_name": "Python Basics",
        "difficulty": "Medium",
        "problem_type": "Coding",
        "question_text": "Convert the string '123' to an integer",
        "options": None,
        "correct_answer": "int('123')",
        "explanation": "The int() function converts a string to an integer if it contains a valid number.",
        "hints": "Use the int() constructor function to convert strings to integers, provided the string contains a valid number.",
        "course_id": SKILL_TO_COURSE["SK001"]
    },
    {
        "skill_id": "SK001",
        "skill_name": "Python Basics",
        "difficulty": "Medium",
        "problem_type": "Debugging",
        "question_text": "What is wrong with this code: x = 5; print X",
        "options": '["Variable X is not defined", "Missing parentheses", "Wrong case for variable", "Nothing is wrong"]',
        "correct_answer": "Wrong case for variable",
        "explanation": "Python is case-sensitive. The variable is 'x' (lowercase) but the code tries to print 'X' (uppercase).",
        "hints": "Python is case-sensitive. 'x' and 'X' are different variables. Check the exact spelling and case of your variable names.",
        "course_id": SKILL_TO_COURSE["SK001"]
    },
    {
        "skill_id": "SK001",
        "skill_name": "Python Basics",
        "difficulty": "Hard",
        "problem_type": "Coding",
        "question_text": "Write code to swap two variables a and b without using a third variable",
        "options": None,
        "correct_answer": "a, b = b, a",
        "explanation": "Python supports tuple unpacking, allowing variable swap in a single line without a temporary variable.",
        "hints": "Python allows multiple assignment in one line using tuple unpacking: a, b = b, a swaps them directly.",
        "course_id": SKILL_TO_COURSE["SK001"]
    },
    {
        "skill_id": "SK001",
        "skill_name": "Python Basics",
        "difficulty": "Hard",
        "problem_type": "Conceptual",
        "question_text": "What will be the output of: a = [1, 2, 3]; b = a; b[0] = 99; print(a[0])?",
        "options": '["1", "99", "Error", "None"]',
        "correct_answer": "99",
        "explanation": "Lists are mutable and b = a creates a reference, not a copy. Changing b also changes a.",
        "hints": "When you assign b = a, you're creating a reference to the same list object, not a copy. Changes to b affect a too.",
        "course_id": SKILL_TO_COURSE["SK001"]
    },

    # ========== Python Loops (SK002) - 10 questions ==========
    {
        "skill_id": "SK002",
        "skill_name": "Python Loops",
        "difficulty": "Easy",
        "problem_type": "Multiple Choice",
        "question_text": "Which loop is used to iterate over a sequence in Python?",
        "options": '["while loop", "for loop", "do-while loop", "foreach loop"]',
        "correct_answer": "for loop",
        "explanation": "The for loop is used to iterate over sequences like lists, tuples, strings, etc.",
        "hints": "The for loop is specifically designed to iterate over sequences (lists, strings, tuples, etc.). Python doesn't have a do-while loop.",
        "course_id": SKILL_TO_COURSE["SK002"]
    },
    {
        "skill_id": "SK002",
        "skill_name": "Python Loops",
        "difficulty": "Easy",
        "problem_type": "Coding",
        "question_text": "Write a for loop to print numbers from 1 to 5",
        "options": None,
        "correct_answer": "for i in range(1, 6): print(i)",
        "explanation": "range(1, 6) generates numbers from 1 to 5 (exclusive of 6).",
        "hints": "Use range(start, stop) where stop is exclusive. So range(1, 6) gives 1, 2, 3, 4, 5.",
        "course_id": SKILL_TO_COURSE["SK002"]
    },
    {
        "skill_id": "SK002",
        "skill_name": "Python Loops",
        "difficulty": "Easy",
        "problem_type": "Multiple Choice",
        "question_text": "What does range(5) produce?",
        "options": '["[0, 1, 2, 3, 4, 5]", "[0, 1, 2, 3, 4]", "[1, 2, 3, 4, 5]", "[5]"]',
        "correct_answer": "[0, 1, 2, 3, 4]",
        "explanation": "range(5) generates numbers from 0 to 4 (5 is exclusive).",
        "hints": "range(n) produces numbers from 0 to n-1. The stop value is never included in the result.",
        "course_id": SKILL_TO_COURSE["SK002"]
    },
    {
        "skill_id": "SK002",
        "skill_name": "Python Loops",
        "difficulty": "Easy",
        "problem_type": "Coding",
        "question_text": "Write a while loop that prints 'Hello' 3 times",
        "options": None,
        "correct_answer": "count = 0; while count < 3: print('Hello'); count += 1",
        "explanation": "The while loop continues as long as the condition is true. We increment a counter to exit.",
        "hints": "Initialize a counter, check condition at start, increment counter inside loop to avoid infinite loop.",
        "course_id": SKILL_TO_COURSE["SK002"]
    },
    {
        "skill_id": "SK002",
        "skill_name": "Python Loops",
        "difficulty": "Medium",
        "problem_type": "Coding",
        "question_text": "Write a for loop to iterate over a list ['a', 'b', 'c'] and print each element",
        "options": None,
        "correct_answer": "for item in ['a', 'b', 'c']: print(item)",
        "explanation": "The for loop can directly iterate over lists without using indices.",
        "hints": "Use 'for item in list:' syntax. Python handles iteration automatically, no need for indices.",
        "course_id": SKILL_TO_COURSE["SK002"]
    },
    {
        "skill_id": "SK002",
        "skill_name": "Python Loops",
        "difficulty": "Medium",
        "problem_type": "Conceptual",
        "question_text": "What is the purpose of the 'break' statement in a loop?",
        "options": '["Skip the current iteration", "Exit the loop immediately", "Continue to next iteration", "Restart the loop"]',
        "correct_answer": "Exit the loop immediately",
        "explanation": "The break statement terminates the loop and transfers control to the statement after the loop.",
        "hints": "break stops the loop entirely and exits it. It doesn't just skip one iteration.",
        "course_id": SKILL_TO_COURSE["SK002"]
    },
    {
        "skill_id": "SK002",
        "skill_name": "Python Loops",
        "difficulty": "Medium",
        "problem_type": "Multiple Choice",
        "question_text": "What does 'continue' do in a loop?",
        "options": '["Exits the loop", "Skips the rest of the current iteration", "Restarts the loop", "Pauses execution"]',
        "correct_answer": "Skips the rest of the current iteration",
        "explanation": "continue skips the remaining code in the current iteration and moves to the next iteration.",
        "hints": "continue skips to the next iteration but doesn't exit the loop. break exits the loop completely.",
        "course_id": SKILL_TO_COURSE["SK002"]
    },
    {
        "skill_id": "SK002",
        "skill_name": "Python Loops",
        "difficulty": "Medium",
        "problem_type": "Debugging",
        "question_text": "What is wrong with: for i in range(5): print(i); if i == 3: break",
        "options": '["Nothing is wrong", "Should use while loop", "Indentation error", "break only works in while"]',
        "correct_answer": "Nothing is wrong",
        "explanation": "This code is correct. It will print 0, 1, 2, 3 and then break out of the loop.",
        "hints": "There's nothing wrong with this code. break works in both for and while loops in Python.",
        "course_id": SKILL_TO_COURSE["SK002"]
    },
    {
        "skill_id": "SK002",
        "skill_name": "Python Loops",
        "difficulty": "Hard",
        "problem_type": "Coding",
        "question_text": "Write nested loops to print a 3x3 multiplication table",
        "options": None,
        "correct_answer": "for i in range(1, 4): for j in range(1, 4): print(i * j, end=' '); print()",
        "explanation": "Nested loops use one loop inside another. The inner loop runs completely for each iteration of the outer loop.",
        "hints": "Place one for loop inside another. The inner loop completes all iterations for each outer loop iteration.",
        "course_id": SKILL_TO_COURSE["SK002"]
    },
    {
        "skill_id": "SK002",
        "skill_name": "Python Loops",
        "difficulty": "Hard",
        "problem_type": "Conceptual",
        "question_text": "What is the output of: for i in range(3): print(i, end=' ')",
        "options": '["0 1 2", "1 2 3", "0 1 2 ", "1 2 3 "]',
        "correct_answer": "0 1 2 ",
        "explanation": "range(3) gives 0, 1, 2. end=' ' prevents newline, so output is '0 1 2 ' with trailing space.",
        "hints": "range(3) = 0,1,2. end=' ' adds space instead of newline. So output: '0 1 2 ' (with trailing space).",
        "course_id": SKILL_TO_COURSE["SK002"]
    },

    # ========== Functions (SK003) - 10 questions ==========
    {
        "skill_id": "SK003",
        "skill_name": "Functions",
        "difficulty": "Easy",
        "problem_type": "Multiple Choice",
        "question_text": "What keyword is used to define a function in Python?",
        "options": '["function", "def", "func", "define"]',
        "correct_answer": "def",
        "explanation": "The 'def' keyword is used to define a function in Python.",
        "hints": "Python uses 'def' (short for define) to create functions, not 'function' or other keywords.",
        "course_id": SKILL_TO_COURSE["SK003"]
    },
    {
        "skill_id": "SK003",
        "skill_name": "Functions",
        "difficulty": "Easy",
        "problem_type": "Coding",
        "question_text": "Write a function that takes two numbers and returns their sum",
        "options": None,
        "correct_answer": "def add(a, b): return a + b",
        "explanation": "Functions are defined using def and can return values using the return statement.",
        "hints": "Use def function_name(parameters): and return the result. Remember the colon and indentation.",
        "course_id": SKILL_TO_COURSE["SK003"]
    },
    {
        "skill_id": "SK003",
        "skill_name": "Functions",
        "difficulty": "Easy",
        "problem_type": "Multiple Choice",
        "question_text": "How do you call a function named 'greet' with argument 'John'?",
        "options": "[\"greet('John')\", \"call greet('John')\", \"greet John\", \"greet[John]\"]",
        "correct_answer": "greet('John')",
        "explanation": "Functions are called by name followed by parentheses containing the arguments.",
        "hints": "Call functions by name with parentheses: function_name(argument). No 'call' keyword needed.",
        "course_id": SKILL_TO_COURSE["SK003"]
    },
    {
        "skill_id": "SK003",
        "skill_name": "Functions",
        "difficulty": "Easy",
        "problem_type": "Coding",
        "question_text": "Write a function that returns True if a number is even",
        "options": None,
        "correct_answer": "def is_even(n): return n % 2 == 0",
        "explanation": "The modulo operator % returns the remainder. If remainder is 0, the number is even.",
        "hints": "Use the modulo operator % to check if remainder is 0 when divided by 2. n % 2 == 0 means even.",
        "course_id": SKILL_TO_COURSE["SK003"]
    },
    {
        "skill_id": "SK003",
        "skill_name": "Functions",
        "difficulty": "Medium",
        "problem_type": "Conceptual",
        "question_text": "What is a default parameter in a function?",
        "options": '["A parameter that must be provided", "A parameter with a predefined value", "A parameter that returns nothing", "A parameter that is optional only in Python 3"]',
        "correct_answer": "A parameter with a predefined value",
        "explanation": "Default parameters have predefined values and can be omitted when calling the function.",
        "hints": "Default parameters have values like def func(x=5):. If you don't provide x, it uses 5 automatically.",
        "course_id": SKILL_TO_COURSE["SK003"]
    },
    {
        "skill_id": "SK003",
        "skill_name": "Functions",
        "difficulty": "Medium",
        "problem_type": "Coding",
        "question_text": "Write a function with a default parameter: def greet(name='World')",
        "options": None,
        "correct_answer": "def greet(name='World'): return f'Hello, {name}!'",
        "explanation": "Default parameters are assigned in the function definition using = operator.",
        "hints": "Set default value in parameter: def func(param='default'):. Use f-strings for formatting.",
        "course_id": SKILL_TO_COURSE["SK003"]
    },
    {
        "skill_id": "SK003",
        "skill_name": "Functions",
        "difficulty": "Medium",
        "problem_type": "Multiple Choice",
        "question_text": "What does *args allow in a function?",
        "options": '["Keyword arguments", "Variable number of positional arguments", "Fixed number of arguments", "Return multiple values"]',
        "correct_answer": "Variable number of positional arguments",
        "explanation": "*args allows a function to accept any number of positional arguments as a tuple.",
        "hints": "*args collects any number of positional arguments into a tuple. **kwargs collects keyword arguments.",
        "course_id": SKILL_TO_COURSE["SK003"]
    },
    {
        "skill_id": "SK003",
        "skill_name": "Functions",
        "difficulty": "Medium",
        "problem_type": "Debugging",
        "question_text": "What is wrong with: def square(x): return x * x; print(square)",
        "options": '["Function not called with argument", "Missing return", "Wrong function name", "Nothing is wrong"]',
        "correct_answer": "Function not called with argument",
        "explanation": "The function square requires an argument x. Calling square() without argument raises TypeError.",
        "hints": "The function expects a parameter x. Call it with an argument: square(5) for example.",
        "course_id": SKILL_TO_COURSE["SK003"]
    },
    {
        "skill_id": "SK003",
        "skill_name": "Functions",
        "difficulty": "Hard",
        "problem_type": "Coding",
        "question_text": "Write a function that accepts *args and returns their sum",
        "options": None,
        "correct_answer": "def sum_all(*args): return sum(args)",
        "explanation": "*args collects all positional arguments into a tuple, which can then be processed.",
        "hints": "Use *args in parameter to accept any number of arguments. Then use sum() built-in function.",
        "course_id": SKILL_TO_COURSE["SK003"]
    },
    {
        "skill_id": "SK003",
        "skill_name": "Functions",
        "difficulty": "Hard",
        "problem_type": "Conceptual",
        "question_text": "What is the difference between local and global variables?",
        "options": '["Local variables are faster", "Global variables exist inside functions", "Local variables are function-scoped, global are module-scoped", "No difference"]',
        "correct_answer": "Local variables are function-scoped, global are module-scoped",
        "explanation": "Local variables are defined inside functions and only accessible there. Global variables are accessible throughout the module.",
        "hints": "Local variables only exist inside the function where they're defined. Global variables are accessible anywhere in the module.",
        "course_id": SKILL_TO_COURSE["SK003"]
    },

    # ========== Data Structures (SK004) - 10 questions ==========
    {
        "skill_id": "SK004",
        "skill_name": "Data Structures",
        "difficulty": "Easy",
        "problem_type": "Multiple Choice",
        "question_text": "Which data structure uses key-value pairs?",
        "options": '["List", "Tuple", "Dictionary", "Set"]',
        "correct_answer": "Dictionary",
        "explanation": "Dictionaries store data in key-value pairs for efficient lookup.",
        "hints": "Dictionaries (dict) map keys to values like {'name': 'John'}. Lists, tuples, and sets don't use key-value pairs.",
        "course_id": SKILL_TO_COURSE["SK004"]
    },
    {
        "skill_id": "SK004",
        "skill_name": "Data Structures",
        "difficulty": "Easy",
        "problem_type": "Coding",
        "question_text": "Create a dictionary with keys 'name' and 'age' with values 'John' and 25",
        "options": None,
        "correct_answer": "{'name': 'John', 'age': 25}",
        "explanation": "Dictionaries are created using curly braces with key: value pairs.",
        "hints": "Use curly braces with key: value pairs separated by commas. Keys and values can be strings or other types.",
        "course_id": SKILL_TO_COURSE["SK004"]
    },
    {
        "skill_id": "SK004",
        "skill_name": "Data Structures",
        "difficulty": "Easy",
        "problem_type": "Multiple Choice",
        "question_text": "Which operation adds an element to the end of a list?",
        "options": '["add()", "append()", "insert()", "push()"]',
        "correct_answer": "append()",
        "explanation": "The append() method adds an element to the end of a list.",
        "hints": "The append() method adds to the end. insert() adds at a specific position. Python doesn't have add() or push() for lists.",
        "course_id": SKILL_TO_COURSE["SK004"]
    },
    {
        "skill_id": "SK004",
        "skill_name": "Data Structures",
        "difficulty": "Easy",
        "problem_type": "Coding",
        "question_text": "Create a list containing the numbers 1, 2, 3",
        "options": None,
        "correct_answer": "[1, 2, 3]",
        "explanation": "Lists are created using square brackets with comma-separated values.",
        "hints": "Use square brackets [] with values separated by commas: [1, 2, 3]",
        "course_id": SKILL_TO_COURSE["SK004"]
    },
    {
        "skill_id": "SK004",
        "skill_name": "Data Structures",
        "difficulty": "Medium",
        "problem_type": "Conceptual",
        "question_text": "What is the time complexity of accessing an element in a list by index?",
        "options": '["O(n)", "O(log n)", "O(1)", "O(n^2)"]',
        "correct_answer": "O(1)",
        "explanation": "List access by index is constant time O(1) because lists are implemented as arrays.",
        "hints": "O(1) means constant time - it takes the same time regardless of list size. Lists are arrays in memory.",
        "course_id": SKILL_TO_COURSE["SK004"]
    },
    {
        "skill_id": "SK004",
        "skill_name": "Data Structures",
        "difficulty": "Medium",
        "problem_type": "Coding",
        "question_text": "Write code to get the value for key 'name' from dict {'name': 'Alice', 'age': 30}",
        "options": None,
        "correct_answer": "d['name'] or d.get('name')",
        "explanation": "Dictionary values can be accessed using square brackets with the key, or the get() method.",
        "hints": "Use dict['key'] or dict.get('key'). get() is safer as it returns None if key doesn't exist.",
        "course_id": SKILL_TO_COURSE["SK004"]
    },
    {
        "skill_id": "SK004",
        "skill_name": "Data Structures",
        "difficulty": "Medium",
        "problem_type": "Multiple Choice",
        "question_text": "Which data structure does NOT allow duplicate elements?",
        "options": '["List", "Tuple", "Set", "Dictionary"]',
        "correct_answer": "Set",
        "explanation": "Sets only store unique elements; duplicates are automatically removed.",
        "hints": "Sets automatically remove duplicates. Lists and tuples can have duplicates. Dictionary keys must be unique but values can repeat.",
        "course_id": SKILL_TO_COURSE["SK004"]
    },
    {
        "skill_id": "SK004",
        "skill_name": "Data Structures",
        "difficulty": "Medium",
        "problem_type": "Debugging",
        "question_text": "What is wrong with: my_list = [1, 2, 3]; my_list[3] = 4",
        "options": '["Nothing is wrong", "Index out of range", "Cannot assign to list", "Wrong syntax"]',
        "correct_answer": "Index out of range",
        "explanation": "List indices are 0-based. A list of 3 elements has valid indices 0, 1, 2. Index 3 is out of range.",
        "hints": "List indices start at 0. A 3-element list has indices 0, 1, 2. Index 3 doesn't exist.",
        "course_id": SKILL_TO_COURSE["SK004"]
    },
    {
        "skill_id": "SK004",
        "skill_name": "Data Structures",
        "difficulty": "Hard",
        "problem_type": "Coding",
        "question_text": "Write code to reverse a list [1, 2, 3, 4] without using reverse()",
        "options": None,
        "correct_answer": "my_list[::-1]",
        "explanation": "List slicing with step -1 reverses the list. Alternatively: list(reversed(my_list))",
        "hints": "Use slicing with step -1: list[::-1]. This creates a reversed copy of the list.",
        "course_id": SKILL_TO_COURSE["SK004"]
    },
    {
        "skill_id": "SK004",
        "skill_name": "Data Structures",
        "difficulty": "Hard",
        "problem_type": "Conceptual",
        "question_text": "What is the difference between a stack and a queue?",
        "options": '["Stack is LIFO, Queue is FIFO", "Stack is FIFO, Queue is LIFO", "Both are LIFO", "Both are FIFO"]',
        "correct_answer": "Stack is LIFO, Queue is FIFO",
        "explanation": "Stack follows Last-In-First-Out (LIFO), while Queue follows First-In-First-Out (FIFO).",
        "hints": "LIFO = Last In First Out (like a stack of plates). FIFO = First In First Out (like a line at a store).",
        "course_id": SKILL_TO_COURSE["SK004"]
    },

    # ========== SQL Queries (SK005) - 10 questions ==========
    {
        "skill_id": "SK005",
        "skill_name": "SQL Queries",
        "difficulty": "Easy",
        "problem_type": "Multiple Choice",
        "question_text": "Which SQL statement is used to retrieve data from a database?",
        "options": '["GET", "OPEN", "EXTRACT", "SELECT"]',
        "correct_answer": "SELECT",
        "explanation": "The SELECT statement is used to retrieve data from database tables.",
        "hints": "SELECT is the command to read/retrieve data. INSERT adds data, UPDATE modifies data, DELETE removes data.",
        "course_id": SKILL_TO_COURSE["SK005"]
    },
    {
        "skill_id": "SK005",
        "skill_name": "SQL Queries",
        "difficulty": "Easy",
        "problem_type": "Coding",
        "question_text": "Write a SQL query to select all columns from a table named 'users'",
        "options": None,
        "correct_answer": "SELECT * FROM users",
        "explanation": "SELECT * retrieves all columns from the specified table.",
        "hints": "Use SELECT * to get all columns. Always specify the table with FROM tablename.",
        "course_id": SKILL_TO_COURSE["SK005"]
    },
    {
        "skill_id": "SK005",
        "skill_name": "SQL Queries",
        "difficulty": "Easy",
        "problem_type": "Multiple Choice",
        "question_text": "Which clause is used to filter records in SQL?",
        "options": '["FILTER", "WHERE", "HAVING", "GROUP BY"]',
        "correct_answer": "WHERE",
        "explanation": "The WHERE clause filters records based on specified conditions.",
        "hints": "WHERE filters rows before aggregation. HAVING filters after GROUP BY. FILTER is not a SQL clause.",
        "course_id": SKILL_TO_COURSE["SK005"]
    },
    {
        "skill_id": "SK005",
        "skill_name": "SQL Queries",
        "difficulty": "Easy",
        "problem_type": "Coding",
        "question_text": "Write a query to select name from users where age > 25",
        "options": None,
        "correct_answer": "SELECT name FROM users WHERE age > 25",
        "explanation": "Combine SELECT, FROM, and WHERE clauses to filter and retrieve specific data.",
        "hints": "Structure: SELECT column FROM table WHERE condition. Use comparison operators like >, <, =, >=, <=",
        "course_id": SKILL_TO_COURSE["SK005"]
    },
    {
        "skill_id": "SK005",
        "skill_name": "SQL Queries",
        "difficulty": "Medium",
        "problem_type": "Coding",
        "question_text": "Write a query to count the number of rows in a table",
        "options": None,
        "correct_answer": "SELECT COUNT(*) FROM table_name",
        "explanation": "COUNT(*) is an aggregate function that returns the number of rows.",
        "hints": "Use the COUNT(*) aggregate function. It counts all rows including NULLs.",
        "course_id": SKILL_TO_COURSE["SK005"]
    },
    {
        "skill_id": "SK005",
        "skill_name": "SQL Queries",
        "difficulty": "Medium",
        "problem_type": "Multiple Choice",
        "question_text": "What does ORDER BY do in SQL?",
        "options": '["Filters results", "Sorts results", "Groups results", "Joins tables"]',
        "correct_answer": "Sorts results",
        "explanation": "ORDER BY sorts the result set in ascending or descending order.",
        "hints": "ORDER BY sorts results. Add DESC for descending order. Default is ascending.",
        "course_id": SKILL_TO_COURSE["SK005"]
    },
    {
        "skill_id": "SK005",
        "skill_name": "SQL Queries",
        "difficulty": "Medium",
        "problem_type": "Coding",
        "question_text": "Write a query to select names sorted alphabetically",
        "options": None,
        "correct_answer": "SELECT name FROM users ORDER BY name",
        "explanation": "ORDER BY with a column name sorts by that column. Default is ascending.",
        "hints": "Add ORDER BY column_name at the end. For descending, use ORDER BY column_name DESC.",
        "course_id": SKILL_TO_COURSE["SK005"]
    },
    {
        "skill_id": "SK005",
        "skill_name": "SQL Queries",
        "difficulty": "Medium",
        "problem_type": "Conceptual",
        "question_text": "What is the difference between WHERE and HAVING?",
        "options": '["No difference", "WHERE filters rows, HAVING filters groups", "HAVING filters rows, WHERE filters groups", "WHERE is for SELECT, HAVING for UPDATE"]',
        "correct_answer": "WHERE filters rows, HAVING filters groups",
        "explanation": "WHERE filters individual rows before grouping. HAVING filters aggregated groups after GROUP BY.",
        "hints": "WHERE filters before aggregation (on individual rows). HAVING filters after GROUP BY (on aggregated results).",
        "course_id": SKILL_TO_COURSE["SK005"]
    },
    {
        "skill_id": "SK005",
        "skill_name": "SQL Queries",
        "difficulty": "Hard",
        "problem_type": "Coding",
        "question_text": "Write a query to find the average salary grouped by department",
        "options": None,
        "correct_answer": "SELECT department, AVG(salary) FROM employees GROUP BY department",
        "explanation": "Use AVG() aggregate function with GROUP BY to calculate averages per group.",
        "hints": "Use AVG(column) with GROUP BY column. The GROUP BY column must be in SELECT.",
        "course_id": SKILL_TO_COURSE["SK005"]
    },
    {
        "skill_id": "SK005",
        "skill_name": "SQL Queries",
        "difficulty": "Hard",
        "problem_type": "Conceptual",
        "question_text": "What does LIKE operator do in SQL?",
        "options": '["Compares equality", "Pattern matching in strings", "Checks for NULL", "Performs arithmetic"]',
        "correct_answer": "Pattern matching in strings",
        "explanation": "LIKE is used for pattern matching with wildcards like % (any characters) and _ (single character).",
        "hints": "LIKE matches patterns. % matches any sequence of characters. _ matches exactly one character.",
        "course_id": SKILL_TO_COURSE["SK005"]
    },

    # ========== SQL Joins (SK006) - 10 questions ==========
    {
        "skill_id": "SK006",
        "skill_name": "SQL Joins",
        "difficulty": "Easy",
        "problem_type": "Multiple Choice",
        "question_text": "Which JOIN returns only matching rows from both tables?",
        "options": '["INNER JOIN", "LEFT JOIN", "RIGHT JOIN", "FULL OUTER JOIN"]',
        "correct_answer": "INNER JOIN",
        "explanation": "INNER JOIN returns only rows where there is a match in both tables.",
        "hints": "INNER JOIN requires matches in both tables. Unmatched rows are excluded from results.",
        "course_id": SKILL_TO_COURSE["SK006"]
    },
    {
        "skill_id": "SK006",
        "skill_name": "SQL Joins",
        "difficulty": "Easy",
        "problem_type": "Coding",
        "question_text": "Write a query to join orders and customers tables on customer_id",
        "options": None,
        "correct_answer": "SELECT * FROM orders INNER JOIN customers ON orders.customer_id = customers.id",
        "explanation": "INNER JOIN combines tables based on a matching condition.",
        "hints": "Syntax: FROM table1 INNER JOIN table2 ON table1.column = table2.column",
        "course_id": SKILL_TO_COURSE["SK006"]
    },
    {
        "skill_id": "SK006",
        "skill_name": "SQL Joins",
        "difficulty": "Easy",
        "problem_type": "Multiple Choice",
        "question_text": "Which JOIN returns all rows from the left table and matching from right?",
        "options": '["INNER JOIN", "LEFT JOIN", "RIGHT JOIN", "CROSS JOIN"]',
        "correct_answer": "LEFT JOIN",
        "explanation": "LEFT JOIN returns all rows from the left table, and matching rows from the right table (NULL if no match).",
        "hints": "LEFT JOIN keeps all rows from the first (left) table. Unmatched rows get NULL values from the right table.",
        "course_id": SKILL_TO_COURSE["SK006"]
    },
    {
        "skill_id": "SK006",
        "skill_name": "SQL Joins",
        "difficulty": "Medium",
        "problem_type": "Coding",
        "question_text": "Write a LEFT JOIN to get all customers and their orders (if any)",
        "options": None,
        "correct_answer": "SELECT * FROM customers LEFT JOIN orders ON customers.id = orders.customer_id",
        "explanation": "LEFT JOIN ensures all customers are included even if they have no orders.",
        "hints": "Put the table you want all rows from first (left). Use LEFT JOIN to include non-matching rows with NULLs.",
        "course_id": SKILL_TO_COURSE["SK006"]
    },
    {
        "skill_id": "SK006",
        "skill_name": "SQL Joins",
        "difficulty": "Medium",
        "problem_type": "Multiple Choice",
        "question_text": "Which JOIN returns all records when there is a match in either table?",
        "options": '["INNER JOIN", "LEFT JOIN", "RIGHT JOIN", "FULL OUTER JOIN"]',
        "correct_answer": "FULL OUTER JOIN",
        "explanation": "FULL OUTER JOIN returns all records from both tables, matching where possible.",
        "hints": "FULL OUTER JOIN combines LEFT and RIGHT JOIN - keeps all rows from both tables, matching where possible.",
        "course_id": SKILL_TO_COURSE["SK006"]
    },
    {
        "skill_id": "SK006",
        "skill_name": "SQL Joins",
        "difficulty": "Medium",
        "problem_type": "Conceptual",
        "question_text": "What is the difference between LEFT JOIN and RIGHT JOIN?",
        "options": '["No difference", "LEFT keeps left table all rows, RIGHT keeps right table all rows", "LEFT is faster", "RIGHT requires more memory"]',
        "correct_answer": "LEFT keeps left table all rows, RIGHT keeps right table all rows",
        "explanation": "LEFT JOIN preserves all rows from the left table, RIGHT JOIN preserves all rows from the right table.",
        "hints": "LEFT JOIN keeps all from first table. RIGHT JOIN keeps all from second table. They're mirror images.",
        "course_id": SKILL_TO_COURSE["SK006"]
    },
    {
        "skill_id": "SK006",
        "skill_name": "SQL Joins",
        "difficulty": "Medium",
        "problem_type": "Coding",
        "question_text": "Write a query to join three tables: users, orders, and products",
        "options": None,
        "correct_answer": "SELECT * FROM users JOIN orders ON users.id = orders.user_id JOIN products ON orders.product_id = products.id",
        "explanation": "Multiple JOINs can be chained to connect more than two tables.",
        "hints": "Chain JOINs: FROM table1 JOIN table2 ON condition JOIN table3 ON condition. Each join connects two tables.",
        "course_id": SKILL_TO_COURSE["SK006"]
    },
    {
        "skill_id": "SK006",
        "skill_name": "SQL Joins",
        "difficulty": "Medium",
        "problem_type": "Debugging",
        "question_text": "What is wrong with: SELECT * FROM table1 JOIN table2",
        "options": '["Missing ON clause", "Wrong JOIN type", "Missing WHERE", "Nothing is wrong"]',
        "correct_answer": "Missing ON clause",
        "explanation": "JOIN requires an ON clause to specify the join condition between tables.",
        "hints": "Every JOIN (except CROSS JOIN) needs an ON clause to specify how tables relate to each other.",
        "course_id": SKILL_TO_COURSE["SK006"]
    },
    {
        "skill_id": "SK006",
        "skill_name": "SQL Joins",
        "difficulty": "Hard",
        "problem_type": "Coding",
        "question_text": "Write a self-join to find employees and their managers",
        "options": None,
        "correct_answer": "SELECT e.name, m.name as manager FROM employees e LEFT JOIN employees m ON e.manager_id = m.id",
        "explanation": "Self-join joins a table to itself by using aliases to treat it as two different tables.",
        "hints": "Use aliases to treat the same table as two instances: employees e and employees m. Join on the foreign key relationship.",
        "course_id": SKILL_TO_COURSE["SK006"]
    },
    {
        "skill_id": "SK006",
        "skill_name": "SQL Joins",
        "difficulty": "Hard",
        "problem_type": "Conceptual",
        "question_text": "What is a CROSS JOIN?",
        "options": '["Join with condition", "Cartesian product of two tables", "Join with aggregation", "Join with NULL values"]',
        "correct_answer": "Cartesian product of two tables",
        "explanation": "CROSS JOIN returns the Cartesian product - every row from first table combined with every row from second table.",
        "hints": "CROSS JOIN combines every row from table A with every row from table B. No ON clause needed. Result size = rowsA × rowsB.",
        "course_id": SKILL_TO_COURSE["SK006"]
    },

    # ========== Debugging (SK007) - 10 questions ==========
    {
        "skill_id": "SK007",
        "skill_name": "Debugging",
        "difficulty": "Easy",
        "problem_type": "Debugging",
        "question_text": "What is wrong with this code: print('Hello",
        "options": '["Missing closing quote", "Missing closing parenthesis", "Both", "Nothing is wrong"]',
        "correct_answer": "Both",
        "explanation": "The string is missing the closing quote and the print function is missing the closing parenthesis.",
        "hints": "Check that every opening quote has a closing quote, and every opening parenthesis has a closing parenthesis.",
        "course_id": SKILL_TO_COURSE["SK007"]
    },
    {
        "skill_id": "SK007",
        "skill_name": "Debugging",
        "difficulty": "Easy",
        "problem_type": "Multiple Choice",
        "question_text": "Which error occurs when dividing by zero?",
        "options": '["ValueError", "TypeError", "ZeroDivisionError", "IndexError"]',
        "correct_answer": "ZeroDivisionError",
        "explanation": "ZeroDivisionError is raised when attempting to divide by zero.",
        "hints": "Division by zero is a specific error type in Python called ZeroDivisionError.",
        "course_id": SKILL_TO_COURSE["SK007"]
    },
    {
        "skill_id": "SK007",
        "skill_name": "Debugging",
        "difficulty": "Easy",
        "problem_type": "Debugging",
        "question_text": "What is wrong with: if x = 5: print(x)",
        "options": '["Assignment instead of comparison", "Missing colon", "Wrong indentation", "Nothing is wrong"]',
        "correct_answer": "Assignment instead of comparison",
        "explanation": "Use == for comparison in if conditions. Single = is assignment.",
        "hints": "In conditions, use == for comparison. Single = is for assignment (setting a value).",
        "course_id": SKILL_TO_COURSE["SK007"]
    },
    {
        "skill_id": "SK007",
        "skill_name": "Debugging",
        "difficulty": "Medium",
        "problem_type": "Debugging",
        "question_text": "What is wrong with this code: for i in range(5): print(i + 1)",
        "options": '["Nothing is wrong", "Should use range(1, 6)", "Indentation error", "Missing colon"]',
        "correct_answer": "Nothing is wrong",
        "explanation": "This code is actually correct - it prints numbers 1-5 by adding 1 to each value.",
        "hints": "This code is correct! It prints 1, 2, 3, 4, 5 by adding 1 to each value from range(5) which is 0, 1, 2, 3, 4.",
        "course_id": SKILL_TO_COURSE["SK007"]
    },
    {
        "skill_id": "SK007",
        "skill_name": "Debugging",
        "difficulty": "Medium",
        "problem_type": "Multiple Choice",
        "question_text": "What is the purpose of a breakpoint in debugging?",
        "options": '["Stop execution at a specific line", "Print all variables", "Fix the bug automatically", "Delete the code"]',
        "correct_answer": "Stop execution at a specific line",
        "explanation": "Breakpoints pause program execution at a specified line, allowing inspection of program state.",
        "hints": "Breakpoints pause execution so you can inspect variables and step through code line by line.",
        "course_id": SKILL_TO_COURSE["SK007"]
    },
    {
        "skill_id": "SK007",
        "skill_name": "Debugging",
        "difficulty": "Medium",
        "problem_type": "Debugging",
        "question_text": "Find the bug: def calculate(x): return x * 2 if x > 0 else x / 0",
        "options": '["Division by zero error", "Missing else clause", "Wrong operator", "No bug"]',
        "correct_answer": "Division by zero error",
        "explanation": "When x <= 0, the code attempts to divide by zero which causes an error.",
        "hints": "The else branch divides by zero, which will raise ZeroDivisionError when x <= 0.",
        "course_id": SKILL_TO_COURSE["SK007"]
    },
    {
        "skill_id": "SK007",
        "skill_name": "Debugging",
        "difficulty": "Medium",
        "problem_type": "Debugging",
        "question_text": "What is wrong with: my_list = [1, 2]; print(my_list[2])",
        "options": '["Index out of range", "Wrong syntax", "Missing comma", "Nothing is wrong"]',
        "correct_answer": "Index out of range",
        "explanation": "List indices are 0-based. A 2-element list has indices 0 and 1. Index 2 is out of range.",
        "hints": "List indices start at 0. A 2-element list has indices 0 and 1 only. Index 2 doesn't exist.",
        "course_id": SKILL_TO_COURSE["SK007"]
    },
    {
        "skill_id": "SK007",
        "skill_name": "Debugging",
        "difficulty": "Hard",
        "problem_type": "Debugging",
        "question_text": "Find the bug: x = 5; y = 10; if x > 3 and y < 5: print('Both true')",
        "options": '["Logic error in condition", "Syntax error", "Nothing is wrong", "Missing colon"]',
        "correct_answer": "Logic error in condition",
        "explanation": "y < 5 is False (y is 10), so the condition fails. This is a logic error if the intent was different.",
        "hints": "y is 10, so y < 5 is False. The and condition requires both parts to be True, so nothing prints.",
        "course_id": SKILL_TO_COURSE["SK007"]
    },
    {
        "skill_id": "SK007",
        "skill_name": "Debugging",
        "difficulty": "Hard",
        "problem_type": "Coding",
        "question_text": "Write a try-except block to handle division by zero",
        "options": None,
        "correct_answer": "try: result = x / y; except ZeroDivisionError: result = None",
        "explanation": "try-except allows graceful error handling. ZeroDivisionError is caught and handled.",
        "hints": "Use try: followed by code that might fail, then except ErrorName: to handle specific errors.",
        "course_id": SKILL_TO_COURSE["SK007"]
    },
    {
        "skill_id": "SK007",
        "skill_name": "Debugging",
        "difficulty": "Hard",
        "problem_type": "Conceptual",
        "question_text": "What is the difference between syntax error and runtime error?",
        "options": '["No difference", "Syntax error before execution, runtime during execution", "Runtime before execution, syntax during", "Both occur during execution"]',
        "correct_answer": "Syntax error before execution, runtime during execution",
        "explanation": "Syntax errors are detected before the program runs (parsing). Runtime errors occur during execution.",
        "hints": "Syntax errors are caught before code runs (like typos). Runtime errors happen while the code is executing (like division by zero).",
        "course_id": SKILL_TO_COURSE["SK007"]
    },

    # ========== Algorithms (SK008) - 10 questions ==========
    {
        "skill_id": "SK008",
        "skill_name": "Algorithms",
        "difficulty": "Easy",
        "problem_type": "Multiple Choice",
        "question_text": "What is the time complexity of binary search?",
        "options": '["O(n)", "O(log n)", "O(n^2)", "O(1)"]',
        "correct_answer": "O(log n)",
        "explanation": "Binary search divides the search space in half each time, resulting in O(log n) complexity.",
        "hints": "Binary search halves the search space each iteration. Halving repeatedly gives logarithmic time complexity.",
        "course_id": SKILL_TO_COURSE["SK008"]
    },
    {
        "skill_id": "SK008",
        "skill_name": "Algorithms",
        "difficulty": "Easy",
        "problem_type": "Multiple Choice",
        "question_text": "Which sorting algorithm has O(n log n) average time complexity?",
        "options": '["Bubble Sort", "Selection Sort", "Merge Sort", "Insertion Sort"]',
        "correct_answer": "Merge Sort",
        "explanation": "Merge Sort has O(n log n) time complexity in all cases, making it efficient for large datasets.",
        "hints": "Merge Sort and Quick Sort are O(n log n) on average. Bubble, Selection, and Insertion sorts are O(n^2).",
        "course_id": SKILL_TO_COURSE["SK008"]
    },
    {
        "skill_id": "SK008",
        "skill_name": "Algorithms",
        "difficulty": "Easy",
        "problem_type": "Conceptual",
        "question_text": "What is the best case time complexity of bubble sort?",
        "options": '["O(n)", "O(n log n)", "O(n^2)", "O(1)"]',
        "correct_answer": "O(n)",
        "explanation": "Bubble sort's best case is O(n) when the array is already sorted (with optimization).",
        "hints": "With optimization (checking if swaps occurred), already sorted arrays take O(n) time to verify.",
        "course_id": SKILL_TO_COURSE["SK008"]
    },
    {
        "skill_id": "SK008",
        "skill_name": "Algorithms",
        "difficulty": "Medium",
        "problem_type": "Multiple Choice",
        "question_text": "What data structure is used for BFS (Breadth-First Search)?",
        "options": '["Stack", "Queue", "Priority Queue", "Linked List"]',
        "correct_answer": "Queue",
        "explanation": "BFS uses a queue (FIFO) to explore nodes level by level.",
        "hints": "BFS explores neighbors first, then neighbors of neighbors. This FIFO behavior requires a queue.",
        "course_id": SKILL_TO_COURSE["SK008"]
    },
    {
        "skill_id": "SK008",
        "skill_name": "Algorithms",
        "difficulty": "Medium",
        "problem_type": "Conceptual",
        "question_text": "What is the difference between BFS and DFS?",
        "options": '["No difference", "BFS uses queue, DFS uses stack", "BFS uses stack, DFS uses queue", "Both use arrays"]',
        "correct_answer": "BFS uses queue, DFS uses stack",
        "explanation": "BFS explores level by level using a queue. DFS explores depth-first using a stack (or recursion).",
        "hints": "BFS (Breadth-First) uses a queue to explore level by level. DFS (Depth-First) uses a stack or recursion to go deep first.",
        "course_id": SKILL_TO_COURSE["SK008"]
    },
    {
        "skill_id": "SK008",
        "skill_name": "Algorithms",
        "difficulty": "Medium",
        "problem_type": "Coding",
        "question_text": "Write a function to find the maximum element in a list",
        "options": None,
        "correct_answer": "def find_max(lst): return max(lst)",
        "explanation": "Python's built-in max() function finds the maximum element. Alternatively: iterate and track max.",
        "hints": "Use Python's built-in max() function, or iterate through the list tracking the largest value seen.",
        "course_id": SKILL_TO_COURSE["SK008"]
    },
    {
        "skill_id": "SK008",
        "skill_name": "Algorithms",
        "difficulty": "Medium",
        "problem_type": "Multiple Choice",
        "question_text": "What is the worst case time complexity of quicksort?",
        "options": '["O(n)", "O(n log n)", "O(n^2)", "O(log n)"]',
        "correct_answer": "O(n^2)",
        "explanation": "Quicksort's worst case is O(n^2) when the pivot selection is poor (e.g., already sorted array with bad pivot).",
        "hints": "Quicksort is O(n log n) on average but O(n^2) in worst case (e.g., when pivot is always smallest/largest element).",
        "course_id": SKILL_TO_COURSE["SK008"]
    },
    {
        "skill_id": "SK008",
        "skill_name": "Algorithms",
        "difficulty": "Hard",
        "problem_type": "Coding",
        "question_text": "Implement a function to check if a number is prime",
        "options": None,
        "correct_answer": "def is_prime(n): if n < 2: return False; for i in range(2, int(n**0.5)+1): if n % i == 0: return False; return True",
        "explanation": "A prime number is only divisible by 1 and itself. We check up to sqrt(n) for efficiency.",
        "hints": "Check divisibility from 2 to sqrt(n). If any number divides evenly, it's not prime. 0 and 1 are not prime.",
        "course_id": SKILL_TO_COURSE["SK008"]
    },
    {
        "skill_id": "SK008",
        "skill_name": "Algorithms",
        "difficulty": "Hard",
        "problem_type": "Coding",
        "question_text": "Write a function to implement binary search on a sorted list",
        "options": None,
        "correct_answer": "def binary_search(arr, target): low, high = 0, len(arr)-1; while low <= high: mid = (low+high)//2; if arr[mid] == target: return mid; elif arr[mid] < target: low = mid+1; else: high = mid-1; return -1",
        "explanation": "Binary search repeatedly divides the search interval in half until the target is found or the interval is empty.",
        "hints": "Use low/high pointers, calculate mid, compare arr[mid] to target, and adjust pointers until found or interval empty.",
        "course_id": SKILL_TO_COURSE["SK008"]
    },
    {
        "skill_id": "SK008",
        "skill_name": "Algorithms",
        "difficulty": "Hard",
        "problem_type": "Conceptual",
        "question_text": "What is dynamic programming?",
        "options": '["A sorting algorithm", "Optimization by breaking into overlapping subproblems", "A search algorithm", "A data structure"]',
        "correct_answer": "Optimization by breaking into overlapping subproblems",
        "explanation": "Dynamic programming solves complex problems by breaking them into simpler overlapping subproblems and storing results.",
        "hints": "DP breaks problems into overlapping subproblems, stores solutions, and reuses them to avoid redundant calculations.",
        "course_id": SKILL_TO_COURSE["SK008"]
    },
]


def seed_database():
    """Seed the database with initial questions and a test user."""
    # Create tables
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()

    try:
        # Check if questions already exist
        existing_questions = db.query(Question).count()
        if existing_questions > 0:
            print(f"Database already has {existing_questions} questions. Skipping seed.")
            return

        # Add questions
        print("Seeding questions...")
        for q_data in SAMPLE_QUESTIONS:
            question = Question(**q_data)
            db.add(question)

        db.commit()
        print(f"Added {len(SAMPLE_QUESTIONS)} questions to the database.")

        # Add a test user with shorter password to avoid bcrypt 72-byte limit
        print("Seeding test user...")
        test_password = "test123"  # Shorter password to avoid bcrypt limit
        test_user = User(
            username="testuser",
            password_hash=get_password_hash(test_password)
        )
        db.add(test_user)
        db.commit()
        print(f"Added test user: username='testuser', password='{test_password}'")

        print("\nDatabase seeded successfully!")

    except Exception as e:
        print(f"Error seeding database: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
