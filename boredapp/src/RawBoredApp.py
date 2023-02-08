"""

1. Generate random tasks to try when bored.

2. Feature: Allows user to save certain activities to a 'favourites' list and also view and delete them from the list.

4. Note: Passwords have been hashed using SHA-1 as they are entered into the Database - So only the user knows their
password.Stretch Goal: salt or pepper the hashed password - REMEMBER: Each time you query the password column you
need to hash the password value.

5. Option for user to reset password.

6. Add error handling, use all the different things taught: decorators, lambda, collections library etc.
7. Same for SQL, use indexing ,alias,SUBQUERY, UPDATE and other advanced.

8. Forgot password feature using SQL Update

9. User can save, view and delete items from their favourites list


"""

import mysql.connector
from config import USER, HOST, DATABASEPASSWORD,DATABASENAME
import json
import requests

APIurl = "http://www.boredapi.com/api/activity"


class DatabaseFunctions:

    def __int__(self):
        pass

    def connect_to_database(self):

        my_database = mysql.connector.connect(
            host=HOST,
            user=USER,
            password=DATABASEPASSWORD,
            auth_plugin='mysql_native_password',
            database=DATABASENAME
        )

        return my_database

    # Decorator for executing SQL query's

    def execute_database_query(self, query):

        database_connection = self.connect_to_database()

        my_cursor = database_connection.cursor(buffered=True)  # the cursor communicated with your mySQL server

        my_cursor.execute(query)

        database_connection.commit()
        my_cursor.close()
        database_connection.close()

        return "Query Successfully Executed"

    def create_new_user(self, FirstName, LastName, Email, DOB, City, Username, Password):

        query = """ INSERT INTO the_users 
        (FirstName, LastName, Email, DOB, City, Username, Password)
        VALUES
        ('{FIRSTNAME}', '{LASTNAME}', '{EMAIL}', str_to_date('{DOB}', '%d-%m-%Y'), '{CITY}', '{USERNAME}', SHA1('{PASSWORD}') )
        """.format(FIRSTNAME=FirstName, LASTNAME=LastName, EMAIL=Email, DOB=DOB, CITY=City, USERNAME=Username,
                   PASSWORD=Password)

        self.execute_database_query(query)
        return "New User Created"

    def save_activity_to_favourites(self, activity_ID, user_id):

        # Connect to API to get activity info
        url = "{}?key={}".format(APIurl, activity_ID)

        user = APIChooseActivity()
        activity = user.connect_to_api(url)
        activity_name = activity['activity']
        participant_number = activity['participants']
        price = activity['price']
        activity_type = activity['type']

        # Run query to save activity info
        query = """ INSERT INTO favourites 
                (activityID,  UserID, activity, participants, price, type)
                VALUES
                ('{ACTIVITYID}','{USERID}','{ACTIVITY}', '{PARTICIPANTS}', '{PRICE}', '{TYPE}');
                """.format(ACTIVITYID=activity_ID, USERID=user_id, ACTIVITY=activity_name,
                           PARTICIPANTS=participant_number, PRICE=price, TYPE=activity_type)

        self.execute_database_query(query)

        return "Your activity has been saved to your favourites! "

    def view_favourites(self, user_id):
        queryToGetFavouritesInformationByUserID = """ SELECT f.activity, f.participants, f.price, type FROM favourites f WHERE f.UserID = {USERID} """.format(
            USERID=user_id)

        queryToGetTotalNumberOfFavourites = """ SELECT COUNT(activityID) FROM favourites f WHERE f.UserID = {USERID} """.format(
            USERID=user_id)

        database_connection = self.connect_to_database()
        my_cursor = database_connection.cursor(buffered=True)  # the cursor communicated with your mySQL server
        my_cursor.execute(queryToGetFavouritesInformationByUserID)
        favourites_list = my_cursor.fetchall()

        my_cursor.execute(queryToGetTotalNumberOfFavourites)
        numberOfFavourites = my_cursor.fetchall()
        numberOfFavourites = numberOfFavourites[0][0]

        # database_connection.commit()
        my_cursor.close()
        database_connection.close()

        list_of_only_activity_names = []
        for favourites in favourites_list:
            list_of_only_activity_names.append(favourites[0])

        numbered_list_of_activities = []
        listNumber = 1
        for activity in list_of_only_activity_names:
            stuff = [listNumber, activity]
            numbered_list_of_activities.append(stuff)

            listNumber += 1

        return "You have {} activities in your Favourites. This is your favourites list: \n {}".format(
            numberOfFavourites, numbered_list_of_activities)

    def delete_from_favourites(self, row_number, user_id):

        queryToFindActivityID = """ SELECT activityID FROM favourites WHERE UserID = {USERID} LIMIT {ROWNUMBER},1 """.format(
            USERID=user_id, ROWNUMBER=row_number - 1)

        database_connection = self.connect_to_database()
        my_cursor = database_connection.cursor(buffered=True)  # the cursor communicated with your mySQL server
        my_cursor.execute(queryToFindActivityID)
        activity_ID = my_cursor.fetchall()

        queryToDeleteActivityFromFavourites = """ DELETE FROM favourites
                    WHERE activityID = {ACTIVITYID} and UserID = {USERID}""".format(ACTIVITYID=activity_ID[0][0],
                                                                                    USERID=user_id)

        self.execute_database_query(queryToDeleteActivityFromFavourites)

        return "Activity Deleted"

    def check_if_username_and_password_match(self, username_or_email_option, username_or_email_value, password_value):

        # This query checks if the email/username and password exist in one record.
        # It returns 1 if True(does exist) or 0 if False(doesn't exist)
        # Note it returns it like a tuple in a list [(0,)] or [(1,)] so we need to use indexing to get the numbers alone
        query = "SELECT(EXISTS(SELECT * FROM the_users WHERE {EmailOrUsernameOption} = '{EmailOrUsernameValue}' AND Password = SHA1('{PasswordValue}')))".format(
            EmailOrUsernameOption=username_or_email_option, EmailOrUsernameValue=username_or_email_value,
            PasswordValue=password_value)

        database_connection = self.connect_to_database()
        my_cursor = database_connection.cursor(buffered=True)  # the cursor communicated with your mySQL server
        my_cursor.execute(query)
        trueOrFalse = my_cursor.fetchall()

        database_connection.commit()
        my_cursor.close()
        database_connection.close()

        if trueOrFalse[0][0] == 1:  # if True
            print(self.successful_login_message(username_or_email_option, username_or_email_value, password_value))
            return True
        elif trueOrFalse[0][0] == 0:  # if False
            print(self.unsuccessful_login_message())
            return False

    def reset_password(self, user_ID, new_password):
        query = "UPDATE the_users SET the_users.Password = SHA1('{NEWPASSWORD}') WHERE UserID = '{USERID}')".format(
            USERID=user_ID, NEWPASSWORD=new_password)

        self.execute_database_query(query)

        return "Password has been reset"

    def successful_login_message(self, username_or_email_option, username_or_email_value, password_value):
        # This query gets the users first name whose login was successful.
        query = "SELECT u.FirstName FROM the_users u WHERE u.{EmailOrUsernameOption} = '{EmailOrUsernameValue}' AND u.Password = SHA1('{PasswordValue}')".format(
            EmailOrUsernameOption=username_or_email_option, EmailOrUsernameValue=username_or_email_value,
            PasswordValue=password_value)

        database_connection = self.connect_to_database()
        my_cursor = database_connection.cursor(buffered=True)  # the cursor communicated with your mySQL server
        my_cursor.execute(query)

        userFirstName = my_cursor.fetchall()

        return "Login Successful!! \nWelcome, {}.".format(userFirstName[0][0])

    def unsuccessful_login_message(self):
        return "Login Unsuccessful, please try again."

    def get_user_id(self, username_or_email_option, username_or_email_value, password_value):

        query = "SELECT u.UserID FROM the_users u WHERE u.{EmailOrUsernameOption} = '{EmailOrUsernameValue}' AND u.Password = SHA1('{PasswordValue}')".format(
            EmailOrUsernameOption=username_or_email_option, EmailOrUsernameValue=username_or_email_value,
            PasswordValue=password_value)

        database_connection = self.connect_to_database()
        my_cursor = database_connection.cursor(buffered=True)  # the cursor communicated with your mySQL server
        my_cursor.execute(query)

        userID = my_cursor.fetchall()

        return userID[0][0]

    def check_if_activity_is_in_favourites(self, activity_ID, user_id):
        query = "SELECT(EXISTS(SELECT * FROM favourites WHERE activityID = '{ACTIVITYID}' AND UserID = '{USERID}'))".format(
            ACTIVITYID=activity_ID, USERID=user_id)

        database_connection = self.connect_to_database()
        my_cursor = database_connection.cursor(buffered=True)  # the cursor communicated with your mySQL server
        my_cursor.execute(query)
        trueOrFalse = my_cursor.fetchall()

        if trueOrFalse[0][0] == 1:  # if True
            return True
        elif trueOrFalse[0][0] == 0:  # if False
            return False


