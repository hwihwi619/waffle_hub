"""
Pseudo code for Training

Use Case 1.
# start train
train(..., hold=True)
# end train

Use Case 2.
# start train in another thread
callback = train(..., hold=False)

# wait for train to finish
while callback.end():
    print(callback.get_progress())

# end train

Sample code for Training
def train(hold: bool=True) -> Union[None, TrainCallback]:

    if hold:
        # train and return
        return
    else:
        # train in another thread and return callback
        return callback

Sample code for Inference
def inference(hold: bool=True) -> Union[None, InferenceCallback]:

    if hold:
        # inference and return
        return
    else:
        # inference in another thread and return callback
        return callback
"""
import threading
import time
import warnings


class ThreadProgressCallback:
    def __init__(self, total_steps: int):
        self._total_steps = total_steps

        self._thread = None
        self._finished = False
        self._progress = 0
        self._start_time = time.time()

    def get_progress(self) -> float:
        """Get the progress of the task. (0 ~ 1)"""
        return self._progress

    def is_finished(self) -> bool:
        """Check if the task has finished."""
        return self._finished

    def get_remaining_time(self) -> float:
        """Get the remaining time of the task. (seconds)"""
        elapsed = time.time() - self._start_time
        if self._progress == 0:
            return float("inf")
        return (elapsed / self._progress) - elapsed

    def update(self, step: int):
        """Update the progress of the task. (0 ~ total_steps)"""
        if self._finished:
            warnings.warn("Callback has already ended")
        elif step >= self._total_steps:
            self._finished = True
            self._progress = step / self._total_steps
        else:
            self._progress = step / self._total_steps

    def force_finish(self):
        """Force the task to end."""
        self._finished = True

    def register_thread(self, thread: threading.Thread):
        """Register the thread that is running the task."""
        self._thread = thread

    def start(self):
        """Start the thread that is running the task."""
        if self._thread is not None:
            self._thread.start()

    def join(self):
        """Wait for the thread that is running the task to end."""
        if self._thread is not None:
            self._thread.join()


class TrainCallback(ThreadProgressCallback):
    def __init__(self, total_steps: int, get_metric_func):
        super().__init__(total_steps)

        self._best_ckpt_file: str = None
        self._last_ckpt_file: str = None
        self._result_dir: str = None
        self._metric_file: str = None

        self._get_metric_func = get_metric_func

    @property
    def best_ckpt_file(self) -> str:
        """Get the path of the best model."""
        return self._best_ckpt_file

    @best_ckpt_file.setter
    def best_ckpt_file(self, path: str):
        self._best_ckpt_file = path

    @property
    def last_ckpt_file(self) -> str:
        """Get the path of the last model."""
        return self._last_ckpt_file

    @last_ckpt_file.setter
    def last_ckpt_file(self, path: str):
        self._last_ckpt_file = path

    @property
    def result_dir(self) -> str:
        """Get the path of the result directory."""
        return self._result_dir

    @property
    def metric_file(self) -> str:
        """Get the path of the metric file."""
        return self._metric_file

    @metric_file.setter
    def metric_file(self, path: str):
        self._metric_file = path

    @result_dir.setter
    def result_dir(self, path: str):
        self._result_dir = path

    def get_metrics(self) -> list[list[dict]]:
        """Get the metrics of the task. (list of list of dict)"""
        return self._get_metric_func()

    def get_progress(self) -> float:
        """Get the progress of the task. (0 ~ 1)"""
        metrics = self._get_metric_func()
        if len(metrics) == 0:
            return 0
        self.update(len(metrics))
        self._progress = len(metrics) / self._total_steps
        return self._progress


class InferenceCallback(ThreadProgressCallback):
    def __init__(self, total_steps: int):
        super().__init__(total_steps)

        self._inference_dir: str = None
        self._draw_dir: str = None

    @property
    def inference_dir(self) -> str:
        """Get the path of the result directory."""
        return self._inference_dir

    @inference_dir.setter
    def inference_dir(self, path: str):
        self._inference_dir = path

    @property
    def draw_dir(self) -> str:
        """Get the path of the visualize directory."""
        return self._draw_dir

    @draw_dir.setter
    def draw_dir(self, path: str):
        self._draw_dir = path


class ExportCallback(ThreadProgressCallback):
    def __init__(self, total_steps: int):
        super().__init__(total_steps)

        self._export_file: str = None

    @property
    def export_file(self) -> str:
        """Get the path of the result file."""
        return self._export_file

    @export_file.setter
    def export_file(self, path: str):
        self._export_file = path
