import base64

from sklearn.cluster import KMeans
from collections import Counter
import cv2
import json
import os
from observable import Observable


class ColorDetector(Observable):

    def __init__(self, observer):
        self.__data = {}
        self.attach(observer)

    @staticmethod
    def __rgb_2_hew(color):
        return "#{:02x}{:02x}{:02x}".format(int(color[0]), int(color[1]), int(color[2]))

    @staticmethod
    def __get_image(image_path):
        image = cv2.imread(image_path)
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        return image

    def attach(self, observer):
        self._observers.append(observer)

    def detach(self, observer):
        self._observers.remove(observer)

    def notify(self, current_img_nbr, total_img_nbr):
        """Trigger an update in each subscriber."""
        for observer in self._observers:
            observer.update_color_detection_progress(current_img_nbr, total_img_nbr)

    def colors_detection(self, clothes_detection_info, color_detection_file, number_of_colors):
        progress_index = 0
        with open(clothes_detection_info) as clothes_info_file:
            list_lines = clothes_info_file.readlines()
        clothes_nbr = len(list_lines)

        for line in list_lines:
            progress_index += 1
            splits = line.split(",")
            image_path = splits[0].strip()
            social_event = splits[1].strip()
            img_name = os.path.basename(image_path)

            index = []
            values = []
            total_values = 0
            image = self.__get_image(image_path)
            modified_image = cv2.resize(image, (600, 400), interpolation=cv2.INTER_AREA)
            modified_image = modified_image.reshape(modified_image.shape[0] * modified_image.shape[1], 3)

            clf = KMeans(n_clusters=number_of_colors)
            labels = clf.fit_predict(modified_image)
            counts = Counter(labels)

            # We get ordered colors by iterating through the keys
            counts = counts.most_common()

            for i in range(0, number_of_colors):
                index.append(counts[i][0])
                values.append(counts[i][1])
                total_values += counts[i][1]

            center_colors = clf.cluster_centers_
            colors = [center_colors[i] for i in index]
            hex_colors = [self.__rgb_2_hew(colors[i]) for i in index]
            rgb_colors = [colors[i] for i in index]
            ordered_hex_colors = [hex_colors[i] for i in index]
            ordered_rgb_colors = [rgb_colors[i] for i in index]

            self.__save_clothes_info(image_path, img_name, social_event, ordered_hex_colors, ordered_rgb_colors, values,
                                     color_detection_file)
            self.notify(progress_index, clothes_nbr)

    def __save_clothes_info(self, image_path, img_name, social_event, ordered_hex_colors, ordered_rgb_colors, values,
                            color_detection_file):
        info = {'path': image_path, 'social event': social_event}
        for i in range(0, len(ordered_hex_colors)):
            info["color " + str(i)] = {
                'hex color': ordered_hex_colors[i],
                'R': ordered_rgb_colors[i][0],
                'G': ordered_rgb_colors[i][1],
                'B': ordered_rgb_colors[i][2],
                'percentage': round((values[i] / sum(values)) * 100, 2)
            }

        ##info['kobayashi class'] = "MODERN"

        with open(image_path, "rb") as image_file:
            base63_image = base64.b64encode(image_file.read()).decode('utf-8')
            info['base64 encoding'] = base63_image
        self.__data[img_name] = info

        with open(color_detection_file, 'w') as outfile:
            json.dump(self.__data, outfile)
