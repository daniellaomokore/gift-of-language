from flask import session
from sqlalchemy import and_
from boredapp import database, connect_to_api
from boredapp.models import TheUsers, Favourites

APIurl = "http://www.boredapi.com/api/activity"



#a function that is used to  extracts information the log in form
def get_login_details(form):
    column = form['logintype']
    print(column)
    value = form['username']
    password = form['password']
    log_in_right = username_and_password_match(column, value, password)
    return log_in_right, column, value


#a function that is used to  extracts information the sign up form
def get_signup_details(form):
    email = form['email']
    firstname = form['firstname']
    lastname = form['lastname']
    dob = form['dob']
    city = form['city']
    username = form['username']
    password = form['password']
    if check_if_valid_password(password) and check_if_valid_username(username) and check_if_valid_email(email) and check_if_valid_date(dob) and check_if_valid_name(firstname):
        passed_regex_check = True
        if does_user_exist('Email', email) or does_user_exist('Username', username):
            duplicate = True
            email = None
        else:
            duplicate = False
            add_a_new_user(firstname, lastname, email, dob, city, username, password)
    else:
        passed_regex_check = False
        duplicate = None
        email = None
    return firstname, email, duplicate, passed_regex_check



# Function returns a word's definition from the api we are using
def get_definition(word):
    dictionary_url = 'https://api.dictionaryapi.dev/api/v2/entries/en/{}'.format(word)

    response = requests.get(dictionary_url)
    # print(response.status_code)
    word_data = response.json()
    try:
        definition = word_data[0]['meanings'][0]['definitions'][0]['definition']
    except Exception:
        return 'This word does not exist in the dictionary.'
    else:
        return definition

# Function displays a word and it's definition when called
def show_word_and_definition(word):
    if get_definition(word) == 'This word does not exist in the dictionary.':
        print('This word does not exist in the dictionary.')
        return 'This word does not exist in the dictionary.'
    else:
        print('The word is: {}'.format(word))
        print('The definition is: {}'.format(get_definition(word)))
        return "The Word : {} .  The Definition : {}.".format(word, get_definition(word))


# Import connection from db_function
class DbConnectionError(Exception):
    pass

@db_connection_decorator
def check_if_word_in_database_for_user(word, userid, cur, db_connection):
    query = "SELECT word FROM searched_words WHERE UserID = {};".format(userid)
    cur.execute(query)
    result = cur.fetchall()
    result = [list(i) for i in result]
    final_result = list(itertools.chain(*result))
    if word.lower() in final_result:
        return True
    else:
        return False


@db_connection_decorator
def add_searched_word(new_word, userid, cur, db_connection):
    if not check_if_word_in_database_for_user(new_word, userid):
        definition = get_definition(new_word)
        query = 'INSERT INTO searched_words(UserID, word, definition_) VALUES ("{}", "{}", "{}");'.format(userid, new_word.lower(), definition)
        cur.execute(query)
        db_connection.commit()

@db_connection_decorator
def display_users_searched_word(userid, cur, db_connection):
    query = """SELECT word, definition_
                FROM searched_words
                WHERE UserID = {} ;""".format(userid)
    cur.execute(query)
    result = cur.fetchall() # a list of tuples
    return result

@db_connection_decorator
def get_all_searched_words(cur, db_connection):
    query = """SELECT word FROM searched_words;"""
    cur.execute(query)
    result = cur.fetchall()
    result_list = [i[0] for i in result]
    return result_list

# Documentation:
# I'm using this manual method below for the random word generator based on the words in our chosen api
# instead of using the random words library as :
# 1. A lot of the words don't exist in the api we are using so the definition and examples etc can't be searched
# 2. The words it generates are extremely advanced english that I don't even know myself and aren't commonly used in day too day speaking

