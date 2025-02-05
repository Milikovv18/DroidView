from abc import ABC, abstractmethod
from dataclasses import dataclass
from threading import Semaphore
from queue import Queue
import numpy as np


@dataclass
class SupplierData:
    pixels : np.ndarray
    nodes : str | bytes | bytearray


class SupplierClosedException(Exception):
    pass


class ContentSupplier(ABC):
    @abstractmethod
    def has_client(self) -> bool:
        pass

    @abstractmethod
    def get_data(self) -> SupplierData:
        pass


class SupplierDoubleBuffer:
    def __init__(self) -> None:
        self.buffer = [SupplierData(None, None) for _ in range(2)]
        self.read_lock = Semaphore()
        self.write_lock = Semaphore()

    def write(self, data : SupplierData):
        if self.write_lock.acquire():
            self.buffer[0] = data
            self.write_lock.release()

    def read(self) -> SupplierData:
        if self.read_lock.acquire():
            data = self.buffer[1]
            self.read_lock.release()
            return data
        
    def swap(self):
        if self.read_lock.acquire():
            if self.write_lock.acquire():
                self.buffer[0], self.buffer[1] = self.buffer[1], self.buffer[0]
                self.write_lock.release()
            self.read_lock.release()
