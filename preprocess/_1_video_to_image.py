import pandas as pd
import os
import cv2

NAME_BATCH = "batch_2305"
ROOT = os.path.dirname(os.path.dirname(__file__))
DIR_SRC = os.path.join(ROOT, "modules", "ring_capture", "out", NAME_BATCH)
DIR_OUT = os.path.join(ROOT, "data", "cow100")
os.chdir(DIR_SRC)

# remove videos that are not complete
ls_rm = [f for f in os.listdir() if f.endswith("_1.mp4")]
for rm in ls_rm:
    os.remove(rm)

# use cv to extract first frame of each video (mp4)
ls_mp4 = [f for f in os.listdir() if f.endswith("_0.mp4")]
for i, name_mp4 in enumerate(ls_mp4):
    name_img = "img_1_%d.jpg" % i
    path_mp4 = os.path.join(DIR_SRC, name_mp4)
    path_img = os.path.join(DIR_OUT, "images", name_img)

    cap = cv2.VideoCapture(path_mp4)
    ret, frame = cap.read()
    try:
        cv2.imwrite(path_img, frame)
    except:
        print("Error: %s" % name_mp4)
    cap.release()