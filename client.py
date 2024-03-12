import grpc
import json
import numpy as np

import server_pb2
import server_pb2_grpc
import utils

options = [('grpc.max_receive_message_length', 1000 * 1024 * 1024)]
with grpc.insecure_channel('localhost:50000', options=options) as channel:
    stub = server_pb2_grpc.ServerStub(channel)
    img = np.zeros((200,200,3),dtype=np.uint8)
    proto_img = utils.numpy_to_proto(img)
    run_arg = server_pb2.ImageArgs(
            image=proto_img,
            model='example',
            args='')
    proto_model_name = server_pb2.StringArg(
            data='example')
    empty_args = server_pb2.EmptyArgs()

    resp = stub.ListModels(empty_args)
    models = json.loads(resp.data)['data']
    print('Models', models)

    resp = stub.RunImage(run_arg)
    recogs = json.loads(resp.data)['data']
    print('Recognition', recogs)

    resp = stub.GetInputShape(proto_model_name)
    resp = json.loads(resp.data)
    if 'error' in resp:
        print('ERROR', resp)
    else:
        print('Example model shape', resp['data'])
