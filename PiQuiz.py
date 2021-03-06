#!/usr/bin/env python3.7

##### GLOBAL VARIABLES #####
PROG_VERSION = "1.0.2"
PROG_NAME = "PiQuiz"
SETTINGS = []
LCD = None
GPIO_INIT_DONE = False
BUTTON_WAIT_DELAY = 0.3
LED_WAIT_DELAY = 2
BOUNCETIME=500
MySQL_DB_Conn = None
##### CLI OPT VARIABLES ####
DEBUG_ENABLED = False
NON_GPIO_ENABLED = False
TEST_MODE_ENABLED = False
##### RESULT VARIABLES ####
NOOFQCORRECT = 0
NOOFQINCORRECT = 0
NOOFQASKED = 0
##### INPUT TUPLES ####
NON_GPIO_INPUT_OPTIONS = "A", "B", "C", "D";
GPIO_INPUT_OPTIONS = []
###########################


try:
    import sys
    import time
    import os
    import argparse
    import configparser
    import RPi.GPIO as GPIO
    import Adafruit_CharLCD
    from ScrollLCD import scroll
    import mysql.connector
    from mysql.connector import Error
    import random
except ImportError as e:
    print("ERROR: Error loading module: " + str(e))
    sys.exit(1)

def handle_args():
    global DEBUG_ENABLED
    global NON_GPIO_ENABLED
    global TEST_MODE_ENABLED

    parser = argparse.ArgumentParser(description=PROG_NAME + ' - Multiple choice Question generator using a LCD screen and RPIs GPIO inputs.')

    parser.add_argument('-v','--version',help='show version info and exit.', action="store_true")
    parser.add_argument('-n','--non-gpio',help='do not use RPIs GPIO inputs/outputs. Instead use keyboard for input and print output to CLI.', action="store_true")
    parser.add_argument('-t','--test',help='run tests to ensure RPIs GPIO inputs/outputs are working correctly.', action="store_true")
    parser.add_argument('-d','--debug',help='print debug info to CLI.', action="store_true")
    args = parser.parse_args()
    ## process arg values from CLI ##
    if args.version:
        print(PROG_NAME + " v" + PROG_VERSION + " running on Python " + sys.version)
        sys.exit(0)
    if args.debug:
        print("DEBUG ENABLED")
        DEBUG_ENABLED = True
    if args.non_gpio:
        if DEBUG_ENABLED:
            print("NON-GPIO OPTION SELECTED")
        NON_GPIO_ENABLED = True
    if args.test:
        if DEBUG_ENABLED:
            print("TEST MODE SELECTED")
        TEST_MODE_ENABLED = True

