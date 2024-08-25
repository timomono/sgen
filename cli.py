import sys
import cmds


class CommandNotFoundError(NotImplementedError):
    pass


class CommandNameDuplicateError(Exception):
    pass


def parseArg():
    cmd = sys.argv[1]
    return [command for command in cmds.commands if command.name == cmd]


def main():
    if len(sys.argv) == 1:
        raise CommandNotFoundError("Command not specified")
    cmd = parseArg()
    if len(cmd) == 0:
        raise CommandNotFoundError(f'Command "{sys.argv[1]}" not found')
    if len(cmd) != 1:
        raise CommandNameDuplicateError()
    cmd[0].run(sys.argv[2:])


if __name__ == "__main__":
    main()
