from typer import Typer
from subprocess import Popen, PIPE

cli = Typer()


@cli.command()
def start():
    process = Popen(["reflex", "run"], shell=False)
    process.communicate()


@cli.command()
def migrate():
    process = Popen(["reflex", "migrate"], shell=False)
    process.communicate()


def main():
    cli()


if __name__ == "__main__":
    main()
