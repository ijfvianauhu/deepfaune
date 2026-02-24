import sys
import os
from pathlib import Path
import pandas as pd
import numpy as np

from detectTools import cropSquareCVtoPIL
from detectTools import YOLOEnsemble, MDRedwood   # ajusta si cambia el import
from detectTools import DFYOLO_WEIGHTS, MDSYOLO_WEIGHTS, MDRYOLO_WEIGHTS
from detectTools import DFYOLO_WIDTH, MDSYOLO_WIDTH, MDRYOLO_WIDTH

from test_detector import CustomDetector2   # ajusta si está en otro fichero

# ---------------------------------------------------------
# CONFIGURACIÓN
# ---------------------------------------------------------

DETECTOR_CONFIGS = {
    "DF": {
        "builder": lambda thres: YOLOEnsemble(
            DFYOLO_WEIGHTS,
            imgszA=DFYOLO_WIDTH,
            thresA=thres
        )
    },
    "MDS": {
        "builder": lambda thres: YOLOEnsemble(
            MDSYOLO_WEIGHTS,
            imgszA=MDSYOLO_WIDTH,
            thresA=thres
        )
    },
    "DFMDS": {
        "builder": lambda thres: YOLOEnsemble(
            DFYOLO_WEIGHTS,
            MDSYOLO_WEIGHTS,
            imgszA=DFYOLO_WIDTH,
            imgszB=MDSYOLO_WIDTH,
            thresA=thres,
            thresB=thres,
            backstop=False
        )
    },
    "MDR": {
        "builder": lambda thres: MDRedwood(
            MDRYOLO_WEIGHTS,
            MDRYOLO_WIDTH,
            thres,
            device=None
        )
    }
}

THRESHOLDS = [0.1, 0.25, 0.5, 0.6, 0.75, 0.9]

# ---------------------------------------------------------
# MAIN
# ---------------------------------------------------------

if len(sys.argv) != 3:
    print("Usage: python run_all_detectors.py <IMAGEPATH> <OUTPUT_FOLDER>")
    sys.exit(1)

image_dir = sys.argv[1]
output_dir = sys.argv[2]
os.makedirs(output_dir, exist_ok=True)

# Cargar imágenes
filenames = sorted(
    [str(f) for f in Path(image_dir).rglob('*.[Jj][Pp][Gg]')] +
    [str(f) for f in Path(image_dir).rglob('*.[Jj][Pp][Ee][Gg]')] +
    [str(f) for f in Path(image_dir).rglob('*.[Bb][Mm][Pp]')] +
    [str(f) for f in Path(image_dir).rglob('*.[Tt][Ii][Ff]')] +
    [str(f) for f in Path(image_dir).rglob('*.[Gg][Ii][Ff]')] +
    [str(f) for f in Path(image_dir).rglob('*.[Pp][Nn][Gg]')]
)

print(f"{len(filenames)} images found")


# ---------------------------------------------------------
# LOOP SOBRE MODELOS Y THRESHOLDS
# ---------------------------------------------------------

for detector_name, config in DETECTOR_CONFIGS.items():
    for thres in THRESHOLDS:

        print(f"\n==============================")
        print(f"Running {detector_name} with threshold={thres}")
        print(f"==============================")

        # Crear modelo con threshold específico
        yolo_model = config["builder"](thres)

        detector = CustomDetector2(
            yolo_model=yolo_model,
            device=None
        )

        results_list = []

        for i, filename in enumerate(filenames):
            print(f"[{detector_name} | {thres}] {i+1}/{len(filenames)}")

            croppedimages, categories, boxes, count, humanboxes = \
                detector.allBoxDetections(filename)

            if len(categories) == 0:
                results_list.append({
                    "filename": filename,
                    "category": 0,
                    "xmin": None,
                    "ymin": None,
                    "xmax": None,
                    "ymax": None,
                    "animal_count": 0,
                    "num_humans": 0
                })
                continue

            for j in range(len(categories)):
                results_list.append({
                    "filename": filename,
                    "category": int(categories[j]),
                    "xmin": float(boxes[j][0]),
                    "ymin": float(boxes[j][1]),
                    "xmax": float(boxes[j][2]),
                    "ymax": float(boxes[j][3]),
                    "animal_count": int(count),
                    "num_humans": len(humanboxes)
                    if isinstance(humanboxes, np.ndarray) else 0,
                    "detector": detector_name,
                    "threshold": thres
                })

        # Guardar CSV por combinación
        output_csv = os.path.join(
            output_dir,
            f"results_{detector_name}_th{str(thres).replace('.', '_')}.csv"
        )

        df = pd.DataFrame(results_list)
        df.to_csv(output_csv, index=False)

        print(f"Saved: {output_csv}")

print("\nAll experiments finished.")