# Copyright (C) 2022 Daniel Boxer
# See __init__.py and LICENSE for more information

from .utils import get_recent_path


def add_recent(project_path):
    path = get_recent_path()
    recent_projects = get_recent()
    if len(recent_projects) > 7:
        recent_projects.append(project_path)
        with path.open("w") as f:
            for line in recent_projects[1:]:
                f.write(line + "\n")
    else:
        with path.open("a") as f:
            f.write(str(project_path) + "\n")


def get_recent():
    path = get_recent_path()
    recent_projects = []
    if path.is_file():
        with path.open() as f:
            for line in f:
                line = line.strip()
                if line != "":
                    recent_projects.append(line)
    return recent_projects