class APIChooseActivity:

    def __int__(self):
        pass

    def connect_to_api(self, url):
        response = requests.get(url)
        dataResponse = response.text
        connection = json.loads(
            dataResponse)  # deserializing - turns json string into python dictionary that can be now accessed

        return connection

    def activity_based_on_random_selection(self):
        url = "{}/".format(APIurl)
        activity = self.connect_to_api(url)

        activity_ID = activity['key']

        return activity_ID

    def activity_based_on_budget_range(self, min_budget, max_budget):
        url = "{}?minprice={}&maxprice={}".format(APIurl, min_budget, max_budget)
        activity = self.connect_to_api(url)

        activity_ID = activity['key']

        return activity_ID

    def activity_based_on_number_of_participants(self, number_of_participants):
        url = "{}?participants={}".format(APIurl, number_of_participants)
        activity = self.connect_to_api(url)

        activity_ID = activity['key']

        return activity_ID

    def activity_based_on_activity_type(self, activity_type):
        url = "{}?type={}".format(APIurl, activity_type)
        activity = self.connect_to_api(url)

        activity_ID = activity['key']

        return activity_ID

    # display activity info, we can use if else statements to formate the string in certain ways depending on what the activity selection was based on
    def display_the_activity(self, activity_ID):
        url = "{}?key={}".format(APIurl, activity_ID)
        activity = self.connect_to_api(url)

        activity_name = activity['activity']
        participant_number = activity['participants']
        price = activity['price']
        activity_type = activity['type']
        activity_link = activity['link']

        if activity_link != "":  # if the link isn't empty; so there's a link available
            string = "Your activity is: {}, costs £{}, is a {} activity and can be done with {} participant/s. \n Link: {}".format(
                activity_name, price, activity_type, participant_number, activity_link)
        else:
            string = "Your activity is: {}, costs £{}, it is a {} activity and can be done by {} participant/s.".format(
                activity_name, price, activity_type, participant_number)

        return string


