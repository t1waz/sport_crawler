import enum


class ScrapJobStatus(str, enum.Enum):
    PENDING = "pending"
    RUNNING = "running"
    FINISH = "finish"
    CONTENT_ERROR = "content_error"
    NETWORK_ERROR = "network error"
    UNEXPECTED_ERROR = "unexpected_error"
