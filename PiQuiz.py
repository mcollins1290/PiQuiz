#!/usr/local/bin/python3.7

##### GLOBAL VARIABLES #####
PROG_VERSION = "0.1.0"
PROG_NAME = "PiQuiz"
SETTINGS = []
##### CLI OPT VARIABLES ####
DEBUG_ENABLED = False
NON_GPIO_ENABLED = False
TEST_MODE_ENABLED = False
###########################

def load_deps():
    # Check all required modules are installed in Python env. If not, alert user and exit with error code.
    pipmodules = ['sys','os','argparse','configparser','RPi.GPIO']
    for module in pipmodules:
        try:
            module_obj = __import__(module)
            globals()[module] = module_obj            
        except ImportError:
            print("ERROR: Missing Python Module: " + module + ". Required modules are: " + str(pipmodules) + ".")
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
        print(PROG_NAME + " v" + PROG_VERSION)
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
            for option in [ 'OPTION_A_BUTTON_GPIO', 'OPTION_B_BUTTON_GPIO', 'OPTION_C_BUTTON_GPIO', 'OPTION_D_BUTTON_GPIO', 'QUIT_BUTTON_GPIO' ]:
                if not config.has_option(section, option):
                    print("ERROR: Missing GPIO settings option: " + option +". Please check " + settings_filename + ". Exiting...")
                    sys.exit(1)
    # Settings file sections and options valid. Now retrieve/check values and store in global dict
    try:        
        SETTINGS = {'MYSQL_HOSTNAME':config.get('MySQL', 'Host'),
                    'MYSQL_DATABASE':config.get('MySQL', 'Database'),
                    'MYSQL_USER':config.get('MySQL', 'User'),
                    'MYSQL_PASSWORD':config.get('MySQL', 'Password'),
                    'GPIO_A_BUTTON':config.getint('GPIO', 'OPTION_A_BUTTON_GPIO'),
                    'GPIO_B_BUTTON':config.getint('GPIO', 'OPTION_B_BUTTON_GPIO'),
                    'GPIO_C_BUTTON':config.getint('GPIO', 'OPTION_C_BUTTON_GPIO'),
                    'GPIO_D_BUTTON':config.getint('GPIO', 'OPTION_D_BUTTON_GPIO'),
                    'GPIO_QUIT_BUTTON':config.getint('GPIO', 'QUIT_BUTTON_GPIO')}
        if DEBUG_ENABLED:
            print("Settings file contains following keys & values:")
            for key, value in SETTINGS.items():
                print(key, value)

    except ValueError as e:
        print("ERROR: Invalid values for options in settings file: \n" + str(e))
        sys.exit(1)
        
if __name__ == "__main__":
    # First, check and load all required modules
    load_deps()
    # Then, check command line arguments and handle accordingly
    handle_args()
    # Now we load MySQL, GPIO and other settings from settings.ini file
    load_settings()
    
    sys.exit(0)
