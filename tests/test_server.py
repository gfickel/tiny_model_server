import unittest
import json

import numpy as np
import grpc
from grpc_testing import server_from_dictionary, strict_real_time
from grpc_health.v1 import health_pb2, health_pb2_grpc

import server_pb2
from server import ServerServicer
import utils


def get_image_arg(model: str, image: np.array, args:dict=''):
    image_proto = utils.numpy_to_proto(image)
    return server_pb2.ImageArgs(
            image=image_proto,
            model=model,
            args=json.dumps(args))

def get_batch_image_arg(model: str, image: np.array, args:dict=''):
    image_proto = utils.numpy_list_to_proto(image)
    return server_pb2.BatchImageArgs(
            images=image_proto,
            model=model,
            args=json.dumps(args))

class TestYourServer(unittest.TestCase):
    def setUp(self):
        self._real_time = strict_real_time()
        # Create a test gRPC server using grpc_testing
        self.my_server = ServerServicer()
        self.service = server_pb2.DESCRIPTOR.services_by_name['Server']
        descriptors_to_servicers = {
            server_pb2.DESCRIPTOR.services_by_name['Server']: self.my_server
        }

        self.server = server_from_dictionary(descriptors_to_servicers, self._real_time)

    def test_run_image(self):
        im = np.zeros((200,150,3), dtype=np.uint8)
        method = self.service.methods_by_name['RunImage']
        request = get_image_arg('example_image', im)
        rpc = self.server.invoke_unary_unary(method, (), request, None)

        response, _, code, _ = rpc.termination()
        res = json.loads(response.data)

        self.assertEqual(res, [['object1', 0.3], ['object2', 0.5]])
        self.assertIs(code, grpc.StatusCode.OK)

        im = np.zeros((200,150), dtype=np.uint8)
        request = get_image_arg('example_image', im)
        rpc = self.server.invoke_unary_unary(method, (), request, None)
        response, _, code, _ = rpc.termination()
        res = json.loads(response.data)

        self.assertEqual(res, [['object1', 0.3], ['object2', 0.5]])
        self.assertIs(code, grpc.StatusCode.OK)

    def test_run_batch_image(self):
        im = np.zeros((200,150,3), dtype=np.uint8)
        method = self.service.methods_by_name['RunBatchImage']
        request = get_batch_image_arg('example_image', [im,im,im,im])
        rpc = self.server.invoke_unary_unary(method, (), request, None)

        response, _, code, _ = rpc.termination()
        res = json.loads(response.data)
        self.assertIs(code, grpc.StatusCode.OK)

        im = np.zeros((20,15,3), dtype=np.uint8)
        request = get_batch_image_arg('example_image', [im,im,im,im])
        rpc = self.server.invoke_unary_unary(method, (), request, None)
        response, _, code, _ = rpc.termination()
        res = json.loads(response.data)
        self.assertEqual(res, [[['object1', 0.3], ['object2', 0.5]]]*4)
        self.assertIs(code, grpc.StatusCode.OK)

        im = np.zeros((20,15), dtype=np.uint8)
        request = get_batch_image_arg('example_image', [im,im,im,im])
        rpc = self.server.invoke_unary_unary(method, (), request, None)
        response, _, code, _ = rpc.termination()
        res = json.loads(response.data)
        self.assertEqual(res, [[['object1', 0.3], ['object2', 0.5]]]*4)
        self.assertIs(code, grpc.StatusCode.OK)

    def test_run_text(self):
        text = 'my dummy text'
        method = self.service.methods_by_name['RunText']
        request = server_pb2.TextArgs(model='example_text', text=text)
        rpc = self.server.invoke_unary_unary(method, (), request, None)

        response, _, code, _ = rpc.termination()
        res = json.loads(response.data)

        self.assertEqual(res, text+'_processed')
        self.assertIs(code, grpc.StatusCode.OK)

    def test_batch_text(self):
        text = 'my dummy text'
        method = self.service.methods_by_name['RunBatchText']
        request = server_pb2.BatchTextArgs(
            model='example_text', texts=[text,text,text,text])
        rpc = self.server.invoke_unary_unary(method, (), request, None)

        response, _, code, _ = rpc.termination()
        res = json.loads(response.data)
        self.assertEqual(res, [f'{text}_processed']*4)
        self.assertIs(code, grpc.StatusCode.OK)

    def test_get_input_shape(self):
        method = self.service.methods_by_name['GetInputShape']
        request = server_pb2.StringArg(data='example_image')
        rpc = self.server.invoke_unary_unary(method, (), request, None)
        response, _, code, _ = rpc.termination()
        res = json.loads(response.data)

        self.assertEqual(res, [1080, 1920, 3])
        self.assertIs(code, grpc.StatusCode.OK)

        request = server_pb2.StringArg(data='example_text')
        rpc = self.server.invoke_unary_unary(method, (), request, None)
        response, _, code, _ = rpc.termination()
        res = json.loads(response.data)
        self.assertEqual(res, None)
        self.assertIs(code, grpc.StatusCode.OK)

    def test_stop_server(self):
        method_shape = self.service.methods_by_name['GetInputShape']
        request = server_pb2.StringArg(data='example_image')
        rpc = self.server.invoke_unary_unary(method_shape, (), request, None)
        response, _, code, _ = rpc.termination()
        res = json.loads(response.data)

        self.assertEqual(res, [1080, 1920, 3])
        self.assertIs(code, grpc.StatusCode.OK)

        method_stop = self.service.methods_by_name['StopServer']
        request = server_pb2.EmptyArgs()
        rpc = self.server.invoke_unary_unary(method_stop, (), request, None)
        response, _, code, _ = rpc.termination()
        res = json.loads(response.data)
        self.assertEqual(res, {'stopping': True})

if __name__ == '__main__':
    unittest.main()