# GENERATING THE RANDOM WORD FOR USERS DAILY WORD
def randomWordGenerator():
    # Converting the text file of the dictionary words into a list of strings
    with open("../docs/english.txt", encoding="utf8") as wordDictionary:
        wordDictionaryList = []  # the wordDictionary in list form
        for line in wordDictionary:
            wordDictionaryList.append(line.strip())
            #  print(wordDictionaryList)    # the wordDictionary in list form
            #  print(wordDictionaryList)    # the wordDictionary in list form

    # Total number of dictionary words
    dictionaryLength = len(wordDictionaryList)
    #  print(dictionaryLength)

    # Generates a random number within the range of the index for the list of dictionary words
    randomDictIndex = random.randint(0, dictionaryLength - 1)
    #  print("RANDOM DICTIONARY INDEX: " , randomDictIndex)

    # Getting our random word
    randomWord = wordDictionaryList[randomDictIndex]
    #  print("RANDOM WORD: " , randomWord)

    return searchAPIForRandomWord(randomWord)



#  SEARCHING THE API WITH A RANDOMLY GENERATED WORD
def searchAPIForRandomWord(randomWord):
    # CONNECTING TO AN API TO SEARCH WITH THE RANDOM WORD AND PRINT ITS NAME AND DEFINITION
    dictionary_url = 'https://api.dictionaryapi.dev/api/v2/entries/en/{}'.format(randomWord)

    response = requests.get(dictionary_url)
    # print(response.status_code)  #should be 200
    word_data = response.json()  # word_data is the API's list of dictionaries

    # printing the name and definition of the word from its dictionary
    for dictionary in word_data:
        print("Word: " + dictionary['word'])  # print the value of the word key
        print("Definition: " + dictionary['meanings'][0]['definitions'][0]['definition'])
        # print("Definition: " + dictionary['meanings'][0]['definitions'][0]['example'])

    return "Word: {}".format(word_data[0]['word']), "Definition: {}".format(word_data[0]['meanings'][0]['definitions'][0]['definition'])


@db_connection_decorator
def does_user_exist(column, value, cur, db_connection):
    query = """
            SELECT (EXISTS(SELECT FirstName
            FROM the_users
            WHERE {COLUMN} = '{VALUE}'));
            """.format(COLUMN=column, VALUE=value)
    cur.execute(query)
    result = cur.fetchall()
    # print(result)
    ## THE ABOVE QUEUERY WILL EITHER RETURN
    ## [(1,)] WHICH REPRESENTS TRUE
    ## OR [(0,)] WHICH REPRESENTS FALSE
    if result[0][0] == 1:
        return True
    else:
        return False


@db_connection_decorator
def add_a_new_user(firstname, lastname, email, dob, city, username, password, cur, db_connection):
    query = """
            INSERT INTO the_users (FirstName, LastName, Email, DOB, City, Username, UserPassword)
            VALUES ('{FIRSTNAME}', '{LASTNAME}', '{EMAIL}', str_to_date('{DOB}', '%d-%m-%Y'), '{CITY}', '{USERNAME}', '{PASSWORD}')
            """.format(FIRSTNAME=firstname, LASTNAME=lastname, EMAIL=email, DOB=dob,
                       CITY=city, USERNAME=username, PASSWORD=password)
    cur.execute(query)
    db_connection.commit()


@db_connection_decorator
def get_user_by_id(userid, cur, db_connection):
    query = """SELECT UserID, Firstname, Lastname, Username
                FROM the_users
                WHERE UserID = {USERID};""".format(USERID=userid)
    cur.execute(query)
    result = cur.fetchall()
    return result


@db_connection_decorator
def get_user_by_column(column, value, cur, db_connection):
    query = """SELECT UserID
                FROM the_users
                WHERE {COLUMN} = '{VALUE}';""".format(COLUMN=column, VALUE=value)
    cur.execute(query)
    result = cur.fetchall()
    userid = result[0][0]
    return userid