def main(userID):
    user = APIChooseActivity()

    activity_selection_choice = input(
        "Do you want your skill to be random, based on type, based on budget or based on the number of participants?")

    if activity_selection_choice == "random":
        activity_key = user.activity_based_on_random_selection()
        print(user.display_the_activity(activity_key))

    elif activity_selection_choice == "type":
        type = input("Activity type:")
        activity_key = user.activity_based_on_activity_type(type)
        print(user.display_the_activity(activity_key))

    elif activity_selection_choice == "budget":
        minprice = float(input("min price:"))
        maxprice = float(input("max price"))
        activity_key = user.activity_based_on_budget_range(minprice, maxprice)
        print(user.display_the_activity(activity_key))

    elif activity_selection_choice == "participants":
        noOfParticipants = input("How many participants?")
        activity_key = user.activity_based_on_number_of_participants(noOfParticipants)
        print(user.display_the_activity(activity_key))

    saveActivityOption = input("Would you like to save this activity?")

    user = DatabaseFunctions()
    if saveActivityOption == "yes":
        user = DatabaseFunctions()
        if user.check_if_activity_is_in_favourites(activity_ID=activity_key, user_id=userID):
            print("This activity is already in your favourites")
        elif not user.check_if_activity_is_in_favourites(activity_ID=activity_key, user_id=userID):
            print(user.save_activity_to_favourites(activity_ID=activity_key, user_id=userID))

    continueActivityHunt = input("Would you like to continue?")

    if continueActivityHunt == "yes":

        continueChoice = input("Would you like to view you favourite's or get a new activity?")
        if continueChoice == "favourites":
            print(user.view_favourites(userID))
            favourites_delete = input("Would you like to delete an activity from your favourites?")
            if favourites_delete == "yes":
                activity_row_number = int(input("Which number activity would you like to delete?"))
                print(user.delete_from_favourites(row_number=activity_row_number, user_id=userID))
                return

            elif favourites_delete == "no":
                return


        elif continueChoice == "activity":
            print(main(userID))


    elif continueActivityHunt == "no":
        return "Okay see ya"

    # print(user1.activity_based_on_random_selection())
    # print(user1.activity_based_on_activity_type("social"))
    # print(user1.activity_based_on_number_of_participants(1))
    # print(user1.activity_based_on_budget_range(0, 2))

    # print(user2.create_new_user("Daniellaj1","Omokore","jad1je@gmail.com", "27-11-1945", "London", "Jade1j1","JJs"))
    # print(user2.view_favourites(5))
    # print(user2.check_if_username_and_password_match("Username", "Yella", "Patella"))
    # print(user2.get_user_id("Username", "Yella", "Patella"))
    # print(user2.save_activity_to_favourites(activity_ID=, user_id=))
    # print(user2.delete_from_favourites(activity_ID=, user_id=))


# create a function that creates an object of the class you need to run functions of


# if __name__ == '__main__':
#    main()


def login_interface():
    login_method = input('How would you like to login? (Email/Username):')
    username_or_email_option = login_method.title()

    if username_or_email_option == 'Email' or 'Username':
        username_or_email_value = input('Enter your {}: '.format(username_or_email_option))
        password_value = input("Enter your password:")

    else:
        print('Please try again, choosing one of the options.')
        login_interface()
    print("Thank you. Checking your details...")

    user = DatabaseFunctions()
    user_id = user.get_user_id(username_or_email_option, username_or_email_value, password_value)

    if user.check_if_username_and_password_match(username_or_email_option, username_or_email_value,
                                                 password_value) is True:
        print(main(user_id))

    return "Thanks for using the BoredApp!"

#print(login_interface())
# user2 = DatabaseFunctions()

# print(user2.create_new_user("bOB", "Omokore", "BOB@gmail.com", "27-11-1945", "London", "BOB", "JJJJs"))
# print(user2.create_new_user("bagy", "js", "BOB1@gmail.com", "27-11-1945", "London", "BOmB", "yo"))
