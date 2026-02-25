import os


def is_process_running(pid):
    if os.name == "posix":
        try:
            os.kill(pid, 0)
            return True
        except OSError:
            return False
    else:
        import subprocess

        output = subprocess.check_output(
            f'tasklist /fi "PID eq {pid}"',
            shell=True,
            encoding="utf-8",
        )
        return str(pid) in output
