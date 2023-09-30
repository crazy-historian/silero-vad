import torch
import torchaudio
import torch.nn.functional as F

from typing import Callable, List
from pathlib import Path

import warnings
import numpy as np
import onnxruntime

project_path = Path(__file__).parent

languages = ['ru', 'en', 'de', 'es']



def get_onnx_inference_session(session_options, onnx_filepath: str, on_cpu: bool = True, num_threads: int = 1):
    if on_cpu and 'CPUExecutionProvider' in onnxruntime.get_available_providers():
        session = onnxruntime.InferenceSession(
            onnx_filepath,
            providers=['CPUExecutionProvider'],
            sess_options=session_options
            )
    else:
        session = onnxruntime.InferenceSession(onnx_filepath, sess_options=session_options)

    session_options.inter_op_num_threads = num_threads
    session_options.intra_op_num_threads = num_threads


    return session
    
def validate_input(x, sr):
    if x.dim() == 1:
        x = x.unsqueeze(0)
    if x.dim() > 2:
        raise ValueError(f"Too many dimensions for input audio chunk {x.dim()}")

    if sr / x.shape[1] > 31.25:
        raise ValueError("Input audio chunk is too short")

    return x, sr


class VoiceActivityDetection:
    def __init__(self, samplerate: int, onnx_filepath: str = f'{project_path}/files/silero_vad.onnx', num_threads: int = 1):
        self.samplerate = samplerate
        self.session = get_onnx_inference_session(onnxruntime.SessionOptions(), onnx_filepath, on_cpu=True, num_threads=num_threads)
        self.set_params_to_initial_values()

    def set_params_to_initial_values(self, batch_size: int = 1):
        self._h = np.zeros((2, batch_size, 64)).astype('float32')
        self._c = np.zeros((2, batch_size, 64)).astype('float32')
        self._last_sr = 0
        self._last_batch_size = 0

    def __call__(self, x, sr):
        x, sr = validate_input(x, sr)
        batch_size = x.shape[0]

        if not self._last_batch_size:
            self.set_params_to_initial_values(batch_size)
        if (self._last_sr) and (self._last_sr != sr):
            self.set_params_to_initial_values(batch_size)
        if (self._last_batch_size) and (self._last_batch_size != batch_size):
            self.set_params_to_initial_values(batch_size)

    
        ort_inputs = {
            'input': x.numpy(),
            'h': self._h,
            'c': self._c,
            'sr': np.array(sr, dtype='int64')
            }
        ort_outs = self.session.run(None, ort_inputs)

        out, self._h, self._c = ort_outs
        self._last_sr = sr
        self._last_batch_size = batch_size

        out = torch.tensor(out)
        return out
