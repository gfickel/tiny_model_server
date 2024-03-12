from model_interface import ModelInterface


class Model(ModelInterface):

    def __init__(self):
        """ Here you may load an instance of your model """
        self.model = 'load my model'

    def get_input_shape(self):
        """ Returns (height, width, channels) just like numpy shape """
        return None

    def run(self, data, args):
        return data+'_processed'

