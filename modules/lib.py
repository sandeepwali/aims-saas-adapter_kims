import os
import datetime

def is_zip(path=""):
    return path.lower().endswith(".zip")


def is_csv(path=""):
    return path.lower().endswith(".csv")


def match_file(filename, starts=None, ends=None):
    does_start = filename.lower().startswith(starts.lower())
    does_end = filename.lower().endswith(ends.lower())
    return does_start and does_end


def append_timestamp(filename):
    """Append current timestamp to a filename before the extension."""
    name, ext = os.path.splitext(filename)
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{name}_{timestamp}{ext}"