import numpy as np
from model_client import ModelClient


model = ModelClient('example', 'localhost')

im = np.zeros((200,150,3), dtype=np.uint8)
res = model.run_image(im)
print(res)
print(model.get_input_shape())
model.stop_server()