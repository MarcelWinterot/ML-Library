import numpy as np
from nano_keras.activations import Activation, ACTIVATIONS
from nano_keras.regulizers import Regularizer
from nano_keras.optimizers import Optimizer
from nano_keras.initializers import Initializer, INITIALIZERS


class Layer:
    """Base class used to build new layers.
    It's used with all the layers that don't have any parameters to update
    """

    def __init__(self, units: int, activation: Activation | str, weight_initialization: Initializer | str = "random_normal", bias_initialization: Initializer | str = "random_normal", regulizer: Regularizer = None, trainable: bool = True, name: str = "Layer") -> None:
        """Initalizer for the Layer class

        Args:
            units (int): Number of neurons the layer should have
            activation (Activation | str): Activation function the model should use. You can find them all in the activations.py.
            weight_initaliziton (str, optional): Weights intialization strategy you want to use to generate weights of the layer. You can find all of them in the Initalizers folder. Defalut to "random_normal"
            bias_initialization (Initalizer | str, optional): Weights intialization strategy you want to use to generate biases of the layer. You can find all of them in the Initalizers folder. Defalut to "random_normal"
            regulizer (Regularizer, optional): Regulizer the model should use. You can find them all in the regulizers.py file. You must pass the already intialized class. Defaults to None.
            trainable (bool, optional): Parameter that decides whether the parameters should be updated or no. Defaults to True.
            name (str, optional): Name of the layer. Helpful for debugging. Defaults to "Layer".
        """
        self.units: int = units
        self.name: str = name

        self.weight_initialization: Initializer = INITIALIZERS[weight_initialization] if type(
            weight_initialization) == str else weight_initialization
        self.bias_initialization: Initializer = INITIALIZERS[bias_initialization] if type(
            bias_initialization) == str else bias_initialization

        self.activation: Activation = ACTIVATIONS[activation] if type(
            activation) == str else activation
        self.regulizer: Regularizer = regulizer
        self.trainable: bool = trainable
        self.batch_size: int = 1
        # Going from 0 to batch_size as it represent the index of self.inputs and self.outputs
        self.current_batch: int = 0

    def set_batch_size(self, batch_size: int, layers: list, index: int) -> None:
        """Function used to set the batch size of the layer

        Args:
            batch_size (int): Batch size of the model
            layers (list): All layers in the model
            index (int): Index of the current layer
        """
        self.batch_size = batch_size

        input_shape = layers[index-1].output_shape(layers, index-1)
        output_shape = self.output_shape(layers, index)

        self.inputs = np.ndarray((self.batch_size, *input_shape)) if type(
            input_shape) == tuple else np.ndarray((self.batch_size, input_shape))
        self.outputs = np.ndarray((self.batch_size, *output_shape)) if type(
            output_shape) == tuple else np.ndarray((self.batch_size, output_shape))

    def generate_weights(self, layers: list, current_layer_index: int, weight_data_type: np.float_, bias_data_type: np.float_) -> None:
        """Function used for weights generation for layers with 2d weights generated by looking at current layer and previous layers amount of neurons

        Args:
            layers (list): All layers in the model
            current_layer_index (int): For what layer do we want to generate the weights
            weight_data_type (np.float_): In what data type do you want to store the weights. Only use datatypes like np.float32 and np.float64
            bias_data_type (np.float_): In what data type do you want to store the biases. Only use datatypes like np.float32 and np.float64
        """
        previous_units = layers[current_layer_index -
                                1].output_shape(layers, current_layer_index-1)

        weights_shape = (previous_units, self.units)

        self.weights = self.weight_initialization(
            weights_shape, weight_data_type)

        self.biases = self.bias_initialization(self.units, bias_data_type)

    def get_weights(self) -> list[np.ndarray]:
        """Function used to get the weights of the layer

        Returns:
            list[np.ndarray]: [Weights, biases] of the layer
        """
        return [np.array([]), np.array([])]

    def get_number_of_params(self) -> tuple:
        """Function used to get the number of trainable and non-trainable parameters of the layer

        Returns:
            tuple: (trainable, non-trainable) parameters of the layer
        """
        return (0, 0)  # Trainable, non-trainable

    def get_params_size(self) -> tuple:
        """Function used to get the size of trainable and non-trainable parameters of the layer

        Returns:
            tuple: Size of (trainable, non-trainable) parameters of the layer
        """
        return (0, 0)  # Trainable, non-trainable

    def output_shape(self, layers: list, current_layer_index: int) -> tuple:
        """Function to generate the output shape of a layer

        Args:
            layers (list): All layers in the model
            current_layer_index (int): Index of the current layer

        Returns:
            tuple: Output shape of the layer
        """
        return

    def __repr__(self) -> str:
        """Function to print out layer information

        Returns:
            str: What to show when using print()
        """
        return "Base layer class"

    def __call__(self, x: np.ndarray, is_training: bool = False) -> np.ndarray:
        """Feed forward function for the layer\n
        Note that we also store all the variables the models calculated in self as it's layer used in backpropagate, so the memory usage might be higher than expected.

        Args:
            x (np.ndarray): X dataset
            is_training (bool): Determines whether the layer should behave like in the training loop or no. Defaults to False.

        Returns:
            np.ndarray: output after performing necessary calculations
        """
        weighted_sum = np.dot(x, self.weights) + self.biases
        output = self.activation.apply_activation(
            weighted_sum)

        if is_training:
            self.inputs[self.current_batch] = x
            self.outputs[self.current_batch] = output
            self.current_batch += 1

        return output

    def backpropagate(self, gradient: np.ndarray, optimizer: Optimizer | list[Optimizer]) -> np.ndarray:
        """Backpropagation algorithm base implementation for all the layers that don't have any parameters to update

        Args:
            gradient (np.ndarray): gradient calculated by losses.compute_derivative()
            optimizer (Optimizer): Optimizer to use when updating layers parameters

        Returns:
            np.ndarray: New gradient
        """
        return gradient
