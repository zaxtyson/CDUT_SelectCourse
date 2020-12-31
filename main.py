from cli.cli import Commander
from cli.utils import show_welcome, set_console_style

if __name__ == "__main__":
    set_console_style()
    show_welcome()
    cmd = Commander()
    try:
        cmd.login()
        while True:
            cmd.run()
    except KeyboardInterrupt:
        print("Bye~")
