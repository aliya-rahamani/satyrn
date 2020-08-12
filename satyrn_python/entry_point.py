import getopt
import multiprocessing
import os
import sys
import time
import webbrowser
import zipfile

from cheroot.wsgi import Server as WSGIServer, PathInfoDispatcher

from .app import create_app
from .interpreter import Interpreter


def start_ui(url, port, interpreter, quiet):
    if not os.path.exists(os.path.dirname(os.path.abspath(__file__)) + "/satyrn_python/static/"):
        if not quiet:
            print("Unzipping static files...")
        with zipfile.ZipFile(os.path.dirname(os.path.abspath(__file__)) + "/static.zip",
                             'r') as zipped_file:
            zipped_file.extractall(os.path.dirname(os.path.abspath(__file__)) + "/static")

    openurl = "localhost" if url == "0.0.0.0" else url

    def delayed_browser_open():
        time.sleep(3)

        webbrowser.open("http://" + openurl + ":" + str(port) + "/#loaded")

    if not quiet:
        print("Initializing CherryPy server...")

    os.environ["FLASK_APP"] = "satyrnUI.satyrnUI"
    os.environ["FLASK_ENV"] = "production"

    d = PathInfoDispatcher({'/': create_app(interpreter)})
    server = WSGIServer((url, port), d)

    try:
        p = multiprocessing.Process(target=delayed_browser_open)
        p.start()

        if not quiet:
            print("Hosting at http://" + openurl + ":" + str(port) + "/#loaded")

        server.start()
    except KeyboardInterrupt:
        if not quiet:
            print("Stopping CherryPy server...")

        server.stop()

        if not quiet:
            print("Stopped")


def start_cli(interpreter):
    interpreter.run()


def main():
    interpreter = Interpreter()
    cli_mode = False
    url = "0.0.0.0"
    port = 20787

    arguments = sys.argv[1:]

    quiet = False

    for opt in arguments:
        if opt == "cli":
            cli_mode = True
        if opt == "ui":
            cli_mode = False
        if opt in ("q", "quiet", "-q", "--quiet"):
            quiet = True

    if not quiet:
        with open(os.path.abspath(__file__)[:(-1 * len(os.path.basename(__file__)))] + "/asciiart.txt") as asciiart:
            print("".join(asciiart.readlines()))

        print("Thank you for using Satyrn! \nFor issues and updates visit https://GitHub.com/CharlesAverill/satyrn\n")

    if cli_mode:
        start_cli(interpreter)
    else:
        opts, args = getopt.getopt(arguments, "p:hq", ["port=", "hidden", "quiet"])

        for opt, arg in opts:
            if opt in ("-p", "--port"):
                port = int(arg[1:])
            if opt in ("-h", "--hidden"):
                url = "127.0.0.1"
        start_ui(url, port, interpreter, quiet)
