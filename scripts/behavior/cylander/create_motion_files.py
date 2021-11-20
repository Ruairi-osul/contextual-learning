import dlc_tools.tidy_trajectory
from pathmodels.base.data_dirs import CylanderBehaviourDir
from pathmodels.pilot.mouse_dir import PilotMouseDir
from pathmodels.find import find_pilot_mouse_dirs
from pathlib import Path
import numpy as np


def main():
    p = Path(r"D:\pilot\data\proper")
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
            df = dlc_tools.tidy_trajectory.tidy_dlc_trajectories(
                df=df, bodyparts=["left_ear", "right_ear", "tail"]
            )
            df = df.assign(
                motion=lambda x: dlc_tools.tidy_trajectory.calculate_motion(
                    x, estimator=np.median, frame_col="frame"
                )
            )
            dlc_tools.tidy_trajectory.save_hdf(df, trajectory_path)


if __name__ == "__main__":
    main()
