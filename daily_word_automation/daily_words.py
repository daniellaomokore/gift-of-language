from datetime import datetime
import requests
import random


# from rebeccas pythonfile import login_interface


# User-defined exception
class ValueNotInTwentyFourHour(ValueError):
    # called if the time entered is not in 24hr time
    pass


def set_reminder_time():
    try:
        print("Please enter the time you would like your daily reminder in 24hr format.")
        reminderHour = int(input("Enter the Hour : "))
        reminderMin = int(input("Enter the Minute : "))

        if 24 < reminderHour < 1 and 00 < reminderMin < 1:
            raise ValueNotInTwentyFourHour

    except ValueNotInTwentyFourHour:
        print("Please enter your reminder time in 24hr format.")

    else:
        if reminderHour == datetime.datetime.now().hour and reminderMin == datetime.now().minute:  # If the current time is equal to the reminder time
            randomWordGenerator()


"""if login_interface() == True:  # if user successfully logs in
    set_reminder_time()        # let them set a time reminder for their random words

"""


# Documentation:
# I'm using this manual method below for the random word generator based on the words in our chosen api
# instead of using the random words library as :
# 1. A lot of the words don#t exist in the api we are using so the definition and examples etc can't be searched
# 2. The words it generates are extremely advanced english that i don't even know myself and aren't commonly used in day too day speaking

# GENERATING THE RANDOM WORD FOR USERS DAILY WORD
def randomWordGenerator():
    # Converting the text file of the dictionary words into a list of strings
    with open("daily_word_automation\english.txt", encoding="utf8") as wordDictionary:
        wordDictionaryList = []  # the wordDictionary in list form
        for line in wordDictionary:
            wordDictionaryList.append(line.strip)
        #  print(wordDictionaryList)    # the wordDictionary in list form

    # Total number of dictionary words
    dictionaryLength = len(wordDictionaryList)
    #  print(dictionaryLength)

    # generates a random number within the range of the index for the list of dictionary words
    randomDictIndex = random.randint(0, dictionaryLength - 1)
    #  print(randomDictIndex)

    # getting our random word
    randomWord = wordDictionaryList[int(randomDictIndex)]


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


searchAPIForRandomWord("water")
