#!/usr/local/bin/python3.7

PIQUIZ_VERSION = "0.1.0"

def load_deps():
    # Check all required modules are installed in Python env. If not, alert user and exit with error code.
    pipmodules = ['os','argparse','sys','getopt','RPi.GPIO']
    for module in pipmodules:
        try:
            module_obj = __import__(module)
            globals()[module] = module_obj            
        except ImportError:
            print("ERROR: Missing Python Module: " + module + ". Required modules are: " + str(pipmodules) + ".")
            sys.exit(1)

def handle_args():
    parser = argparse.ArgumentParser(description='PiQuiz - Multiple choice Question generator using a LCD screen and RPIs GPIO inputs.')
    
    parser.add_argument('-v','--version',help='show Version info and exit.', action="store_true")
    parser.add_argument('-k','--keyboard',help='use keyboard instead of RPIs GPIO inputs.', action="store_true")
    parser.add_argument('-t','--test',help='run tests to ensure RPIs GPIO inputs/outputs are working correctly.', action="store_true")
    args = parser.parse_args()
    
    ## process arg values from CLI ##
    if args.version:
        print(os.path.basename(__file__) + " v" + PIQUIZ_VERSION)
        sys.exit(0)        
    if args.keyboard:
        print("KEYBOARD ENABLED")
    if args.test:
        print("TEST ENABLED")

if __name__ == "__main__":
    # First, check and load all required modules
    load_deps()
    # Then, check command line arguments and handle accordingly
    handle_args()
    sys.exit(0)
    #main(sys.argv[1:])
