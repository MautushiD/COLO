# coding=utf-8
# Copyright 2023 The NicheSquad Team.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"https://huggingface.co/datasets/Howuhh/nle_hf_dataset/blob/main/nle_hf_dataset.py"
"https://huggingface.co/datasets/vivos/blob/main/vivos.py"  # audio
"""
Documentation:
- datasets in lightining
https://lightning.ai/docs/pytorch/stable/notebooks/lightning_examples/text-transformers.html
- how to use datasets

"""

import os
import json
import datasets

CITATION = """Das, M., G. Ferreira, and C.P.J. Chen. (2024)"""
VERSION = datasets.Version("1.0.0")


def get_coco(setname, split):
    """
    setname: 1a_angle_t2s, 1b_angle_s2t, 2_light, 3_breed, 4_all
    split: train, test
    """
    path = os.path.join(setname, split, "coco.json")
    return path


def get_imgdir(setname, split):
    """
    setname: 1a_angle_t2s, 1b_angle_s2t, 2_light, 3_breed, 4_all
    split: train, test
    """
    path = os.path.join(setname, split)
    return path


class COLODatasets(datasets.GeneratorBasedBuilder):
    BUILDER_CONFIGS = [
        datasets.BuilderConfig(
            name="0_all",
            version=VERSION,
            description="Including top-down and side-view images with pre-defined train-test split",
        ),
        datasets.BuilderConfig(
            name="1_top",
            version=VERSION,
            description="Top-down images with pre-defined train-test split, and also splits for different lighting conditions",
        ),
        datasets.BuilderConfig(
            name="2_side",
            version=VERSION,
            description="Side view images with pre-defined train-test split, and also splits for different lighting conditions",
        ),
        datasets.BuilderConfig(
            name="3_external",
            version=VERSION,
            description="Images captured from external sources, which have lower angle and different lighting conditions",
        ),
        datasets.BuilderConfig(
            name="a1_t2s",
            version=VERSION,
            description="For testing the model generalization from top-down to side-view images",
        ),
        datasets.BuilderConfig(
            name="a2_s2t",
            version=VERSION,
            description="For testing the model generalization from side-view to top-down images",
        ),
        datasets.BuilderConfig(
            name="b_light",
            version=VERSION,
            description="For testing the model generalization from daylight condition to indoor lightning and NIR images",
        ),
        datasets.BuilderConfig(
            name="c_external",
            version=VERSION,
            description="For testing the model generalization from 0_all to 3_external",
        ),
    ]

    def _info(self):
        return datasets.DatasetInfo(
            description=self.config.description,
            features=datasets.Features(
                {
                    "image": datasets.Image(),
                    "width": datasets.Value("int64"),
                    "height": datasets.Value("int64"),
                    "n_cows": datasets.Value("int64"),
                    "annotations": datasets.Sequence(
                        {
                            "id": datasets.Value("int64"),
                            "image_id": datasets.Value("int64"),
                            "category_id": datasets.Value("int64"),
                            "iscrowd": datasets.Value("int64"),
                            "area": datasets.Value("float64"),
                            "bbox": datasets.Sequence(
                                datasets.Value("float64"), length=4
                            ),
                            "segmentation": datasets.Sequence(
                                datasets.Sequence(datasets.Value("int64"))
                            ),
                        }
                    ),
                    "image_id": datasets.Value("int64"),
                    "filename": datasets.Value("string"),
                }
            ),
            homepage="github.com/niche-squad",
            citation=CITATION,
        )

    def _split_generators(self, dl_manager):
        setname = self.config.name
        if setname == "1_top" or setname == "2_side":
            return [
                datasets.SplitGenerator(
                    name=datasets.Split("daylight"),
                    gen_kwargs={
                        "path_label": dl_manager.download(
                            get_coco(setname, "daylight")
                        ),
                        "images": dl_manager.iter_files(
                            get_imgdir(setname, "daylight")
                        ),
                    },
                ),
                datasets.SplitGenerator(
                    name=datasets.Split("indoorlight"),
                    gen_kwargs={
                        "path_label": dl_manager.download(
                            get_coco(setname, "indoor-light")
                        ),
                        "images": dl_manager.iter_files(
                            get_imgdir(setname, "indoor-light")
                        ),
                    },
                ),
                datasets.SplitGenerator(
                    name=datasets.Split("infrared"),
                    gen_kwargs={
                        "path_label": dl_manager.download(
                            get_coco(setname, "infrared")
                        ),
                        "images": dl_manager.iter_files(
                            get_imgdir(setname, "infrared")
                        ),
                    },
                ),
                datasets.SplitGenerator(
                    name=datasets.Split.TRAIN,
                    gen_kwargs={
                        "path_label": dl_manager.download(get_coco(setname, "train")),
                        "images": dl_manager.iter_files(get_imgdir(setname, "train")),
                    },
                ),
                datasets.SplitGenerator(
                    name=datasets.Split.TEST,
                    gen_kwargs={
                        "path_label": dl_manager.download(get_coco(setname, "test")),
                        "images": dl_manager.iter_files(get_imgdir(setname, "test")),
                    },
                ),
            ]
        else:
            return [
                datasets.SplitGenerator(
                    name=datasets.Split.TRAIN,
                    gen_kwargs={
                        "path_label": dl_manager.download(get_coco(setname, "train")),
                        "images": dl_manager.iter_files(get_imgdir(setname, "train")),
                    },
                ),
                datasets.SplitGenerator(
                    name=datasets.Split.TEST,
                    gen_kwargs={
                        "path_label": dl_manager.download(get_coco(setname, "test")),
                        "images": dl_manager.iter_files(get_imgdir(setname, "test")),
                    },
                ),
            ]

    def _generate_examples(self, path_label, images):
        """
        images: list of filenames
            filename example: "1a_angle_t2s/train/000000000139.jpg"
        """
        labels = COCO(path_label)
        for filename in images:
            # if the file is coco.json and not an image, skip
            if not filename.endswith(".jpg"):
                continue
            # if the file is not in the json, skip
            img = labels.get_img_info(filename)
            if img is None:
                continue
            img_id = img["id"]
            img_w, img_h = img["width"], img["height"]
            # read the image into bytes by the filenamt
            bytes_img = open(filename, "rb").read()
            ls_anns = labels.load_ann_by_id(img_id)
            record = {
                "image": {"path": filename, "bytes": bytes_img},
                "n_cows": len(ls_anns),
                "width": img_w,
                "height": img_h,
                "annotations": [
                    {
                        "id": ann["id"],
                        "image_id": ann["image_id"],
                        "category_id": ann["category_id"],
                        "iscrowd": ann["iscrowd"],
                        "area": ann["area"],
                        "bbox": ann["bbox"],
                        "segmentation": ann["segmentation"],
                    }
                    for ann in ls_anns
                ],
                "image_id": img_id,
                "filename": os.path.basename(filename),
            }
            yield filename, record


class COCO:
    def __init__(self, filename):
        with open(filename) as f:
            data = json.load(f)
        self.imgs = data["images"]
        self.anns = data["annotations"]
        self.cats = data["categories"]
        self.licenses = data["licenses"]

    def load_ann_by_id(self, img_id):
        ls = [ann for ann in self.anns if ann["image_id"] == img_id]
        return ls

    def get_img_info(self, filename):
        # cut the filename from the path
        imagename = os.path.basename(filename)
        for img in self.imgs:
            if img["file_name"] == imagename:
                return img
        return None
