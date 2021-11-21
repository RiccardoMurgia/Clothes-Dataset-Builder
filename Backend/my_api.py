""" MyApi: aggregates the end points that allow the transfer of data between backend and frontend"""
import json
import os
import io
import pathlib
import shutil
import zipfile
from json import dumps
from flask import Flask, Response, request, send_file
from flask_cors import CORS
from clothes_detector import ClothesDetector
from colors_detector import ColorDetector
from dataset_builder import DatasetBuilder
from observer import Observer
from web_crawler import WebCrawler


class MyApi(Observer):

    def __init__(self, download_folder="./datasets/tmp_name"):

        self.__api_keys = {
            # 'google': ('AIzaSyASY8GTOQ0puFPxT6rG5SHkoNlHGb70Q6k', 'c955f1106a6303de0'),  # Api_key , Engine_ID
            # 'flickr': ('3691ef1c7c91026abbe6c0e01669b610', 'ab6652e8afc21351')
        }

        self.__images_nbr = 100

        self.__download_folder = download_folder
        self.__tmp_folder = download_folder + "/tmp"  # folder in which the images will be temporarily stored
        self.__target_folder = self.__download_folder + "/social_event_images"
        self.__event_images_info = download_folder + "/images_inf.json"
        self.__processed_datasets = download_folder + "/processed_dataset"
        self.__clothes_images = self.__processed_datasets + "/clothes"
        self.clothes_ann_file = self.__processed_datasets + "/clothes_info.txt"
        self.color_detection_ann_file = self.__processed_datasets + "/clothes_info.json"
        self.clothes_detection_model_weights = "./model/model_final.pth"

        self.__crawler = WebCrawler(self.__api_keys, self)
        self.__dataset_builder = DatasetBuilder()
        self.__clothes_detector = ClothesDetector(self, self.__event_images_info,
                                                  self.__processed_datasets, self.__clothes_images,
                                                  self.clothes_ann_file,
                                                  self.clothes_detection_model_weights)
        self.__color_detector = ColorDetector(self)

        self.download_progress_sate = 0
        self.clothes_detection_progress_state = 0
        self.color_detection_progress_state = 0

        self.app = Flask('yourapplication')
        CORS(self.app)
        CORS(self.app, resource={r"/*": {"origins": "*"}})
        self.app.add_url_rule('/state_of_the_keys', view_func=self.get_status_of_the_keys, methods=['GET'])
        self.app.add_url_rule('/clothes_detected', view_func=self.clothes_detection, methods=['GET'])
        self.app.add_url_rule('/images', view_func=self.download_images_links, methods=['GET'])
        self.app.add_url_rule('/api_keys', view_func=self.set_api_keys, methods=['GET'])
        self.app.add_url_rule('/progress_state', view_func=self.get_progress_state, methods=['GET'])
        self.app.add_url_rule('/number_of_links', view_func=self.set_links_number, methods=['GET'])
        self.app.add_url_rule('/download_dataset', view_func=self.send_dataset, methods=['GET'])
        self.app.add_url_rule('/keywords', view_func=self.delete_tab, methods=['DELETE'])
        self.app.add_url_rule('/delete_link', view_func=self.delete_image, methods=['DELETE'])
        self.app.add_url_rule('/delete_dataset', view_func=self.delete_dataset, methods=['DELETE'])
        self.app.add_url_rule('/deleted_clothes', view_func=self.delete_clothes_image, methods=['DELETE'])
        self.app.add_url_rule('/dataset_viewer', view_func=self.get_datasets, methods=['GET'])

        self.app.run(port=5000)

    def get_status_of_the_keys(self):
        """check if the client keys are set"""
        return Response(dumps({
            'content': str(bool(self.__api_keys))
        }), mimetype='text/jason')

    def clothes_detection(self):
        """Downloads to the server the  client side displayed images, scans the clothes and creating new images
        containing the clothes on black background"""
        self.download_progress_sate = 0
        self.clothes_detection_progress_state = 0
        self.color_detection_progress_state = 0
        dataset_name = request.args['key']
        name = dataset_name
        count = 1
        while os.path.exists("./datasets/" + name):
            name = dataset_name + "(" + str(count) + ")"
            count += 1
        self.__crawler.download_images(self.__tmp_folder)
        self.__dataset_builder.merge_folders(self.__tmp_folder, self.__target_folder,
                                             self.__event_images_info,
                                             extensions=('.jpg', '.jpeg', '.png', '.gif'))
        self.__dataset_builder.reset_dataset_builder_state()
        shutil.rmtree(self.__tmp_folder)
        self.__clothes_detector.clothes_detection()
        self.__color_detector.colors_detection(self.clothes_ann_file, self.color_detection_ann_file, 3)
        self.__rename_dataset_path(self.__event_images_info, name)
        self.__rename_dataset_path(self.color_detection_ann_file, name)
        os.rename('./datasets/tmp_name', './datasets/' + name)
        return Response(dumps({
            'content': 'Detection completed. Your Dataset is now available in the Dataset-viewer section'
        }), mimetype='text/jason')

    def __rename_dataset_path(self, file_path, name):
        images_inf = open(file_path, "r")
        json_object = json.load(images_inf)
        images_inf.close()
        for image in json_object:
            (json_object[image]['path']) = json_object[image]['path'].replace("tmp_name", name)
        images_inf = open(file_path, "w")
        json.dump(json_object, images_inf)
        images_inf.close()

    def download_images_links(self):
        """Saves the links of the images that the crawler was able to find"""
        query = request.args['key']
        self.__crawler.collect_links_from_web(query, self.__images_nbr, remove_duplicated_links=True)
        self.__crawler.save_urls_to_json(self.__download_folder + "/images_links.json")
        return Response(dumps({'content': self.__crawler.get_images_links()}), mimetype='text/jason')

    def set_api_keys(self):
        """set the client's api keys"""
        self.__crawler.reset_api_key()
        if request.args.get('code') == "0":
            google_key = request.args.get('google_key')
            google_engine_id = request.args.get('google_engine_id')
            flickr_key = request.args.get('flickr_key')
            flickr_engine_id = request.args.get('flickr_engine_id')
            self.__api_keys = {'google': (google_key, google_engine_id), 'flickr': (flickr_key, flickr_engine_id)}
        elif request.args.get('code') == "1":
            flickr_key = request.args.get('flickr_key')
            flickr_engine_id = request.args.get('flickr_engine_id')
            self.__api_keys = {'flickr': (flickr_key, flickr_engine_id)}
        else:
            google_key = request.args.get('google_key')
            google_engine_id = request.args.get('google_engine_id')
            self.__api_keys = {'google': (google_key, google_engine_id)}
        self.__crawler.set_api_keys(self.__api_keys)
        return Response(dumps({
            'content': 'keys initialized '
        }), mimetype='text/jason')

    def get_progress_state(self):
        """Provides the progress of clothes detection"""
        return Response(dumps({
            'content': (
                               self.download_progress_sate + self.clothes_detection_progress_state + self.color_detection_progress_state) / 3
        }), mimetype='text/jason')

    def set_links_number(self):
        self.__images_nbr = int(request.args.get('value'))
        return Response(dumps({
            'content': 'number of links initialized '
        }), mimetype='text/jason')

    def delete_tab(self):
        """Delete the links of the images present in the closed tab"""
        query = request.args['key']
        for keyword, link in list(self.__crawler.get_images_links().items()):
            if keyword == query:
                del self.__crawler.get_images_links()[keyword]
        return Response(dumps({
            'content': 'Links deleted'
        }), mimetype='text/jason')

    def delete_image(self):
        """Removes the link of the deleted image"""
        query = request.args['key']
        for keyword in self.__crawler.get_images_links():
            try:
                self.__crawler.get_images_links()[keyword].remove(query)
            except ValueError:
                pass
        return Response(dumps({
            'content': 'Deleted image'
        }), mimetype='text/jason')

    def get_datasets(self):
        data = {}
        if os.path.exists('./datasets'):
            datasets = os.listdir('./datasets')
            for dataset in datasets:
                if dataset != "tmp_name":
                    data[dataset] = {}
                    clothes_info_path = os.path.join("./datasets", dataset, 'processed_dataset', 'clothes_info.json')
                    processed_dataset_dir = os.path.join("./datasets", dataset, 'processed_dataset', 'clothes')
                    events = os.listdir(processed_dataset_dir)
                    for event in events:
                        data[dataset][event] = {}
                        data[dataset][event] = os.listdir(os.path.join(processed_dataset_dir, event))
                    with open(clothes_info_path, 'r') as file:
                        data[dataset]['info'] = json.load(file)
            return Response(dumps({
                'content': data
            }), mimetype='text/jason')
        else:
            return Response(dumps({
                'content': 'No datasets available'
            }), mimetype='text/jason')

    def delete_clothes_image(self):
        image_path = request.args['path']
        path_list = image_path.split("/")
        dataset_path = os.path.join(path_list[0], path_list[1], path_list[2])
        image_inf_path = os.path.join(dataset_path, "images_inf.json")
        clothes_inf_path = os.path.join(dataset_path, path_list[3], "clothes_info.json")
        clothes_dir_path = os.path.join(dataset_path, path_list[3], path_list[4])
        event_dir_path = os.path.join(dataset_path, path_list[3], path_list[4], path_list[5])
        social_event_image = os.path.basename(image_path).split("-")[0]
        clothes_image = os.path.basename(image_path)

        images_inf = open(image_inf_path, "r")
        json_object = json.load(images_inf)
        images_inf.close()
        json_object[social_event_image]['clothes_nbr'] = str(int(json_object[social_event_image]['clothes_nbr']) - 1)
        images_inf = open(image_inf_path, "w")
        json.dump(json_object, images_inf)
        images_inf.close()

        images_inf = open(clothes_inf_path, "r")
        json_object = json.load(images_inf)
        images_inf.close()
        del json_object[clothes_image]
        images_inf = open(clothes_inf_path, "w")
        json.dump(json_object, images_inf)
        images_inf.close()
        os.remove(image_path)

        if len(os.listdir(event_dir_path)) == 0:
            shutil.rmtree(event_dir_path)
            if len(os.listdir(clothes_dir_path)) == 0:
                shutil.rmtree(dataset_path)
                if len(os.listdir("./datasets")) == 0:
                    shutil.rmtree("./datasets")

        return Response(dumps({
            'content': 'Image Deleted'
        }), mimetype='text/jason')

    def delete_dataset(self):
        dataset = request.args['dataset']
        shutil.rmtree("./datasets/" + dataset)
        return Response(dumps({
            'content': 'Dataset Deleted'
        }), mimetype='text/jason')

    def send_dataset(self):
        base_path = pathlib.Path('./datasets/MyDataset')
        data = io.BytesIO()
        with zipfile.ZipFile(data, mode='w') as z:
            for f_name in base_path.rglob("*"):
                z.write(f_name)
        data.seek(0)
        return send_file(
            data,
            mimetype='application/zip',
            as_attachment=True,
            attachment_filename='data.zip'
        )

    def update_download_progress(self, current_img_nbr, total_img_nbr):
        """Update the download state"""
        self.download_progress_sate = ((current_img_nbr + 1) * 100) / total_img_nbr

    def update_clothes_detection_progress(self, current_img_nbr, total_img_nbr):
        """Update the clothes detection progress"""
        self.clothes_detection_progress_state = ((current_img_nbr + 1) * 100) / total_img_nbr

    def update_color_detection_progress(self, current_img_nbr, total_img_nbr):
        """Update the colors download state"""
        self.color_detection_progress_state = ((current_img_nbr + 1) * 100) / total_img_nbr