def load_settings():
    global DEBUG_ENABLED
    global SETTINGS
    global GPIO_INPUT_OPTIONS
    settings_filename = 'settings.ini'
    if DEBUG_ENABLED:
        print("Settings file: " + settings_filename)
    config = configparser.ConfigParser()
    config.read(settings_filename)
    # If settings file is missing, print error to CLI and Exit
    if not config.sections():
        print("ERROR: "+ settings_filename + " is missing. Exiting...")
        sys.exit(1)
    # File exists, check sections and options are present. If not, print error to CLI and Exit.
    for section in [ 'MySQL', 'GPIO' ]:

        if not config.has_section(section):
            print("ERROR: Missing settings section: " + section +". Please check " + settings_filename + ". Exiting...")
            sys.exit(1)

        if section == 'MySQL':
            for option in [ 'Host', 'User', 'Password', 'Database' ]:
                if not config.has_option(section, option):
                    print("ERROR: Missing MySQL settings option: " + option +". Please check " + settings_filename + ". Exiting...")
                    sys.exit(1)
        elif section == 'GPIO':
            for option in [ 'OPTION_A_BUTTON_GPIO', 'OPTION_B_BUTTON_GPIO', 'OPTION_C_BUTTON_GPIO', 'OPTION_D_BUTTON_GPIO',
                            'QUIT_BUTTON_GPIO' ,'LCD_RS','LCD_EN','LCD_D4','LCD_D5','LCD_D6','LCD_D7','LCD_COLUMNS','LCD_ROWS',
                            'RED_LED','GREEN_LED']:
                if not config.has_option(section, option):
                    print("ERROR: Missing GPIO settings option: " + option +". Please check " + settings_filename + ". Exiting...")
                    sys.exit(1)
    # Settings file sections and options valid. Now retrieve/parse values and store in global dict
    try:
        SETTINGS = {'MYSQL_HOSTNAME':config.get('MySQL', 'Host'),
                    'MYSQL_DATABASE':config.get('MySQL', 'Database'),
                    'MYSQL_USER':config.get('MySQL', 'User'),
                    'MYSQL_PASSWORD':config.get('MySQL', 'Password'),
                    'GPIO_OPTION_A_BUTTON':config.getint('GPIO', 'OPTION_A_BUTTON_GPIO'),
                    'GPIO_OPTION_B_BUTTON':config.getint('GPIO', 'OPTION_B_BUTTON_GPIO'),
                    'GPIO_OPTION_C_BUTTON':config.getint('GPIO', 'OPTION_C_BUTTON_GPIO'),
                    'GPIO_OPTION_D_BUTTON':config.getint('GPIO', 'OPTION_D_BUTTON_GPIO'),
                    'GPIO_QUIT_BUTTON':config.getint('GPIO', 'QUIT_BUTTON_GPIO'),
                    'GPIO_LCD_RS':config.getint('GPIO', 'LCD_RS'),
                    'GPIO_LCD_EN':config.getint('GPIO', 'LCD_EN'),
                    'GPIO_LCD_D4':config.getint('GPIO', 'LCD_D4'),
                    'GPIO_LCD_D5':config.getint('GPIO', 'LCD_D5'),
                    'GPIO_LCD_D6':config.getint('GPIO', 'LCD_D6'),
                    'GPIO_LCD_D7':config.getint('GPIO', 'LCD_D7'),
                    'GPIO_LCD_COLUMNS':config.getint('GPIO', 'LCD_COLUMNS'),
                    'GPIO_LCD_ROWS':config.getint('GPIO', 'LCD_ROWS'),
                    'GPIO_RED_LED':config.getint('GPIO', 'RED_LED'),
                    'GPIO_GREEN_LED':config.getint('GPIO', 'GREEN_LED')}
        #Populate GPIO Input Options dict based on keys,values in SETTINGS dict
        for key, value in SETTINGS.items():
            if 'OPTION' in key:
                GPIO_INPUT_OPTIONS.append(value)
        if DEBUG_ENABLED:
            print("INFO: Settings file contains following keys & values:")
            for key, value in SETTINGS.items():
                print(key, value)
            print("INFO: GPIO Input Options list contains following keys & values:")
            print(GPIO_INPUT_OPTIONS)

    except ValueError as e:
        print("ERROR: Unable to parse values from settings file: \n" + str(e))
        sys.exit(1)

