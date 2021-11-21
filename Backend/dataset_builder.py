""" DatasetBuilder: aggregate utilities to build large images datasets"""

from __future__ import print_function
import os
import shutil
import cv2
import numpy as np
import matplotlib.pyplot as plt
import imageio
import json


class DatasetBuilder(object):
    """ Aggregate utilities to build large datasets (renaming files, spliting categories,
        creating labels, loading data...) """

    __merge_files_counter = 1
    __rename_files_counter = 1
    __data = {}
    __category_id = 0
    __labels = []

    def __init__(self):
        print("\nPreparing DatasetBuilder...")

    @staticmethod
    def check_folder_existence(folder_path, throw_error_if_no_folder=False, display_msg=True):
        """ check if a folder exists.
        If throw_error_if_no_folder = True and the folder does not exist:
            the method will print an error message and stop the program,
        Otherwise:
            the method will create the folder
        """
        if not os.path.exists(folder_path):
            if throw_error_if_no_folder:
                print("Error: Folder '" + folder_path + "' does not exist")
                exit()
            else:
                os.makedirs(folder_path)
                if display_msg:
                    print("Target folder '", folder_path, "' does not exist...")
                    print(" >> Folder created")

    @classmethod
    def rename_files(cls, source_folder, target_folder, extensions=('.jpg', '.jpeg', '.png')):
        """ list subfolders recursively and rename files according to
            the following the pattern: 1.jpg, 2.jpg..."""
        # check source_folder and target_folder:
        cls.check_folder_existence(source_folder, throw_error_if_no_folder=True)
        cls.check_folder_existence(target_folder, display_msg=False)
        if source_folder[-1] == "/":
            source_folder = source_folder[:-1]
        if target_folder[-1] == "/":
            target_folder = target_folder[:-1]

        # copy files and rename:
        print("Renaming files '", source_folder, "' files...")
        cls.__rename_files_counter = 1
        for filename in os.listdir(source_folder):
            if os.path.isdir(source_folder + '/' + filename):
                cls.rename_files(source_folder + '/' + filename, target_folder + '/' + filename, extensions=extensions)
            else:
                if extensions == '' and os.path.splitext(filename)[1] == '':
                    shutil.copy2(source_folder + "/" + filename, target_folder + "/" + str(cls.__rename_files_counter))
                    cls.__rename_files_counter += 1
                else:
                    for extension in extensions:
                        if filename.endswith(extension):
                            shutil.copy2(source_folder + "/" + filename,
                                         target_folder + "/" + str(cls.__rename_files_counter) + extension)
                            cls.__rename_files_counter += 1

    @classmethod
    def reshape_images(cls, source_folder, target_folder, height=128, width=128, extensions=('.jpg', '.jpeg', '.png')):
        """ copy images and reshape them"""

        # check source_folder and target_folder:
        cls.check_folder_existence(source_folder, throw_error_if_no_folder=True)
        cls.check_folder_existence(target_folder, display_msg=False)
        if source_folder[-1] == "/":
            source_folder = source_folder[:-1]
        if target_folder[-1] == "/":
            target_folder = target_folder[:-1]

        # read images and reshape:
        print("Resizing '", source_folder, "' images...")
        for filename in os.listdir(source_folder):
            if os.path.isdir(source_folder + '/' + filename):
                cls.reshape_images(source_folder + '/' + filename,
                                   target_folder + '/' + filename,
                                   height, width, extensions=extensions)
            else:
                if extensions == '' and os.path.splitext(filename)[1] == '':
                    shutil.copy2(source_folder + "/" + filename, target_folder + "/" + filename)
                    image = plt.imread(target_folder + "/" + filename, extensions)
                    image_resized = cv2.resize(image, dsize=(height, width), interpolation=cv2.INTER_CUBIC)
                    imageio.imwrite(target_folder + "/" + filename, image_resized)
                else:
                    for extension in extensions:
                        if filename.endswith(extension):
                            shutil.copy2(source_folder + "/" + filename, target_folder + "/" + filename)
                            image = plt.imread(target_folder + "/" + filename, extension)
                            image_resized = cv2.resize(image, dsize=(height, width), interpolation=cv2.INTER_CUBIC)
                            imageio.imwrite(target_folder + "/" + filename, image_resized)

    @classmethod
    def crop_images(cls, source_folder, target_folder, height=128, width=128,
                    extensions=('.jpg', '.jpeg', '.png')):
        """ copy images and center crop them"""

        # check source_folder and target_folder:
        cls.check_folder_existence(source_folder, throw_error_if_no_folder=True)
        cls.check_folder_existence(target_folder, display_msg=False)
        if source_folder[-1] == "/":
            source_folder = source_folder[:-1]
        if target_folder[-1] == "/":
            target_folder = target_folder[:-1]

        # read images and crop:
        print("Cropping '", source_folder, "' images...")
        for filename in os.listdir(source_folder):
            if os.path.isdir(source_folder + '/' + filename):
                cls.crop_images(source_folder + '/' + filename, target_folder + '/' + filename,
                                height, width, extensions=extensions)
            else:
                if extensions == '' and os.path.splitext(filename)[1] == '':
                    shutil.copy2(source_folder + "/" + filename, target_folder + "/" + filename)
                    image = cv2.imread(target_folder + "/" + filename)
                    [width_original, height_original, _] = image.shape
                    offset_w = (width_original - width) / 2
                    offset_h = (width_original - width) / 2
                    image_cropped = image[offset_w: width + offset_w, offset_h: height + offset_h, :]
                    imageio.imwrite(target_folder + "/" + filename, image_cropped)
                else:
                    for extension in extensions:
                        if filename.endswith(extension):
                            shutil.copy2(source_folder + "/" + filename,
                                         target_folder + "/" + filename)
                            image = cv2.imread(target_folder + "/" + filename)
                            [width_original, height_original, _] = image.shape
                            offset_w = (width_original - width) / 2
                            offset_h = (width_original - width) / 2
                            image_cropped = image[offset_w: width + offset_w, offset_h: height + offset_h, :]
                            imageio.imwrite(target_folder + "/" + filename, image_cropped)

    @classmethod
    def merge_folders(cls, source_folder, target_folder, output_file, extensions=('.jpg', '.jpeg', '.png')):
        """ merge images in separated folders in one single folder
            The images will be renamed"""

        # check source_folder and target_folder:
        cls.check_folder_existence(source_folder, throw_error_if_no_folder=True)
        cls.check_folder_existence(target_folder, display_msg=False)
        if source_folder[-1] == "/":
            source_folder = source_folder[:-1]
        if target_folder[-1] == "/":
            target_folder = target_folder[:-1]
        # copy files and rename:
        print("Merging '", source_folder, "' files...")
        for filename in os.listdir(source_folder):
            if os.path.isdir(source_folder + '/' + filename):
                cls.merge_folders(source_folder + '/' + filename, target_folder, output_file, extensions=extensions)
                cls.__category_id += 1
            else:
                if extensions == '' and os.path.splitext(filename)[1] == '':
                    shutil.copy2(source_folder + "/" + filename,
                                 target_folder + "/" + str(cls.__merge_files_counter).zfill(6))
                    cls.__merge_files_counter += 1
                else:
                    for extension in extensions:
                        if filename.endswith(extension):
                            shutil.copy2(source_folder + "/" + filename,
                                         target_folder + "/" + str(cls.__merge_files_counter).zfill(6) + extension)
                            cls.__save_info(source_folder, target_folder, filename, cls.__category_id, extension,
                                            output_file)
                            cls.__merge_files_counter += 1

    @classmethod
    def reset_dataset_builder_state(cls):
        cls.__data = {}
        cls.__merge_files_counter = 1
        cls.__category_id = 0

    @classmethod
    def __save_info(cls, source_folder, target_folder, old_filename, category_id, extension, output_file):
        """ Save the path and category of each renamed image in a json file """
        cls.__data[str(cls.__merge_files_counter).zfill(6)] = {
            'old_image_name': old_filename,
            'path': os.path.abspath(target_folder + "/" + str(cls.__merge_files_counter).zfill(6) + extension),
            'category': category_id,
            'query': os.path.basename(os.path.normpath(source_folder)),
            'clothes_nbr': 'None'
        }
        with open(output_file, 'w') as outfile:
            json.dump(cls.__data, outfile)

    @classmethod
    def convert_to_array(cls, source_folder, target_folder, create_labels_file=False,
                         flatten=False, extensions=('.jpg', '.jpeg', '.png')):
        """ Read all images in subfolders and convert them to a single array """

        # check source_folder and target_folder:
        cls.check_folder_existence(source_folder, throw_error_if_no_folder=True)
        cls.check_folder_existence(target_folder, display_msg=False)
        if source_folder[-1] == "/":
            source_folder = source_folder[:-1]
        if target_folder[-1] == "/":
            target_folder = target_folder[:-1]

        # read images and concatenate:
        print("Converting '", source_folder, "' images...")
        for filename in os.listdir(source_folder):
            if os.path.isdir(source_folder + '/' + filename):
                cls.convert_to_array(source_folder + '/' + filename, target_folder,
                                     create_labels_file=create_labels_file, extensions=extensions)
            else:
                if extensions == '' and os.path.splitext(filename)[1] == '':
                    image = cv2.imread(source_folder + "/" + filename)
                    if flatten:
                        cls.__data.append(image.flatten())
                    else:
                        cls.__data.append(image)
                    if create_labels_file:
                        cls.__labels.append(source_folder.replace('/', '_'))
                else:
                    for extension in extensions:
                        if filename.endswith(extension):
                            image = cv2.imread(source_folder + "/" + filename)
                            if flatten:
                                cls.__data.append(image.flatten())
                            else:
                                cls.__data.append(image)
                            if create_labels_file:
                                cls.__labels.append(source_folder.replace('/', '_'))

    @classmethod
    def convert_to_single_file(cls, source_folder, target_folder, create_labels_file=False,
                               flatten=False, extensions=('.jpg', '.jpeg', '.png')):
        """ Convert dataset images to a single file (array of images)
            The algorithm generates labels automatically according to subfolders"""

        # convert files in source_folder to data array and labels array:
        print("Converting images to single file...")
        cls.__data = []
        cls.__labels = []
        cls.convert_to_array(source_folder, target_folder, create_labels_file=create_labels_file,
                             flatten=flatten, extensions=extensions)

        # convert string labels to numeric type:
        if create_labels_file:
            print("Converting Labels to numeric type...")
            keys = list(set(cls.__labels))  # unique list of labels
            numeric_labels = dict(zip(keys, range(len(keys))))
            for i in range(len(cls.__labels)):
                cls.__labels[i] = numeric_labels[cls.__labels[i]]

        # save files:
        print(" Saving...")
        np.save(target_folder + '/data.npy', cls.__data)
        print(" > Images saved to: ", target_folder + '/data.npy')
        if create_labels_file:
            np.save(target_folder + '/labels.npy', cls.__labels)
            print(" > Labels saved to: ", target_folder + '/labels.npy')

    @classmethod
    def convert_to_grayscale(cls, source_folder, target_folder, extensions=('.jpg', '.jpeg', '.png')):
        """ convert images from RGB to Grayscale"""

        # check source_folder and target_folder:
        cls.check_folder_existence(source_folder, throw_error_if_no_folder=True)
        cls.check_folder_existence(target_folder, display_msg=False)
        if source_folder[-1] == "/":
            source_folder = source_folder[:-1]
        if target_folder[-1] == "/":
            target_folder = target_folder[:-1]

        # read images and reshape:
        print("Convert '", source_folder, "' images to grayscale...")
        for filename in os.listdir(source_folder):
            if os.path.isdir(source_folder + '/' + filename):
                cls.convert_to_grayscale(source_folder + '/' + filename,
                                         target_folder + '/' + filename,
                                         extensions=extensions)
            else:
                if extensions == '' and os.path.splitext(filename)[1] == '':
                    shutil.copy2(source_folder + "/" + filename,
                                 target_folder + "/" + filename)
                    image = cv2.imread(target_folder + "/" + filename, 0)
                    imageio.imwrite(target_folder + "/" + filename, image)
                else:
                    for extension in extensions:
                        if filename.endswith(extension):
                            shutil.copy2(source_folder + "/" + filename,
                                         target_folder + "/" + filename)
                            grayscale_image = cv2.imread(target_folder + "/" + filename, 0)
                            imageio.imwrite(target_folder + "/" + filename, grayscale_image)

    def convert_format(self, source_folder, target_folder, extensions=('.jpg', '.jpeg', '.png'), new_extension='.jpg'):
        """ change images from one format to another (eg. change png files to jpeg) """

        # check source_folder and target_folder:
        self.check_folder_existence(source_folder, throw_error_if_no_folder=True)
        self.check_folder_existence(target_folder, display_msg=False)
        if source_folder[-1] == "/":
            source_folder = source_folder[:-1]
        if target_folder[-1] == "/":
            target_folder = target_folder[:-1]

        # read images and change the format:
        print("Change format of '", source_folder, "' files...")
        for filename in os.listdir(source_folder):
            if os.path.isdir(source_folder + '/' + filename):
                self.convert_format(source_folder + '/' + filename,
                                    target_folder + '/' + filename,
                                    extensions=extensions, new_extension=new_extension)
            else:
                if extensions == '' and os.path.splitext(filename)[1] == '':
                    shutil.copy2(source_folder + "/" + filename, target_folder + "/" + filename + new_extension)
                    image = cv2.imread(target_folder + "/" + filename + new_extension)
                    imageio.imwrite(target_folder + "/" + filename + new_extension, image)
                    print("errore")
                else:
                    for extension in extensions:
                        if filename.endswith(extension):
                            new_filename = os.path.splitext(filename)[0] + new_extension
                            shutil.copy2(source_folder + "/" + filename, target_folder + "/" + new_filename)
                            image = plt.imread(target_folder + "/" + new_filename, extension)
                            imageio.imwrite(target_folder + "/" + new_filename, image)
