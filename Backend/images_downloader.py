""" ImagesDownloader: get a list of links, download the images and order them in a folder"""

from __future__ import print_function
import sys
from dataset_builder import DatasetBuilder
from urllib.request import urlopen
from shutil import copyfileobj
from observable import Observable


class ImagesDownloader(Observable):
    """Download a list of images, rename them and save them to the specified folder"""

    def __init__(self, observer):
        print("Preparing to download images...")
        self.__images_links = []
        self.__failed_links = []
        self._observers.append(observer)

    def download(self, links, target_folder='./data'):
        """Download images from a lisk of links"""

        # check links and folder:
        if len(links) < 1:
            print("Error: Empty list, no links provided")
            exit()
        self.__images_links = links
        DatasetBuilder.check_folder_existence(target_folder)
        if target_folder[-1] == '/':
            target_folder = target_folder[:-1]

        # start downloading:
        print("Downloading files...")
        progress = 0
        images_nbr = sum([len(self.__images_links[key]) for key in self.__images_links])
        for keyword, links in self.__images_links.items():
            DatasetBuilder.check_folder_existence(target_folder + '/' + keyword, display_msg=False)
            for link in links:
                target_file = target_folder + '/' + keyword + '/' + link.split('/')[-1]
                try:
                    with urlopen(link) as in_stream, open(target_file, 'wb') as out_file:
                        copyfileobj(in_stream, out_file)
                except IOError:
                    self.__failed_links.append(link)
                self.notify(progress, images_nbr)
                progress = progress + 1
                sys.stdout.flush()
        print(" >> ", (progress - len(self.__failed_links)), " images downloaded")
        # save failed links:
        if len(self.__failed_links):
            f2 = open(target_folder + "/failed_list.txt", 'w')
            for link in self.__failed_links:
                f2.write(link + "\n")
            print(" >> Failed to download ", len(self.__failed_links),
                  " images: access not granted ",
                  "(links saved to: '", target_folder, "/failed_list.txt')")

    def attach(self, observer):
        self._observers.append(observer)
        print("Subject: Attached an observer.")

    def detach(self, observer):
        self._observers.remove(observer)

    def notify(self, current_img_nbr, total_img_nbr):
        """Trigger an update in each subscriber."""
        for observer in self._observers:
            observer.update_download_progress(current_img_nbr, total_img_nbr)


