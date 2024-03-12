import abc


class ModelInterface(abc.ABC):

    def get_input_shape(self):
        """ Returns numpy shape """
        return None


    @abc.abstractmethod
    def run(self, data, args):
        """ Returns a response dict """


    def run_batch(self, data, args):
        """ Same interface as run, however the images batch is encoded on
            a single numpy image. If the model does not provide a batch option
            just call it once for every input data.
        """
        return [self.run(x, args) for x in data]
