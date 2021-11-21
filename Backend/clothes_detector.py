import cv2
import json
import ntpath
import os
import numpy as np
from tqdm import tqdm
from detectron2 import model_zoo
from detectron2.config import get_cfg
from detectron2.engine import DefaultPredictor
from detectron2.utils.logger import setup_logger
from observable import Observable

setup_logger()


class ClothesDetector(Observable):

    def __init__(self, observer, path_images_info, path_processed_dataset, path_clothes_images,
                 path_clothes_ann, path_model_weights):

        self.social_event_images_info = path_images_info
        self.path_processed_dataset = path_processed_dataset
        self.path_clothes_dataset = path_clothes_images
        self.path_clothes_ann = path_clothes_ann
        self.path_model_weights = path_model_weights

        """Set the configuration of model"""

        cfg = get_cfg()
        cfg.merge_from_file(model_zoo.get_config_file("COCO-InstanceSegmentation/mask_rcnn_R_50_FPN_3x.yaml"))
        cfg.DATASETS.TRAIN = ()
        cfg.DATASETS.TEST = ()
        cfg.DATALOADER.NUM_WORKERS = 2
        cfg.MODEL.WEIGHTS = self.path_model_weights
        cfg.SOLVER.IMS_PER_BATCH = 8
        cfg.SOLVER.BASE_LR = 0.00025  # pick a good LR
        cfg.SOLVER.MAX_ITER = 300  # 300 iterations seems good enough for this toy dataset; you will need to train longer for a practical dataset
        cfg.SOLVER.STEPS = []  # do not decay learning rate
        cfg.MODEL.ROI_HEADS.BATCH_SIZE_PER_IMAGE = 128  # faster, and good enough for this toy dataset (default: 512)
        cfg.MODEL.ROI_HEADS.NUM_CLASSES = 13
        cfg.MODEL.ROI_HEADS.SCORE_THRESH_TEST = 0.7  # Confidence threshold for predictions

        self.predictor = DefaultPredictor(cfg)
        self.attach(observer)

    def attach(self, observer):
        self._observers.append(observer)

    def detach(self, observer):
        self._observers.remove(observer)

    def notify(self, current_img_nbr, total_img_nbr):
        """Trigger an update in each subscriber."""
        for observer in self._observers:
            observer.update_clothes_detection_progress(current_img_nbr, total_img_nbr)

    def __create_required_folders(self, queries):
        """Create required folders"""
        if not os.path.isdir(self.path_processed_dataset):
            os.mkdir(self.path_processed_dataset)

        # Train folders
        if not os.path.isdir(self.path_clothes_dataset):
            os.mkdir(self.path_clothes_dataset)
        for i in queries:
            path_dir_class = os.path.join(self.path_clothes_dataset, i)
            if not os.path.isdir(path_dir_class):
                os.mkdir(path_dir_class)

    def __read_annotation_file(self):
        """Function to load the images names and class from the json file"""
        list_images_paths = []
        list_images_classes = []
        f = open(self.social_event_images_info)
        data = json.load(f)
        queries = []
        for image_id in data:
            list_images_paths.append(data[image_id]['path'])
            list_images_classes.append(data[image_id]['category'])
            if data[image_id]['query'] not in queries:
                queries.append(data[image_id]['query'])
        f.close()
        return list_images_paths, list_images_classes, queries

    def clothes_detection(self):
        """Function to preprocess and save the datasets"""
        np.random.seed(1995)  # For reproducibility

        list_path_images, list_images_classes, queries = self.__read_annotation_file()
        self.__create_required_folders(queries)

        # Read and preprocess all the images inside the dataset
        list_pp_train_paths = []
        list_pp_train_classes = []
        list_pp_train_clothes = []
        list_nbr_clothes_for_image = [0] * len(list_path_images)
        for i in tqdm(range(len(list_path_images))):
            path_img = list_path_images[i]
            img_class = list_images_classes[i]
            img_name = ntpath.basename(path_img)
            img = cv2.imread(path_img)
            if img is not None:
                res = self.predictor(img)
                instances = res["instances"].to("cpu")
                # Check if the model found clothes in the image
                if len(instances):
                    path_pp_dataset = self.path_clothes_dataset
                    list_pp_paths = list_pp_train_paths
                    list_pp_classes = list_pp_train_classes
                    list_pp_clothes = list_pp_train_clothes
                    # Use the instance segmentation masks to crop the clothes area
                    for pred_mask, pred_box, pred_clothes, j in zip(instances.pred_masks, instances.pred_boxes,
                                                                    instances.pred_classes.numpy(),
                                                                    range(1, len(instances))):
                        res_img = np.repeat(pred_mask.numpy()[:, :, None], 3, axis=-1) * img
                        w = int(pred_box[2] - pred_box[0])
                        h = int(pred_box[3] - pred_box[1])
                        y = int(pred_box[1])
                        x = int(pred_box[0])
                        crop_img = res_img[y:y + h, x:x + w]
                        # Save the preprocessed image in the folder dedicated to its class
                        path_pp = os.path.join(path_pp_dataset, queries[img_class],
                                               str(os.path.splitext(img_name)[0]) + f"-{j}.png")
                        list_nbr_clothes_for_image[i] = j
                        list_pp_paths.append(path_pp)
                        list_pp_classes.append(img_class)
                        list_pp_clothes.append(pred_clothes)  # Clothes class predicted by mask-r-cnn
                        cv2.imwrite(path_pp, crop_img)

            self.notify(i, len(list_path_images))

        self.__save_annotation_file(list_pp_train_paths, list_pp_train_classes, queries, list_pp_train_clothes,
                                    self.path_clothes_ann)
        self.__save_clothes_nbr_per_image(list_path_images, list_nbr_clothes_for_image)

    @staticmethod
    def __save_clothes_nbr_per_image(list_path_images, clothes_nbr):
        with open("datasets/tmp_name/images_inf.json", 'r+') as images_inf:
            data = json.load(images_inf)
            for i in range(len(list_path_images)):
                name = ntpath.basename(list_path_images[i]).split(".")[0]
                data[name]['clothes_nbr'] = str(clothes_nbr[i])
                images_inf.seek(0)
                json.dump(data, images_inf, indent=4)
                images_inf.truncate()

    @staticmethod
    def __save_annotation_file(path_list, classes_list, queries, clothes_list, path_ann):
        # Save the annotation file
        file_string = ""
        for i in range(len(path_list)):
            file_string += path_list[i] + "," + str(queries[classes_list[i]]) + "," + str(
                clothes_list[i]) + "\n"
        with open(path_ann, "w") as f:
            f.write(file_string)


