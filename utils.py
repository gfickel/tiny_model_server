import numpy as np

import server_pb2


np_dtype_to_str = {
    np.dtype(np.uint8)   : 'uint8',
    np.dtype(np.float32) : 'float32',
    np.dtype(np.float64) : 'float64',
}
str_to_np_dtype = {v: k for k,v in np_dtype_to_str.items()}


def numpy_to_proto(mat):
    try:
        dtype_str = np_dtype_to_str[mat.dtype]
    except KeyError as exc:
        raise KeyError(
            f'Invalid numpy dtype. Available types: {str_to_np_dtype.keys()}') from exc

    return server_pb2.NumpyImage(
            height=mat.shape[0],
            width=mat.shape[1],
            channels=(1 if len(mat.shape)==2 else mat.shape[2]),
            data=mat.tobytes(),
            dtype=dtype_str
        )

def proto_to_numpy(image):
    try:
        dtype = str_to_np_dtype[image.dtype]
    except KeyError as exc:
        raise KeyError(
            f'Invalid numpy dtype. Available types: {str_to_np_dtype.keys()}') from exc
    np_image = np.frombuffer(image.data, dtype=dtype)
    if image.channels == 1:
        shape = (image.height, image.width)
    else:
        shape = (image.height, image.width, image.channels)
    return np_image.reshape(shape)

def numpy_list_to_proto(images):
    return [numpy_to_proto(im) for im in images]

def proto_to_numpy_list(images):
    return [proto_to_numpy(im) for im in images]