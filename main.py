from cli.cli import Commander
from cli.utils import show_welcome

if __name__ == "__main__":
    show_welcome()
    cmd = Commander()
    try:
        cmd.login()
        while True:
            cmd.run()
    except KeyboardInterrupt:
        print("Bye~")