def init_gpio_lcd():
    try:
        global SETTINGS
        global LCD
        global DEBUG_ENABLED
        global GPIO_INIT_DONE
        global BOUNCETIME
        # Set GPIO reference mode
        GPIO.setmode(GPIO.BCM)
        # Setup GPIO LEDs
        GPIO.setup(SETTINGS['GPIO_RED_LED'], GPIO.OUT, initial=GPIO.LOW)
        GPIO.setup(SETTINGS['GPIO_GREEN_LED'], GPIO.OUT, initial=GPIO.LOW)
        # Setup GPIO Buttons
        GPIO.setup(SETTINGS['GPIO_OPTION_A_BUTTON'], GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        GPIO.setup(SETTINGS['GPIO_OPTION_B_BUTTON'], GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        GPIO.setup(SETTINGS['GPIO_OPTION_C_BUTTON'], GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        GPIO.setup(SETTINGS['GPIO_OPTION_D_BUTTON'], GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        GPIO.setup(SETTINGS['GPIO_QUIT_BUTTON'], GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        # Add event triggers to Button GPIO channels
        GPIO.add_event_detect(SETTINGS['GPIO_OPTION_A_BUTTON'], GPIO.RISING, bouncetime=BOUNCETIME)
        GPIO.add_event_detect(SETTINGS['GPIO_OPTION_B_BUTTON'], GPIO.RISING, bouncetime=BOUNCETIME)
        GPIO.add_event_detect(SETTINGS['GPIO_OPTION_C_BUTTON'], GPIO.RISING, bouncetime=BOUNCETIME)
        GPIO.add_event_detect(SETTINGS['GPIO_OPTION_D_BUTTON'], GPIO.RISING, bouncetime=BOUNCETIME)
        GPIO.add_event_detect(SETTINGS['GPIO_QUIT_BUTTON'], GPIO.RISING, bouncetime=BOUNCETIME)
        # Retrieve LCD GPIO pins from global SETTINGS dict.
        lcd_rs = SETTINGS['GPIO_LCD_RS']
        lcd_en = SETTINGS['GPIO_LCD_EN']
        lcd_d4 = SETTINGS['GPIO_LCD_D4']
        lcd_d5 = SETTINGS['GPIO_LCD_D5']
        lcd_d6 = SETTINGS['GPIO_LCD_D6']
        lcd_d7 = SETTINGS['GPIO_LCD_D7']
        lcd_columns = SETTINGS['GPIO_LCD_COLUMNS']
        lcd_rows = SETTINGS['GPIO_LCD_ROWS']
        # Create LCD object
        LCD = Adafruit_CharLCD.Adafruit_CharLCD(lcd_rs, lcd_en, lcd_d4, lcd_d5, lcd_d6, lcd_d7,
                           lcd_columns, lcd_rows)
        GPIO_INIT_DONE = True
        if DEBUG_ENABLED:
            print(str(LCD))
            print("GPIO INIT COMPLETE? = ", GPIO_INIT_DONE)

    except:
        print("ERROR: Unexpected error during INIT GPIO LCD:", sys.exc_info())
        GPIO.cleanup()
        sys.exit(1)

def run_gpio_tests():
    try:
        global SETTINGS
        global BUTTON_WAIT_DELAY
        global LCD
        print("====== RUNNING GPIO TESTS======")
        print("====== TEST 1: LEDs ======")
        print("------ Switching on RED LED.")
        GPIO.output(SETTINGS['GPIO_RED_LED'], GPIO.HIGH)
        time.sleep(2)
        print("------ Switching on GREEN LED.")
        GPIO.output(SETTINGS['GPIO_GREEN_LED'], GPIO.HIGH)
        time.sleep(2)
        print("------ Switching off LEDs.")
        GPIO.output(SETTINGS['GPIO_RED_LED'], GPIO.LOW)
        GPIO.output(SETTINGS['GPIO_GREEN_LED'], GPIO.LOW)
        print("====== TEST 2: BUTTONs ======")
        print("------ Press each button until all are tested successfully. Ctrl-C to move on to next TEST.")
        BUTTON_A_TESTED_OK=False
        BUTTON_B_TESTED_OK=False
        BUTTON_C_TESTED_OK=False
        BUTTON_D_TESTED_OK=False
        BUTTON_QUIT_TESTED_OK=False
        try:
            while (BUTTON_A_TESTED_OK == False or BUTTON_B_TESTED_OK == False or
                   BUTTON_C_TESTED_OK == False or BUTTON_D_TESTED_OK == False or
                   BUTTON_QUIT_TESTED_OK == False):
                if GPIO.event_detected(SETTINGS['GPIO_OPTION_A_BUTTON']):
                    print("Button A Pressed")
                    BUTTON_A_TESTED_OK=True
                if GPIO.event_detected(SETTINGS['GPIO_OPTION_B_BUTTON']):
                    print("Button B Pressed")
                    BUTTON_B_TESTED_OK=True
                if GPIO.event_detected(SETTINGS['GPIO_OPTION_C_BUTTON']):
                    print("Button C Pressed")
                    BUTTON_C_TESTED_OK=True
                if GPIO.event_detected(SETTINGS['GPIO_OPTION_D_BUTTON']):
                    print("Button D Pressed")
                    BUTTON_D_TESTED_OK=True
                if GPIO.event_detected(SETTINGS['GPIO_QUIT_BUTTON']):
                    print("Quit Button Pressed")
                    BUTTON_QUIT_TESTED_OK=True
        except KeyboardInterrupt:
            print("Leaving TEST 2. Moving onto next TEST...")
        if LCD == None:
            print("ERROR: LCD has not been setup correctly. Please check your config. Exiting...")
            raise Exception('LCD_SETUP_ERROR')
        print("====== TEST 3: LCD ======")
        print("------ Now writing TEST message to LCD screen.")
        lcd_text = "!!! LCD TEST !!!"
        scroll(LCD,lcd_text,1,1,2)
        LCD.clear()
        print("====== ALL TESTS COMPLETE ======")
    except:
        print("ERROR: Unexpected error during GPIO TESTS:", sys.exc_info())
        GPIO.cleanup()
        sys.exit(1)

def establish_db_connection():
    try:
        global MySQL_DB_Conn
        global DEBUG_ENABLED
        global SETTINGS

        if DEBUG_ENABLED:
            print("INFO: Attempting to connect to " + SETTINGS['MYSQL_DATABASE'] + '@' + SETTINGS['MYSQL_HOSTNAME'] +
                  " using '" + SETTINGS['MYSQL_USER'] + "' as the User and '" + SETTINGS['MYSQL_PASSWORD'] + "' as the Password.")

        MySQL_DB_Conn = mysql.connector.connect(host=SETTINGS['MYSQL_HOSTNAME'],
                                       database=SETTINGS['MYSQL_DATABASE'],
                                       user=SETTINGS['MYSQL_USER'],
                                       password=SETTINGS['MYSQL_PASSWORD'])
        if MySQL_DB_Conn.is_connected():
            print('Connected to ' + SETTINGS['MYSQL_DATABASE'] + '@' + SETTINGS['MYSQL_HOSTNAME'] +  ' MySQL database.')

    except Error as e:
        print("ERROR: Error occurred while trying to connect to the MySQL database: ", str(e))
        sys.exit(1)

def output(output_text,pause1=False, pause2=False, rep=False, printToConsole=False):
    global NON_GPIO_ENABLED
    global LCD

    PAUSE_NEXT = 1
    PAUSE_REP = 1
    REPETITIONS = 2

    if pause1: PAUSE_NEXT = pause1
    if pause2: PAUSE_REP = pause2
    if rep: REPETITIONS = rep

    if NON_GPIO_ENABLED or printToConsole:
        print(output_text)
    if not NON_GPIO_ENABLED:
        scroll(LCD,output_text,PAUSE_NEXT,PAUSE_REP,REPETITIONS)

def display_score(noqcorrect,noqincorrect,noqasked):
    msg = "GAME OVER! Here are the results..."
    output(msg,1,2,1,True)
    msg = "You were asked " + str(noqasked) + " question(s)"
    output(msg,1,2,1,True)
    if noqasked > 0:
        msg = "You got " + str(noqcorrect) + " question(s) CORRECT!"
        output(msg,1,2,1,True)
        msg = "You got " + str(noqincorrect) + " question(s) WRONG"
        output(msg,1,2,1,True)

def output_question(qno,qtext):
    msg = ("Q" + str(qno) + ": " + qtext)
    output(msg,1,2,2,False)

def input_answer(question_id):
    global NON_GPIO_ENABLED
    global NON_GPIO_INPUT_OPTIONS
    global GPIO_INPUT_OPTIONS
    global LCD
    answers_input_dict = {}

    cursor = MySQL_DB_Conn.cursor(named_tuple=True)
    query = ("""SELECT a.answer_id,a.answer_text
                FROM answers a
                WHERE a.question_id = """ + str(question_id))
    if DEBUG_ENABLED:
        print("INFO: Query to get answers for question_id " + str(question_id) + " is:")
        print(query)
    try:
        #Execute query
        cursor.execute(query)
        #Fetch all rows from executed query
        answers = cursor.fetchall()
    except:
        print("ERROR: Unexpected error retrieving answers to Question ID: " + str(question_id), sys.exc_info())
        MySQL_DB_Conn.close()
        GPIO.cleanup
        sys.exit(1)
    #Retrieve row count from executed query and store in variable
    anscnt = cursor.rowcount
    if DEBUG_ENABLED:
        print("INFO: Available answers row count: " + str(anscnt))
    if anscnt == 0:
        print("ERROR: No answers available for Question ID: " + str(question_id) + ". Please check MySQL Database and try again.")
        MySQL_DB_Conn.close()
        GPIO.cleanup()
        sys.exit(1)
    #Now shuffle the answers for a bit of fun
    random.shuffle(answers)
    #Map answers to Inputs
    for i,row in enumerate(answers):
        if NON_GPIO_ENABLED:
            answers_input_dict[i] = {
                    'answer_id': row.answer_id,
                    'answer_text': str(row.answer_text),
                    'input': NON_GPIO_INPUT_OPTIONS[i]}
        else:
            answers_input_dict[i] = {
                    'answer_id': row.answer_id,
                    'answer_text': str(row.answer_text),
                    'input': GPIO_INPUT_OPTIONS[i]}
    #Display answers to Player
    popts = "a", "b", "c", "d";
    msg = ''
    for i,row in enumerate(answers_input_dict):
        msg = msg + popts[i] + ") " + answers_input_dict[i]['answer_text'] + " "
    output(msg,1,2,2,False)
    #Get player input
    user_input = None
    while True:
        if NON_GPIO_ENABLED:
            user_input = input("Press the letter on your keyboard corresponding to the answer you wish to select and press ENTER...").upper()
        else:
            LCD.message("Choose your \nanswer...")
            while True:
                if GPIO.event_detected(SETTINGS['GPIO_OPTION_A_BUTTON']):
                    user_input = GPIO_INPUT_OPTIONS[0]
                    break
                if GPIO.event_detected(SETTINGS['GPIO_OPTION_B_BUTTON']):
                    user_input = GPIO_INPUT_OPTIONS[1]
                    break
                if GPIO.event_detected(SETTINGS['GPIO_OPTION_C_BUTTON']):
                    user_input = GPIO_INPUT_OPTIONS[2]
                    break
                if GPIO.event_detected(SETTINGS['GPIO_OPTION_D_BUTTON']):
                    user_input = GPIO_INPUT_OPTIONS[3]
                    break
                if GPIO.event_detected(SETTINGS['GPIO_QUIT_BUTTON']):
                    global NOOFQASKED
                    global NOOFQCORRECT
                    global NOOFQINCORRECT
                    display_score(NOOFQCORRECT,NOOFQINCORRECT,NOOFQASKED)
                    output("Thanks for playing. Good-Bye!",1,2,1,True)
                    MySQL_DB_Conn.close()
                    GPIO.cleanup()
                    sys.exit(0)
        #Validate user input
        for i,row in enumerate(answers_input_dict):
            if user_input == answers_input_dict[i]['input']:
                msg = ("You selected Answer " + popts[i].upper() + " (" + answers_input_dict[i]['answer_text'] + ")")
                output(msg,1,2,1,False)
                return answers_input_dict[i]['answer_id']
        #If answer from user not valid, display appropiate message
        msg = ("Input invalid. Try again")
        output(msg,1,2,1,True)

def illuminate_led(gpio_output,sleep_time):
    GPIO.output(gpio_output, GPIO.HIGH)
    time.sleep(sleep_time)
    GPIO.output(gpio_output, GPIO.LOW)

def main():
    global MySQL_DB_Conn
    global LCD
    #First create cursor object from current My SQL DB connection.
    cursor = MySQL_DB_Conn.cursor(named_tuple=True)
    #Define query that will check Questions table for non-archived questions.
    query = ("""SELECT q.question_id,q.question_text,answer_id
                FROM questions q
                WHERE q.archived = 0""")
    try:
        #Execute query
        cursor.execute(query)
        #Fetch all rows from executed query
        availq = cursor.fetchall()
    except:
        print("ERROR: Unexpected error retrieving non-archived questions:", sys.exc_info())
        MySQL_DB_Conn.close()
        GPIO.cleanup
        sys.exit(1)
    #Retrieve row count from executed query and store in variable
    availqcnt = cursor.rowcount
    if DEBUG_ENABLED:
        print("INFO: Non-archived questions row count: " + str(availqcnt))
    if availqcnt == 0:
        print("ERROR: No non-archived questions available in MySQL Database. Please check MySQL Database and try again.")
        MySQL_DB_Conn.close()
        GPIO.cleanup()
        sys.exit(1)
    #### MAIN GAME LOGIC STARTS HERE ####
    try:
        global PROG_NAME
        global PROG_VERSION
        global SETTINGS
        global LED_WAIT_DELAY
        global NON_GPIO_ENABLED
        msg = ("Welcome to " + PROG_NAME + ". v" + PROG_VERSION)
        output(msg,1,2,1,True)
        #Use the randint method to randomly choose a number between 1 and the total # of avail q's in the database
        noofselq = random.randint(1,availqcnt)
        #Prepare and display message to player.
        msg = (str(availqcnt) + " question(s) available. " + str(noofselq) + " question(s) selected.")
        output(msg,1,2,1,False)
        #Randomly choose x number of questions to pose to player and store as separate list to iterate through.
        selected_questions = random.sample(availq, noofselq)
        if DEBUG_ENABLED:
            print("Question(s) selected:")
            print(str(selected_questions))
        output("Let's begin!",1,2,1,False)
        global NOOFQASKED
        global NOOFQCORRECT
        global NOOFQINCORRECT
        try:
            q = 0
            for row in selected_questions:
                NOOFQASKED = NOOFQASKED + 1
                q = q + 1
                # Output current Question to Player either on LCD or CLI (if non-GPIO mode is enabled)
                output_question(q,row.question_text)
                # Grab answers to current question, pose them to Player and return Player's selected Answer ID from the function
                chosenanswerid = input_answer(row.question_id)
                # Validate answer from Player vs right answer
                if chosenanswerid == row.answer_id:
                    if NON_GPIO_ENABLED == False:
                        illuminate_led(SETTINGS['GPIO_GREEN_LED'], LED_WAIT_DELAY)
                    output("You are CORRECT!",1,2,1,False)
                    NOOFQCORRECT = NOOFQCORRECT + 1
                else:
                    if NON_GPIO_ENABLED == False:
                        illuminate_led(SETTINGS['GPIO_RED_LED'], LED_WAIT_DELAY)
                    output("Sorry, you are INCORRECT!",1,2,1,False)
                    NOOFQINCORRECT = NOOFQINCORRECT + 1
        except KeyboardInterrupt:
            display_score(NOOFQCORRECT,NOOFQINCORRECT,NOOFQASKED)
            output("Thanks for playing. Good-Bye!",1,2,1,True)
            MySQL_DB_Conn.close()
            GPIO.cleanup()
            sys.exit(0)
        # GAME OVER. Show final score on LCD screen (if GPIO is enabled) and also print to CLI.
        display_score(NOOFQCORRECT,NOOFQINCORRECT,NOOFQASKED)
        output("Thanks for playing. Good-Bye!",1,2,1,True)
    except KeyboardInterrupt:
        print("ERROR: Keyboard Interrupt detected. Exiting...")
        LCD.clear()
        MySQL_DB_Conn.close()
        GPIO.cleanup
        sys.exit(1)

if __name__ == "__main__":
    # Check command line arguments and handle accordingly
    handle_args()
    # Load MySQL, GPIO and other settings from settings.ini file
    load_settings()
    # Init GPIO & LCD
    if not NON_GPIO_ENABLED:
        if DEBUG_ENABLED:
            print("INFO: Enter INIT GPIO & LCD Function")
        init_gpio_lcd()
        if DEBUG_ENABLED:
            print("INFO: Left INIT GPIO & LCD Function")
    # If '-t, --test' CLI arg provided, run GPIO Input/Output tests
    if TEST_MODE_ENABLED:
        if NON_GPIO_ENABLED:
            print("ERROR: Test Mode cannot be run if Non-GPIO mode enabled.")
            sys.exit(1)
        if DEBUG_ENABLED:
            print("INFO: Enter GPIO TESTS Function")
        run_gpio_tests()
        if DEBUG_ENABLED:
            print("INFO: Left GPIO TESTS Function. Program exiting normally.")
        GPIO.cleanup()
        sys.exit(0)
    # Attempt to create a connection to the database
    if DEBUG_ENABLED:
        print("INFO: Enter ESTABLISH DB CONNECTION Function")
    establish_db_connection()
    if DEBUG_ENABLED:
        print("INFO: Left ESTABLISH DB CONNECTION Function")
    # Entering Main program code
    if DEBUG_ENABLED:
        print("INFO: Enter MAIN Function")
    main()
    if DEBUG_ENABLED:
        print("INFO: Left MAIN Function. Program exiting normally.")
    MySQL_DB_Conn.close()
    GPIO.cleanup()
    sys.exit(0)
