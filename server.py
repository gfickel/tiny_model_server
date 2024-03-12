import contextlib
import logging
import multiprocessing
from multiprocessing import Pool, Lock
import importlib
import json
import socket
import sys
import os
from concurrent.futures import ThreadPoolExecutor

import grpc
from grpc_health.v1.health import HealthServicer
from grpc_health.v1 import health_pb2, health_pb2_grpc

import utils
import server_pb2
import server_pb2_grpc

LOGGER = logging.getLogger(__name__)
NUM_CPUS = multiprocessing.cpu_count()
NUM_PARALLEL_WORKERS = NUM_CPUS//2
PORT_NUMBER = 50000
SERVICE = 'TinyModelServer'

multiprocessing.set_start_method('fork')
# Queue that informs when all the workers must shutdown
shutdown_queue = multiprocessing.Queue()



class ServerServicer(server_pb2_grpc.ServerServicer):

    def __init__(self):
        self.models = {}
        for model in self._list_models():
            self._init_model(model)

        LOGGER.info('Tiny Model Server started!')

    def RunText(self, request, _context):  # pylint: disable=invalid-name
        results = self._run_text_model(request)

        return server_pb2.Response(
                data=json.dumps(results))

    def RunBatchText(self, request, _context):  # pylint: disable=invalid-name
        results = self._run_text_batch_model(request)

        return server_pb2.Response(
                data=json.dumps(results))

    def RunImage(self, request, _context):  # pylint: disable=invalid-name
        try:
            results = self._run_image_model(request)
            return server_pb2.Response(
                    data=json.dumps(results)
                )
        except BaseException as e:
            return server_pb2.Response(
                    data=json.dumps({'error': str(e)})
                )

    def RunBatchImage(self, request, _context):  # pylint: disable=invalid-name
        try:
            results = self._run_image_batch_model(request)
            return server_pb2.Response(
                    data=json.dumps(results)
                )
        except BaseException as e:
            LOGGER.error(e, exc_info=True)
            return server_pb2.Response(
                    data=json.dumps({'error': str(e)})
                )

    def ListModels(self, _request, _context):  # pylint: disable=invalid-name
        return server_pb2.Response(
                data=json.dumps(self._list_models()))

    def ReloadModel(self, request, context):  # pylint: disable=invalid-name,unused-argument
        model = request.data
        ok = self._init_model(model)
        return server_pb2.Response(
                data=json.dumps({'ok': ok}))

    def GetInputShape(self, request, _context):  # pylint: disable=invalid-name
        model = request.data
        if model not in self._list_models():
            response = {'error': 'Unitialized model'}
            return server_pb2.Response(
                data=json.dumps(response))

        try:
            response = self.models[model]['object'].get_input_shape()
        except BaseException as e:
            LOGGER.error('Exception: %s', e, exc_info=True)
            response = {'error': str(e)}

        return server_pb2.Response(
                data=json.dumps(response))

    def GetPID(self, _request, _context):  # pylint: disable=invalid-name
        return server_pb2.Response(
                data=json.dumps(
                    {'pid': os.getpid()}
                ))

    def GetNumParallelWorkers(self, _request, _context):  # pylint: disable=invalid-name
        return server_pb2.Response(
                data=json.dumps(
                    {'num_workers': NUM_PARALLEL_WORKERS}
                ))

    def StopServer(self, _request, _context):
        for _ in range(NUM_PARALLEL_WORKERS):
            shutdown_queue.put(1)
        LOGGER.info('Shuting down server...')
        return server_pb2.Response(
                data=json.dumps(
                    {'stopping': True}
                ))

    def _run_image_model(self, request):
        image = utils.proto_to_numpy(request.image)
        model = request.model
        if model not in self.models:
            return image, {'error': 'Unitialized model'}

        args = {} if len(request.args)==0 else json.loads(request.args)
        # Make sure we don't run the same model at the same time
        # on different threads
        with self.models[model]['lock']:
            results = self.models[model]['object'].run(image, args)

        return results

    def _run_image_batch_model(self, request):
        images = utils.proto_to_numpy_list(request.images)
        model = request.model
        if model not in self.models:
            return images, {'error': 'Unitialized model'}

        args = {} if len(request.args)==0 else json.loads(request.args)
        # Make sure we don't run the same model at the same time
        # on different threads
        with self.models[model]['lock']:
            results = self.models[model]['object'].run_batch(images, args)
        return results

    def _run_text_model(self, request):
        model = request.model
        if model not in self.models:
            return request.text, {'error': 'Unitialized model'}

        args = {} if len(request.args)==0 else json.loads(request.args)
        # Make sure we don't run the same model at the same time
        # on different threads
        with self.models[model]['lock']:
            results = self.models[model]['object'].run(request.text, args)

        return results

    def _run_text_batch_model(self, request):
        model = request.model
        if model not in self.models:
            return request.texts, {'error': 'Unitialized model'}

        args = {} if len(request.args)==0 else json.loads(request.args)
        # Make sure we don't run the same model at the same time
        # on different threads
        with self.models[model]['lock']:
            results = self.models[model]['object'].run_batch(request.texts, args)
        return results

    def _list_models(self):
        return os.listdir('./models/')

    def _init_model(self, model):
        model = model.lower()
        if model not in self._list_models():
            return False
        # TODO: check this import path
        # model_path = 'tiny_model_server.models.'+model
        model_path = f'models.{model}'
        model_import = __import__(model_path, globals(), locals(), ['object'])
        importlib.reload(model_import)

        try:
            obj = model_import.Model()
        except BaseException as e:
            LOGGER.error(str(e), exc_info=True)
            return False
        self.models[model] = {
                'object': obj,
                'lock': Lock(),
            }
        return True

def _run_server(bind_address):
    """Starts a server in a subprocess."""
    LOGGER.info('Starting new server.')
    options = (('grpc.so_reuseport', 1),
               ('grpc.max_receive_message_length', int(1e9)))

    health = HealthServicer()
    health.set(SERVICE, health_pb2.HealthCheckResponse.NOT_SERVING)

    server = grpc.server(
        ThreadPoolExecutor(max_workers=1,),
        options=options)
    server_pb2_grpc.add_ServerServicer_to_server(ServerServicer(), server)
    health_pb2_grpc.add_HealthServicer_to_server(health, server)
    server.add_insecure_port(bind_address)
    server.start()

    health.set(SERVICE, health_pb2.HealthCheckResponse.SERVING)
    shutdown_queue.get()


@contextlib.contextmanager
def _reserve_port(port_number):
    """Find and reserve a port for all subprocesses to use."""
    sock = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
    if sock.getsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT) == 0:
        raise RuntimeError('Failed to set SO_REUSEPORT.')
    sock.bind(('', port_number))
    try:
        yield sock.getsockname()[1]
    finally:
        sock.close()


def main():
    with _reserve_port(PORT_NUMBER) as port:
        bind_address = f'[::]:{port}'
        LOGGER.info('Binding to %s', bind_address)
        sys.stdout.flush()
        with Pool(processes=NUM_PARALLEL_WORKERS) as pool:
            pool.starmap(_run_server, [(bind_address,) for _ in range(NUM_PARALLEL_WORKERS)])

if __name__ == '__main__':
    handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter('[PID %(process)d] %(message)s')
    handler.setFormatter(formatter)
    LOGGER.addHandler(handler)
    LOGGER.setLevel(logging.INFO)
    main()
