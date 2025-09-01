from abc import ABC, abstractmethod

class BaseUserRepository(ABC):
    @abstractmethod
    def load_users(self):
        pass

    @abstractmethod
    def save_users(self, users):
        pass
