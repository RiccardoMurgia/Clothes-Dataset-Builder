from abc import ABC, abstractmethod


class Observer(ABC):
    """ The Observer interface declares the update method, used by subjects."""

    @abstractmethod
    def update_clothes_detection_progress(self, current_img_nbr, total_img_nbr):
        """Receive update from subject. """
        pass

    @abstractmethod
    def update_download_progress(self, current_img_nbr, total_img_nbr):
        """Receive update from subject. """
        pass

    @abstractmethod
    def update_color_detection_progress(self, current_img_nbr, total_img_nbr):
        """Receive update from subject. """
        pass
