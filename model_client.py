import abc
import time
import json
import math
from enum import Enum

import grpc
import numpy as np
from grpc_health.v1 import health_pb2, health_pb2_grpc
from PIL import Image

import utils
import server_pb2
import server_pb2_grpc


class ConnectionTimeout(Exception):
    " Raised when we couldn't connect to Tiny Model Server "
    def __init__(self, ip:str, port:str, timeout:int):
        print('Could not connect to model server. Perhaps check the following: '+\
              f'IP: {ip}, port: {port}, timeout: {timeout}s')

class InputType(Enum):
    IMAGE = 1
    TEXT = 2


class ModelClient(abc.ABC):
    def __init__(self, model: str, ip: str, port: str='50000', timeout: int=60*5):
        self.model = model
        self.stub_idx = 0
        self.channels = {}
        self.stubs = {}

        self._connect(ip, port, timeout)
        self.num_server_workers = self._get_num_parallel_workers()
        # opens one channel/stub per parallel server worker
        while len(self.channels) < self.num_server_workers:
            self._connect(ip, port, timeout)

        self.health_stubs = {k: health_pb2_grpc.HealthStub(v) for k,v in self.channels.items()}
        self.size = self.get_input_shape()

    def _connect(self, ip: str, port: str, timeout: int):
        # Change options to accept send large messages. And also sets
        # use_local_subhannel_pool enable connections to different workers when using so_reuseport
        options = [
            ('grpc.max_receive_message_length', int(1e9)),
            ('grpc.max_send_message_length', int(1e9)),
            ('grpc.use_local_subchannel_pool', 1)]
        channel = grpc.insecure_channel(f'{ip}:{port}', options=options)
        stub = server_pb2_grpc.ServerStub(channel)

        begin = time.time()
        pid = None
        while pid is None: # keep trying to connect until timeout
            try:
                response = stub.GetPID(
                    server_pb2.StringArg(data=self.model))
                pid = json.loads(response.data)['pid']
            except grpc._channel._InactiveRpcError:
                time.sleep(1)
            if time.time()-begin > timeout and pid is None:
                raise ConnectionTimeout(ip, port, timeout)

        if pid in self.channels:
            channel.close()
            return
        self.channels[pid] = channel
        self.stubs[pid] = stub

    def _load_balancer_pid(self):
        """Simple Round Robing load balancer that returns the stub index to be used."""
        self.stub_idx = (self.stub_idx+1) % len(self.stubs)
        pids = list(self.stubs.keys())
        return pids[self.stub_idx]

    def _get_stub(self):
        idx = self._load_balancer_pid()
        return self.stubs[idx]

    def _get_image_arg(self, image: np.array, args:dict=''):
        image_proto = utils.numpy_to_proto(image)
        return server_pb2.ImageArgs(
                image=image_proto,
                model=self.model,
                args=json.dumps(args))

    def _get_batch_image_arg(self, image: np.array, args:dict=''):
        image_proto = utils.numpy_list_to_proto(image)
        return server_pb2.BatchImageArgs(
                images=image_proto,
                model=self.model,
                args=json.dumps(args))

    def _get_text_arg(self, text: str, args:dict=''):
        return server_pb2.TextArgs(
                text=text,
                model=self.model,
                args=json.dumps(args))

    def _get_batch_text_arg(self, text: list[str], args:dict=''):
        return server_pb2.BatchTextArgs(
                texts=text,
                model=self.model,
                args=json.dumps(args))


    def _form_batch(self, inputs: list, input_type: InputType):
        if len(inputs) == 0:
            return None

        batch_inputs = []
        if input_type == InputType.TEXT:
            batch_inputs = inputs
        elif self.size is not None:
            # In order to avoid passing unnecessary data to model server, resize and change
            # the colors before sending them
            gray = len(self.size) == 2
            for im in inputs:
                if min(im.shape) == 0: # invalid image
                    batch_inputs.append(
                        np.zeros((self.size[0],self.size[1],3),dtype=np.uint8))
                    continue

                if im.shape[0] != self.size[0] or im.shape[1] > self.size[1]:
                    scale = self.size[0]/im.shape[0]
                    if scale < 1:
                        cols = min(self.size[1], math.ceil(scale*im.shape[1]))
                        tmp_img = Image.fromarray(im)
                        tmp_img = tmp_img.resize((cols, self.size[0]), Image.BICUBIC)
                        im = np.array(tmp_img)

                if gray and len(im.shape) > 2:
                    im = im.convert('L')
                batch_inputs.append(im)
        else:
            batch_inputs = inputs

        return batch_inputs

    def _get_num_parallel_workers(self):
        stub = self._get_stub()
        response = stub.GetNumParallelWorkers(
                server_pb2.StringArg(data=self.model))
        return json.loads(response.data)['num_workers']

    def _bad_input(self):
        return {}

    def run_image(self, image: np.array, args:dict=''):
        """Runs an image into the given model."""
        if image is None or min(image.shape[0:2]) <= 2:
            return self._bad_input()
        stub = self._get_stub()
        run_arg = self._get_image_arg(image, args)
        response = stub.RunImage(run_arg)
        return json.loads(response.data)

    def run_image_batch(self, images: list[np.array], args:dict=''):
        """Runs a batch of images into the given model."""
        batch = self._form_batch(images, InputType.IMAGE)
        if batch is None:
            return self._bad_input()
        stub = self._get_stub()
        run_arg = self._get_batch_image_arg(batch, args)
        response = stub.RunBatchImage(run_arg)
        return json.loads(response.data)

    def run_text(self, text: str, args:dict=''):
        """Runs a text into the given model."""
        if not isinstance(text, str):
            return self._bad_input()
        stub = self._get_stub()
        run_arg = self._get_text_arg(text, args)
        response = stub.RunText(run_arg)
        return json.loads(response.data)

    def run_text_batch(self, texts: list[str], args:dict=''):
        """Runs a batch of texts into the given model."""
        batch = self._form_batch(texts, InputType.TEXT)
        if batch is None:
            return self._bad_input()
        stub = self._get_stub()
        run_arg = self._get_batch_text_arg(batch, args)
        response = stub.RunBatchText(run_arg)
        return json.loads(response.data)

    def get_input_shape(self):
        """Get the input model shape, returns None if it doesn't have one."""
        stub = self._get_stub()
        response = stub.GetInputShape(
                server_pb2.StringArg(data=self.model))
        return json.loads(response.data)

    def health_check(self):
        """Checks all connections health status, returning a dict with the workers
        pids that are still serving and the ones that are not.
        """
        request = health_pb2.HealthCheckRequest(service='TinyModelServer')
        res = {'serving': [], 'stopped_serving': []}
        for pid in self.health_stubs:
            resp = self.health_stubs[pid].Check(request)
            if resp.status == health_pb2.HealthCheckResponse.SERVING:
                res['serving'].append(pid)
            else:
                res['stopped_serving'].append(pid)

        return res

    def stop_server(self):
        stub = self._get_stub()
        response = stub.StopServer(server_pb2.StringArg(data=self.model))
        return json.loads(response.data)
