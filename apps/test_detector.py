import sys
import os
from pathlib import Path
import pandas as pd
import numpy as np

from detectTools import Detector
from detectTools import cropSquareCVtoPIL

class CustomDetector(Detector):

    """def __init__(self, yolo_model, device=None):
        if not callable(yolo_model):
            raise TypeError("yolo_model must be callable")

        self.device = device
        self.yolo = yolo_model
        print(f"Using custom detector: {type(yolo_model).__name__}")
    """

    def allBoxDetections(self, filename_or_imagecv):
        try:
            results = self.yolo(filename_or_imagecv, device=self.device)
        except FileNotFoundError:
            return [], [], [], 0, []
        except Exception as err:
            print(err)
            return [], [], [], 0, []

        r = results[0].cpu()

        imagecv = r.orig_img
        detection = r.numpy().boxes

        # No detections
        if not len(detection.cls):
            return [], [], [], 0, []

        boxes = detection.xyxy  # shape (N,4)
        classes = detection.cls.astype(int)  # shape (N,)

        # categories: 1=animal, 2=person, 3=vehicle, 0=empty
        categories = classes + 1

        croppedimages = []
        for i, cls in enumerate(classes):
            if cls == 0:  # animal
                crop = cropSquareCVtoPIL(imagecv, boxes[i].copy())
                croppedimages.append(crop)
            else:
                croppedimages.append(None)

        # animal count
        animal_count = np.sum(classes == 0)

        # human boxes
        human_mask = classes == 1
        if np.any(human_mask):
            humanboxes = boxes[human_mask]
        else:
            humanboxes = []

        return croppedimages, categories, boxes, animal_count, humanboxes

# DF, MDS, DFbsMDS, DFMDS, MDR
# DF
# self.yolo = YOLOEnsemble(DFYOLO_WEIGHTS, imgszA=DFYOLO_WIDTH, thresA=DFYOLO_THRES)
# MDS,
# self.yolo = YOLOEnsemble(MDSYOLO_WEIGHTS, imgszA=MDSYOLO_WIDTH, thresA=MDSYOLO_THRES)
# DFbsMDS,
# self.yolo = YOLOEnsemble(DFYOLO_WEIGHTS, MDSYOLO_WEIGHTS, imgszA=DFYOLO_WIDTH, imgszB=MDSYOLO_WIDTH,
#                             thresA=DFYOLO_THRES, thresB=MDSYOLO_THRES, backstop=True)
#  DFMDS,
#    self.yolo = YOLOEnsemble(DFYOLO_WEIGHTS, MDSYOLO_WEIGHTS, imgszA=DFYOLO_WIDTH, imgszB=MDSYOLO_WIDTH,
#                             thresA=DFYOLO_THRES, thresB=MDSYOLO_THRES, backstop=False)
# MDR
#    self.yolo = MDRedwood(MDRYOLO_WEIGHTS, MDRYOLO_WIDTH, MDRYOLO_THRES, device=device)

class CustomDetector2(CustomDetector):

    def __init__(self, yolo_model, device=None):
        if not callable(yolo_model):
            raise TypeError("yolo_model must be callable")

        self.device = device
        self.yolo = yolo_model
        print(f"Using custom detector: {type(yolo_model).__name__}")


# ####################################################################################
# main
# ####################################################################################

if __name__ == "__main__":

    if len(sys.argv) != 3:
        print("Usage: python testDetector.py <IMAGEPATH> <CSVFILENAME>")
        sys.exit(1)

    # Añadir path del proyecto
    curdir = os.path.abspath(os.path.dirname(sys.argv[0]))
    sys.path.append(curdir + '/../')

    from detectTools import Detector  # asegúrate que el fichero se llama detector.py

    # -------------------------
    # CARGAR IMÁGENES
    # -------------------------
    testdir = sys.argv[1]

    filenames = sorted(
        [str(f) for f in Path(testdir).rglob('*.[Jj][Pp][Gg]')] +
        [str(f) for f in Path(testdir).rglob('*.[Jj][Pp][Ee][Gg]')] +
        [str(f) for f in Path(testdir).rglob('*.[Bb][Mm][Pp]')] +
        [str(f) for f in Path(testdir).rglob('*.[Tt][Ii][Ff]')] +
        [str(f) for f in Path(testdir).rglob('*.[Gg][Ii][Ff]')] +
        [str(f) for f in Path(testdir).rglob('*.[Pp][Nn][Gg]')]
    )

    print(f"{len(filenames)} images found")

    # -------------------------
    # INICIALIZAR DETECTOR
    # -------------------------
    detector_name = "DF"   # Opciones: DF, MDS, DFbsMDS, DFMDS, MDR
    detector = CustomDetector(name=detector_name)

    # -------------------------
    # DETECCIÓN
    # -------------------------
    results_list = []

    for i, filename in enumerate(filenames):
        print(f"Processing {i+1}/{len(filenames)}: {filename}")

        croppedimages, categories, boxes, count, humanboxes = detector.allBoxDetections(filename)

        # Si no hay detecciones
        if len(categories) == 0:
            print("No detections")
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

        # Iterar sobre todas las detecciones
        for j in range(len(categories)):
            results_list.append({
                "filename": filename,
                "category": int(categories[j]),
                "xmin": float(boxes[j][0]),
                "ymin": float(boxes[j][1]),
                "xmax": float(boxes[j][2]),
                "ymax": float(boxes[j][3]),
                "animal_count": int(count),
                "num_humans": len(humanboxes) if isinstance(humanboxes, np.ndarray) else 0
            })

    # -------------------------
    # GUARDAR CSV
    # -------------------------
    df = pd.DataFrame(results_list)
    df.to_csv(sys.argv[2], index=False)

    print("Done, results saved in " + sys.argv[2])