@db_connection_decorator
def username_and_password_match(column, value, password_value, cur, db_connection):
    # This query checks if the records of the password and username exist in one record. It returns 1 if it does exist and 0 if it does not exist.
    query = "SELECT(EXISTS(SELECT FirstName FROM the_users WHERE {} = '{}' AND UserPassword = '{}'))".format(column,
                                                                                                             value,
                                                                                                             password_value)
    cur.execute(query)
    result2 = cur.fetchall()
    if result2[0][0] == 1:
        # This query calls the users first name, if the login has been successful.
        query2 = "SELECT FirstName FROM the_users WHERE {} = '{}' AND UserPassword = '{}'".format(column, value,
                                                                                                  password_value)
        cur.execute(query2)
        result3 = cur.fetchall()
        # This for loop extracts the first name from the tuple case.
        for data in result3:
            name = data[0]
            print("Login Successful. \nWelcome, {}".format(name))
        return True
    else:
        print(
            "You have entered an incorrect password ; you are now locked out of your account.\nPlease contact your customer care for support.")
        return False


def new_user_credentials():
    # This function implements the add_a_new_user function.
    # The function was created to prevent the repeat of code.
    username = input('Username -> Total length of the username should be between 5 and 21.\n'
                     'It should start with a letter.\n'
                     'Contains only letters, numbers, underscores and dashes.\n'
                     'Username: ')
    while not check_if_valid_username(username):
        print("You have entered an invalid username. Please try again")
        username = input('Username: ')
    email = input('Email: ')
    while not check_if_valid_email(email):
        print('You have entered an invalid email. Please try again.')
        email = input('Email: ')
    password = input('Password -> 1. Should have at least one number;\n'
                     ' 2. Should have at least one uppercase and one lowercase character.\n'
                     '3. Should have at least one special symbol.(No dashes or underscores)\n'
                     '4. Should be between 6 to 20 characters long: \n'
                     'Password: ')
    while not check_if_valid_password(password):
        print("Please enter e valid password")
        password = input('Password: ')
    firstname = input('First name: ')
    while not check_if_valid_name(firstname):
        print("Please enter e valid name")
        firstname = input('First name: ')
    lastname = input('Last name: ')
    while not check_if_valid_name(lastname):
        print("Please enter e valid last name")
        lastname = input('Last name: ')
    dob = input('DOB (%d-%m-%Y): ')
    while not check_if_valid_date(dob):
        print("Please enter e valid date of birth.")
        dob = input('DOB (%d-%m-%Y): ')
    city = input('City: ')
    while not check_if_valid_name(city):
        print("Please enter e valid city")
        city = input('City: ')
    if does_user_exist('Email', email) or does_user_exist('Username', username):
        duplicate = True
    else:
        duplicate = False
        add_a_new_user(firstname, lastname, email, dob, city, username, password)
    return duplicate


#  Decorator for regex
def regex_decorator(func):
    def wrapper(*args):
        pattern = re.compile(func())
        # searching regex
        match = re.search(pattern, *args)
        # validating conditions
        if match:
            return True
        else:
            return False
    return wrapper


"""
Password should have at least one number
Should have at least one uppercase and one lowercase character
Should have at least one special symbol.(No dashes or underscores)
Should be between 6 to 20 characters long
"""
@regex_decorator
def check_if_valid_password():
    reg = "^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!#%*?&]{6,20}$"
    return reg


"""
Total length of the username should be between 5 and 21
It should start with a letter
Contains only letters, numbers, underscores and dashes
"""
@regex_decorator
def check_if_valid_username():
    reg = "^[A-Za-z][A-Za-z0-9_-]{4,20}$"
    return reg

"""
The first name, last name and city should contain only letter, in length 2 to 25
"""
@regex_decorator
def check_if_valid_name():
    reg = "^[A-Za-z]{2,25}$"
    return reg

"""
The email should be a subset of ASCII characters separated into two parts by @ symbol
It can contain letters and numbers
"""
@regex_decorator
def check_if_valid_email():
    reg = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    return reg

# date format should be dd-mm-yyyy
@regex_decorator
def check_if_valid_date():
    reg = '^(0[1-9]|[12][0-9]|3[01])[- /.](0[1-9]|1[012])[- /.](19|20)\d\d$'
    return reg

