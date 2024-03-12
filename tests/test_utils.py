import unittest

import numpy as np

import utils
import server_pb2

class TestUtils(unittest.TestCase):

    def test_numpy_to_proto_and_back(self):
        valid_dtypes = [np.uint8, np.float32, np.float64]
        dtypes_str_name = ['uint8', 'float32', 'float64']
        for dtype, dtype_str in zip(valid_dtypes, dtypes_str_name):
            for shape in [(200,300), (200,300,3)]:
                mat = np.zeros(shape, dtype=dtype)
                proto_mat = utils.numpy_to_proto(mat)
                mat_from_proto = utils.proto_to_numpy(proto_mat)

                if proto_mat.channels > 1:
                    proto_shape = (proto_mat.height, proto_mat.width, proto_mat.channels)
                else:
                    proto_shape = (proto_mat.height, proto_mat.width)
                self.assertEqual(mat.shape, proto_shape)
                self.assertEqual(dtype_str, proto_mat.dtype)
                self.assertTrue(np.array_equal(mat, mat_from_proto))


    def test_numpy_to_proto_invalid_dtype(self):
        mat = np.zeros((300,400,3), dtype=np.int32)
        with self.assertRaises(KeyError):
            _ = utils.numpy_to_proto(mat)


    def test_proto_to_numpy_invalid_dtype(self):
        mat = np.zeros((300,400,3), dtype=np.int32)
        proto_mat = server_pb2.NumpyImage(
            height=mat.shape[0],
            width=mat.shape[1],
            channels=(1 if len(mat.shape)==2 else mat.shape[2]),
            data=mat.tobytes(),
            dtype='int32'
        )
        with self.assertRaises(KeyError):
            _ = utils.proto_to_numpy(proto_mat)

    def test_numpy_to_proto_list_and_back(self):
        valid_dtypes = [np.uint8, np.float32, np.float64]
        dtypes_str_name = ['uint8', 'float32', 'float64']
        for dtype, dtype_str in zip(valid_dtypes, dtypes_str_name):
            for shape in [(200,300), (200,300,3)]:
                mat_list = [np.zeros(shape, dtype=dtype) for _ in range(6)]
                proto_mat_list = utils.numpy_list_to_proto(mat_list)
                mat_from_proto_list = utils.proto_to_numpy_list(proto_mat_list)

                for proto_mat, mat_from_proto in zip(proto_mat_list, mat_from_proto_list):
                    if proto_mat.channels > 1:
                        proto_shape = (proto_mat.height, proto_mat.width, proto_mat.channels)
                    else:
                        proto_shape = (proto_mat.height, proto_mat.width)
                    self.assertEqual(mat_list[0].shape, proto_shape)
                    self.assertEqual(dtype_str, proto_mat.dtype)
                    self.assertTrue(np.array_equal(mat_list[0], mat_from_proto))


                    
    def test_numpy_list_to_proto_invalid_dtype(self):
        mat = np.zeros((300,400,3), dtype=np.int32)
        with self.assertRaises(KeyError):
            _ = utils.numpy_list_to_proto([mat,mat,mat])


    def test_proto_to_numpy_list_invalid_dtype(self):
        mat = np.zeros((300,400,3), dtype=np.float32)
        proto_mat = utils.numpy_list_to_proto([mat,mat,mat])
        for idx, _ in enumerate(proto_mat):
            proto_mat[idx].dtype='int32'
        with self.assertRaises(KeyError):
            _ = utils.proto_to_numpy_list(proto_mat)

if __name__ == '__main__':
    unittest.main()
