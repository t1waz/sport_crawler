import enum


class ScrapJobStatus(str, enum.Enum):
    PENDING = "pending"
    RUNNING = "running"
    FINISH = "finish"
    CONTENT_ERROR = "content_error"
    NETWORK_ERROR = "network error"
    UNEXPECTED_ERROR = "unexpected_error"
    PROCESS_DATA_ERROR = "process_data_error"
    FETCHER_NOT_FINISHED = "fetcher_not_finish"
