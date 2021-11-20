from pathmodels.base import CylanderBehaviourDir
import pathmodels.find
from pathlib import Path
from pprint import pprint


def main():
    p = Path(r"D:\pilot\data\proper")
    mouse_dirs = pathmodels.find.find_pilot_mouse_dirs(p)
    cylander_dirs = []
    for mouse_dir in mouse_dirs:
        for session_dir in mouse_dir.session_dirs.values():
            cylander_dir: CylanderBehaviourDir = session_dir.data_dirs[
                "cylander_behaviour"
            ]
            cylander_dir.tidy_dlc_output()


if __name__ == "__main__":
    main()
