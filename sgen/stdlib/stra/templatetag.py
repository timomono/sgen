from sgen.stdlib.pyrender.avoid_escape import AvoidEscape


def trans(key: str):
    return AvoidEscape(f'[[trans (key:"{key}")]]')
