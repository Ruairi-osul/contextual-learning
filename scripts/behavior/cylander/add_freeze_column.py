import dlc_tools.tidy_trajectory
from dlc_tools.freeze_detect import detect_freezes
from pathmodels.base.data_dirs import CylanderBehaviourDir
from pathmodels.pilot.mouse_dir import PilotMouseDir
from pathmodels.find import find_pilot_mouse_dirs
from pathlib import Path
import numpy as np


def main():
    p = Path(r"E:\pilot\data\proper")
    mouse_dirs = find_pilot_mouse_dirs(p)
    for mouse_dir in mouse_dirs:
        for session_dir in mouse_dir.session_dirs.values():
            cylander_dir: CylanderBehaviourDir = session_dir.data_dirs[
                "cylander_behaviour"
            ]
            if not cylander_dir.has_exports():
                continue
            trajectory_path = cylander_dir.dlc_trajectory_file
            df = dlc_tools.tidy_trajectory.load_dlc_h5_file(trajectory_path)
            df = df.assign(
                freeze=lambda x: detect_freezes(
                    x["motion"], freeze_threshold=0.2, min_duration=45
                )
            )
            dlc_tools.tidy_trajectory.save_hdf(df, trajectory_path)


if __name__ == "__main__":
    main()
