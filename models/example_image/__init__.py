from model_interface import ModelInterface


class Model(ModelInterface):

    def __init__(self):
        """ Here you may load an instance of your model """
        self.model = 'load my model here'

    def get_input_shape(self):
        """ Returns just like numpy shape """
        return (1080, 1920, 3)

    def run(self, data, args):
        return [('object1',0.3),('object2',0.5)]
