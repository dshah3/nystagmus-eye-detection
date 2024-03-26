from typing import Protocol

from .video import FrameSource as VideoFrameSource

class FrameSource(Protocol):

    def next_frame(self):
        ...

    def start(self):
        ...

    def stop(self):
        ...