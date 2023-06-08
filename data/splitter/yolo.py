"""
Folder structure:

root/
    data.yaml
    images/
        img_1_13_jpg.rf.d69528304f2d10b633c6d94982185cb2.jpg
        img_2_13_jpg.rf.d69528304f2d10b633c6d94982185cb2.jpg
        ...
    labels/
        img_1_13_jpg.rf.d69528304f2d10b633c6d94982185cb2.txt
        img_2_13_jpg.rf.d69528304f2d10b633c6d94982185cb2.txt
        ...
    train/
        images/
            ...
        labels/
            ...
    val/
        images/
            ...
        labels/
            ...
    test/
        images/
            ...
        labels/
            ...
"""

import os
import shutil
import random

from .splitter import Splitter


class YOLO_Splitter(Splitter):
    def __init__(
        self,
        path_root: str,
        classes: list,
        ratio_train: float = 0.64,
        ratio_val: float = 0.16,
        ratio_test: float = 0.2,
    ):
        super().__init__(path_root, ratio_train, ratio_val, ratio_test)
        self.classes = classes

    def read_dataset(self):
        path_yaml = os.path.join(self.path_root, "data.yaml")
        f = open(path_yaml, "w")
        return f

    def get_ids(self):
        # from img_1_13_jpg.rf.jpg
        # to img_1_13_jpg.rf
        ls_imagefiles = os.listdir(os.path.join(self.path_root, "images"))
        ls_ids = [f[:-4] for f in ls_imagefiles if f.endswith(".jpg")]
        return ls_ids

    def shuffle_train_test(self):
        random.shuffle(self.ids)
        n = len(self.ids)
        n_train = int(self.ratio_train * n)
        n_val = int(self.ratio_val * n)
        # assignment
        self.id_train = self.ids[:n_train]
        self.id_val = self.ids[n_train : n_train + n_val]
        self.id_test = self.ids[n_train + n_val :]

    def write_dataset(self):
        self._handle_folders()
        self._write_yaml(classes=self.classes)
        self._copy_images_labels()

    def _handle_folders(self):
        for s in ["train", "val", "test"]:
            if not os.path.exists(os.path.join(self.path_root, s)):
                os.mkdir(os.path.join(self.path_root, s))
                os.mkdir(os.path.join(self.path_root, s, "images"))
                os.mkdir(os.path.join(self.path_root, s, "labels"))

    def _write_yaml(self, classes: list):
        self.config.write(
            f"""
                train: {os.path.join(self.path_root, "train", "images")}
                val: {os.path.join(self.path_root, "val", "images")}
                test: {os.path.join(self.path_root, "test", "images")}
                nc: {len(classes)}
                names: {classes}
            """
        )
        self.config.close()

    def _copy_images_labels(self):
        for s in ["train", "val", "test"]:
            ls_ids = getattr(self, f"id_{s}")
            dir_img = os.path.join(self.path_root, s, "images")
            dir_label = os.path.join(self.path_root, s, "labels")
            for id in ls_ids:
                # copy images
                path_img = os.path.join(self.path_root, "images", f"{id}.jpg")
                path_img_out = os.path.join(self.path_root, s, "images", f"{id}.jpg")
                shutil.copy(path_img, path_img_out)
                # copy labels
                path_label = os.path.join(self.path_root, "labels", f"{id}.txt")
                path_label_out = os.path.join(self.path_root, s, "labels", f"{id}.txt")
                shutil.copy(path_label, path_label_out)
