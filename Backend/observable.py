from abc import ABC, abstractmethod


class Observable(ABC):
    """The Subject interface declares a set of methods for managing subscribers."""
    _observers = []

    @abstractmethod
    def attach(self, observer):
        """Attach an observer to the subject."""
        pass

    @abstractmethod
    def detach(self, observer):
        """Detach an observer from the subject. """
        pass

    @abstractmethod
    def notify(self, current_img_nbr, total_img_nbr):
        """Notify all observers about an event."""
        pass
