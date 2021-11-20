from dlc_tools.freeze_detect import detect_freezes
from dlc_tools.video import freeze_annotations, save_anotated_video
from pathmodels.base.data_dirs import CylanderBehaviourDir
from pathmodels.pilot.mouse_dir import PilotMouseDir
from pathmodels.find import find_pilot_mouse_dirs
from pathlib import Path
import numpy as np
import pandas as pd


def main():
    p = Path(r"E:\pilot\data\proper")
    SESSIONS = ["day3-test1", "day4-test2"]
    mouse_dirs = find_pilot_mouse_dirs(p)
    for mouse_dir in mouse_dirs:
        print(mouse_dir.mouse.name)
        for session_dir_name in SESSIONS:
            session_dir = mouse_dir.session_dirs[session_dir_name]
            cylander_dir: CylanderBehaviourDir = session_dir.data_dirs[
                "cylander_behaviour"
            ]
            if not cylander_dir.has_exports():
                continue
            trajectory_path = cylander_dir.dlc_trajectory_file
            freezes = pd.read_hdf(trajectory_path)["freeze"].values
            freezes = freeze_annotations(freezes)
            outpath = str(cylander_dir.export_dir / "freeze_video.avi")
            inpath = str(cylander_dir.raw_video_file)
            save_anotated_video(
                source_video_path=inpath, outfile_path=outpath, annotations=freezes
            )


if __name__ == "__main__":
    main()
