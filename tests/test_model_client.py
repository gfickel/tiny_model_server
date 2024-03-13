import unittest
import subprocess

import numpy as np
from grpc._channel import _InactiveRpcError

from model_client import ModelClient


class TestModelClient(unittest.TestCase):
    def setup_class(self):
        subprocess.Popen(['python', 'server.py'])

    def teardown_class(self):
        model = ModelClient('example_image', 'localhost')
        model.stop_server()

    def test_image(self):
        model = ModelClient('example_image', 'localhost')

        im = np.zeros((200,150,3), dtype=np.uint8)
        res = model.run_image(im)
        self.assertEqual(res, [['object1', 0.3], ['object2', 0.5]])

        im = np.zeros((200,150), dtype=np.uint8)
        res = model.run_image(im)
        self.assertEqual(res, [['object1', 0.3], ['object2', 0.5]])

    def test_image_batch(self):
        model = ModelClient('example_image', 'localhost')

        im = np.zeros((20,15,3), dtype=np.uint8)
        res = model.run_image_batch([im,im,im,im])
        self.assertEqual(res, [[['object1', 0.3], ['object2', 0.5]]]*4)

        im = np.zeros((20,15), dtype=np.uint8)
        res = model.run_image_batch([im,im,im,im])
        self.assertEqual(res, [[['object1', 0.3], ['object2', 0.5]]]*4)

    def test_text(self):
        model = ModelClient('example_text', 'localhost')

        text = 'my random text'
        res = model.run_text(text)
        self.assertEqual(res, f'{text}_processed')

    def test_text_batch(self):
        model = ModelClient('example_text', 'localhost')

        text = 'my random text'
        res = model.run_text_batch([text,text,text,text])
        self.assertEqual(res, [f'{text}_processed']*4)

    def test_get_input_shape(self):
        model = ModelClient('example_image', 'localhost')
        model_text = ModelClient('example_text', 'localhost')

        res = model.get_input_shape()
        self.assertEqual(res, [1080, 1920, 3])

        res_txt = model_text.get_input_shape()
        self.assertEqual(res_txt, None)

    def test_stop_server(self):
        model = ModelClient('example_image', 'localhost')

        res = model.get_input_shape()
        self.assertEqual(res, [1080, 1920, 3])

        res = model.stop_server()
        self.assertEqual(res, {'stopping': True})

        # Wait for server to shutdown before setting it up again
        while res is not None:
            try:
                res = model.get_input_shape()
            except _InactiveRpcError:
                res = None

        self.setup_class()

    def test_health(self):
        model = ModelClient('example_image', 'localhost')

        res = model.health_check()
        self.assertTrue(len(res['serving'])>0)
        self.assertTrue(len(res['stopped_serving'])==0)


if __name__ == '__main__':
    unittest.main()
