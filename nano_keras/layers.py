import numpy as np
from nano_keras.activations import ACTIVATIONS, Activation
from nano_keras.optimizers import Optimizer
from nano_keras.regulizers import Regularizer
import math


class Layer:
    def __init__(self, units: int, activation: Activation | str, regulizer: Regularizer = None, name: str = "Layer") -> None:
        """Intializer for the layer class. 

        Args:
            units (int): Number of neurons the layer should have
            activation (Activation | str): Activation function the model should use. You can find them all in the activations.py.
            regulizer (Regularizer, optional): Regulizer the model should use. You can find them all in the regulizers.py file. You must pass the already intialized class. Defaults to None.
            name (str, optional): Name of the layer. Helpful for debugging. Defaults to "Layer".
        """
        self.units = units
        self.name = name
        self.weights = np.array([])
        self.biases = np.array([])
        self.activation = ACTIVATIONS[activation] if type(
            activation) == str else activation
        self.regulizer = regulizer

    @staticmethod
    def random_initalization(previous_units: int, current_units: int, weight_data_type: np.float_) -> tuple[np.ndarray, np.ndarray]:
        """Random intitalization strategy used for weights generation. Note that this works for 2d layers that use units for weight generation and not layers like Conv1d and Conv2d

        Args:
            previous_units (int): Number of units in the previous layer
            current_units (int): Number of units in the current layer in which we want the weights generated
            weight_data_type (np.float_): In what data type do we want the weights stored

        Returns:
            tuple[np.ndarray, np.ndarray]: Weights and biases of the layer
        """
        return np.random.randn(previous_units, current_units).astype(weight_data_type), np.random.randn(current_units).astype(weight_data_type)

    @staticmethod
    def xavier_intialization(previous_units: int, current_units: int, weight_data_type: np.float_) -> tuple[np.ndarray, np.ndarray]:
        """Xavier intitalization strategy used for weights generation. Note that this works for 2d layers that use units for weight generation and not layers like Conv1d and Conv2d

        Args:
            previous_units (int): Number of units in the previous layer
            current_units (int): Number of units in the current layer in which we want the weights generated
            weight_data_type (np.float_): In what data type do we want the weights stored

        Returns:
            tuple[np.ndarray, np.ndarray]: Weights and biases of the layer
        """
        weights = np.random.randn(
            previous_units, current_units).astype(weight_data_type)
        weights = 2 * weights - 1
        weights *= np.sqrt(6/(previous_units+current_units))
        return weights, np.zeros(current_units).astype(weight_data_type)

    @staticmethod
    def he_intialization(previous_units: int, current_units: int, weight_data_type: np.float_) -> tuple[np.ndarray, np.ndarray]:
        """He intitalization strategy used for weights generation. Note that this works for 2d layers that use units for weight generation and not layers like Conv1d and Conv2d

        Args:
            previous_units (int): Number of units in the previous layer
            current_units (int): Number of units in the current layer in which we want the weights generated
            weight_data_type (np.float_): In what data type do we want the weights stored

        Returns:
            tuple[np.ndarray, np.ndarray]: Weights and biases of the layer
        """
        weights = np.random.randn(
            previous_units, current_units).astype(weight_data_type)
        weights *= np.sqrt(2./previous_units)
        return weights, np.zeros(current_units).astype(weight_data_type)

    def generate_weights(self, layers: list, current_layer_index: int, weight_initalization: str, weight_data_type: np.float_) -> None:
        """Function used for weights generation for layers with 2d weights generated by looking at current layer and previous layers amount of neurons

        Args:
            layers (list): All layers in the model
            current_layer_index (int): For what layer do we want to generate the weights
            weight_initalization (str): What strategy do we want to use for weight generation. Currently you have 3 options and those being: random, xavier, he
            weight_data_type (np.float_): In what data type do you want to store the weights. Only use datatypes like np.float32 and np.float64
        """
        LAYER_INTIALIZATIONS = {"random": self.random_initalization,
                                "xavier": self.xavier_intialization, "he": self.he_intialization}

        previous_units = layers[current_layer_index -
                                1].output_shape(layers, current_layer_index-1)
        self.weights, self.biases = LAYER_INTIALIZATIONS[weight_initalization](
            previous_units, self.units, weight_data_type)

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

    def __call__(self, x: np.ndarray) -> np.ndarray:
        """Call function for the layer, also know as feed forward\n
        Note that we also store all the variables the models calculated in self as it's layer used in backpropagate

        Args:
            x (np.ndarray): X dataset

        Returns:
            np.ndarray: output of the model
        """
        self.inputs = x
        weighted_sum = np.dot(x, self.weights) + self.biases
        output = self.activation.compute_loss(weighted_sum)
        self.outputs = np.array([output, weighted_sum])
        return output

    def backpropagate(self, gradient: np.ndarray, optimizer: Optimizer | list[Optimizer, Optimizer]) -> np.ndarray:
        """Backpropagation algorithm base implementation for all the layers that don't have any parameters to update

        Args:
            gradient (np.ndarray): gradient calculated by losses.compute_derivative()
            optimizer (Optimizer): Optimizer to use when updating layers parameters

        Returns:
            np.ndarray: New gradient
        """
        return gradient


class Input(Layer):
    def __init__(self, input_shape: tuple, name: str = "Input") -> None:
        """Intializer for input layer.

        Args:
            input_shape (tuple): Shape of the input for the model
            name (str, optional): Name of the layer. Defaults to "Input".
        """
        self.input_shape = input_shape
        self.name = name
        self.biases = None
        self.biases = np.random.randn(
            *input_shape) if type(input_shape) == tuple else np.random.randn(input_shape)
        # Initializing the weights as I don't want to add another if statement to NN.summary() for checking if a layer has weights
        self.weights = np.array([])

    def output_shape(self, layers: list, current_layer_index: int) -> tuple:
        return self.input_shape

    def __repr__(self) -> str:
        try:
            formatted_output = f'(None, {", ".join(map(str, self.input_shape))})'
        except:
            formatted_output = f'(None, {self.input_shape})'
        return f"{self.name} (Input){' ' * (28 - len(self.name) - 7)}{formatted_output}{' ' * (26 - len(formatted_output))}{self.biases.size}\n"

    def __call__(self, x: np.ndarray) -> np.ndarray:
        self.inputs = x
        if self.biases is not None:
            x = x + self.biases
            self.outputs = x
        return x


class Dense(Layer):
    def output_shape(self, layers: list, current_layer_index: int) -> tuple:
        return self.units

    def __repr__(self) -> str:
        return f"{self.name} (Dense){' ' * (28 - len(self.name) - 7)}{(None, self.units)}{' ' * (26 - len(f'(None, {self.units})'))}{self.weights.size + self.biases.size}\n"

    def backpropagate(self, gradient: np.ndarray, optimizer: list[Optimizer, Optimizer]) -> np.ndarray:
        """Backpropagation algorithm for the dense layer

        Args:
            gradient (np.ndarray): Gradient calculated by the loss function derivative or by previous layers backpropagation algorithm
            optimizer (List[Optimizer, Optimizer]): Optimizer to use for updating the model's parameters. Note that we use 2 different optimizers as then we don't have to check a bunch of times 
            wheter we use 1 or 2 optimizers, and we need 2 optimizers for CNNs

        Returns:
            np.ndarray: Output gradient of the layer
        """
        if self.regulizer:
            gradient = self.regulizer.compute_loss(
                gradient, self.weights, self.biases)
        delta = np.average(
            [gradient * self.activation.compute_derivative(output) for output in self.outputs])

        weights_gradients = np.outer(self.inputs, delta)

        self.weights, self.biases = optimizer[0].apply_gradients(weights_gradients, np.array(
            delta, dtype=float), self.weights, self.biases)

        return np.dot(delta, self.weights.T)


class Dropout(Layer):
    def __init__(self, units: int, activation: Activation | str, dropout_rate: float = 0.2, regulizer: Regularizer | None = None, name: str = "Layer") -> None:
        """Intializer for the dropout layer. Note that dropout layer acts the same as Dense but also drops connections between neurons

        Args:
            units (int): Number of neurons in the layer
            activation (Activation | str): ACtivation function the model should use
            dropout_rate (float, optional): The pecentage of connections dropped. Note that we 0.2 means 20%. Defaults to 0.2.
            regulizer (Regularizer | None, optional): Regulizer the model should use. Defaults to None.
            name (str, optional): Name of the layer. Defaults to "Layer".
        """
        super().__init__(units, activation, regulizer, name)
        self.dropout_rate = dropout_rate

    def output_shape(self, layers: list, current_layer_index: int) -> tuple:
        return self.units

    def __repr__(self) -> str:
        return f"{self.name} (Dropout){' ' * (28 - len(self.name) - 9)}{(None, self.units)}{' ' * (26 - len(f'(None, {self.units})'))}{self.weights.size + self.biases.size}\n"

    def __call__(self, x: np.ndarray, isTraining: bool = True) -> np.ndarray:
        """Call function for the dropout layer, also known as feedforward for it. We drop the connections by applying this mask:\n
        weighted_sum /= 1 - self.dropout_rate

        Args:
            x (np.ndarray): X dataset
            isTraining (bool, optional): Param to control the mask. If it's set to False we don't apply the mask. Defaults to True.

        Returns:
            np.ndarray: Output of the model
        """
        self.inputs = x
        if isTraining:
            weighted_sum = np.dot(x, self.weights) + self.biases
            weighted_sum /= 1 - self.dropout_rate
            output = self.activation.compute_loss(weighted_sum)
            self.outputs = np.array([output, weighted_sum])
            return output

        return super().__call__(x)

    def backpropagate(self, gradient: np.ndarray, optimizer: list[Optimizer, Optimizer]) -> np.ndarray:
        """Backpropagation algorithm for the dropout layer

        Args:
            gradient (np.ndarray): Gradient calculated by loss.compute_derivative() or previous layers output gradient
            optimizer (List[Optimizer, Optimizer]): Optimizer to use for updating the model's parameters. Note that we use 2 different optimizers as then we don't have to check a bunch of times 
            wheter we use 1 or 2 optimizers, and we need 2 optimizers for CNNs

        Returns:
            np.ndarray: Output gradient
        """
        if self.regulizer:
            gradient = self.regulizer.compute_loss(
                gradient, self.weights, self.biases)

        delta = np.average(
            [gradient * self.activation.compute_derivative(output) for output in self.outputs])

        delta /= 1/(1-self.dropout_rate)  # Scaling the gradient

        weights_gradients = np.outer(self.inputs, delta)

        self.weights, self.biases = optimizer[0].apply_gradients(weights_gradients, np.array(
            delta, dtype=float), self.weights, self.biases)

        return np.dot(delta, self.weights.T)


class Flatten(Layer):
    def __init__(self, name: str = "Flatten") -> None:
        """Initalizer for the flatten layer

        Args:
            name (str, optional): Name of the layer. Defaults to "Flatten".
        """
        self.name = name

    def output_shape(self, layers: list, current_layer_index: int) -> tuple:
        input_shape = layers[current_layer_index -
                             1].output_shape(layers, current_layer_index-1)
        self.output_shape_value = (np.prod(np.array(input_shape)))
        self.next_layer_shape = layers[current_layer_index +
                                       1].output_shape(layers, current_layer_index+1)
        return self.output_shape_value

    def __repr__(self) -> str:
        return f"{self.name} (Flatten){' ' * (28 - len(self.name) - 9)}{(None, self.output_shape_value)}{' ' * (26-len(f'(None, {self.output_shape_value})'))}0\n"

    def __call__(self, x: np.ndarray) -> np.ndarray:
        self.original_shape = x.shape
        return np.ravel(x)

    def backpropagate(self, gradient: np.ndarray, optimizer: list[Optimizer, Optimizer]) -> np.ndarray:
        """Backpropagate algorithm for the flatten layer. We unflatten the gradient in here

        Args:
            gradient (np.ndarray): Gradient calculated by loss.compute_derivative() or previous layers output gradient
            optimizer (List[Optimizer, Optimizer]): Optimizer to use for updating the model's parameters. Note that we use 2 different optimizers as then we don't have to check a bunch of times 
            wheter we use 1 or 2 optimizers, and we need 2 optimizers for CNNs

        Returns:
            np.ndarray: Output gradient
        """
        try:
            return gradient.reshape(self.next_layer_shape, *self.original_shape)
        except:
            return gradient


class Reshape(Layer):
    def __init__(self, target_shape: tuple, name: str = "Reshape") -> None:
        """Initalizer for the Reshape layer

        Args:
            target_shape (tuple): Target shape of the layer
            name (str, optional): Name of the layer. Defaults to "Reshape".
        """
        self.target_shape = target_shape
        self.name = name

    def output_shape(self, layers: list, current_layer_index: int) -> tuple:
        self.next_layer_shape = layers[current_layer_index +
                                       1].output_shape(layers, current_layer_index+1)
        return self.target_shape

    def __repr__(self) -> str:
        formatted_output = f'(None, {", ".join(map(str, self.target_shape))})'
        return f"{self.name} (Reshape){' ' * (28 - len(self.name) - 9)}{formatted_output}{' ' * (26-len(formatted_output))}0\n"

    def __call__(self, x: np.ndarray) -> np.ndarray:
        self.original_shape = x.shape
        return np.reshape(x, self.target_shape)

    def backpropagate(self, gradient: np.ndarray, optimizer: list[Optimizer, Optimizer]) -> np.ndarray:
        """Backpropagate algorithm used for reshape layer. We reshape the gradient in here

        Args:
            gradient (np.ndarray): Gradient calculated by the loss.compute_derivative function
            optimizer (List[Optimizer, Optimizer]): Optimizer to use for updating the model's parameters. Note that we use 2 different optimizers as then we don't have to check a bunch of times 
            wheter we use 1 or 2 optimizers, and we need 2 optimizers for CNNs

        Returns:
            np.ndarray: Output gradient
        """
        try:
            return gradient.reshape(self.next_layer_shape, *self.original_shape)
        except:
            return gradient


class MaxPool1D(Layer):
    def __init__(self, kernel_size: int = 2, strides: int = 2, name: str = "MaxPool1D") -> None:
        """Intializer for the MaxPool1D layer

        Args:
            kernel_size (int, optional): Size of the pooling window. Defaults to 2.
            strides (int, optional): Step the kernel should take. If the parameter is set to None it will be assigned the value of kernel_size. Defaults to 2.
            name (str, optional): Name of the layer. Defaults to MaxPool1D.
        """
        self.kernel_size = kernel_size
        self.strides = strides
        self.name = name

    def output_shape(self, layers: list, current_layer_index: int) -> tuple:
        input_shape = layers[current_layer_index -
                             1].output_shape(layers, current_layer_index-1)
        self.output_shape_value = math.ceil(
            (input_shape - self.kernel_size + 1) / self.strides)
        return self.output_shape_value

    def __repr__(self) -> str:
        return f"{self.name} (MaxPool1D){' ' * (28 - len(self.name) - 11)}{(None, self.output_shape_value)}{' ' * (26-len(f'(None, {self.output_shape_value})'))}0\n"

    def __call__(self, x: np.ndarray) -> np.ndarray:
        """Call function for the MaxPool1D layer. It reduces the size of an array by how much the kernel_size and strides is set to.
        For example let's say we have those parameters:\n
        array X = [[1., 5., 3., 6., 7., 4.]]\n
        both kernel_size and strides set to 2\n
        The result we'd get is [[5., 6., 7.]]\n
        As we take a smaller sub arrays of size kernel_size and return the max value out of them, then onto a next sub-array, with index of: current index + strides

        Args:
            x (np.ndarray): Array to reduce the size of

        Returns:
            np.ndarray: Array with reduced size
        """
        output_size = math.ceil((x.size - self.kernel_size + 1) / self.strides)
        output = np.empty((output_size,))

        currentIndex = 0
        for i in range(0, x.size, self.strides):
            if i + self.kernel_size > x.size:
                break  # Reached the end of the input

            output[currentIndex] = np.max(x[i:i + self.kernel_size])
            currentIndex += 1

        return output


class MaxPool2D(Layer):
    def __init__(self, pool_size: tuple[int, int] = (2, 2), strides: tuple[int, int] = (2, 2), name: str = "MaxPool2D"):
        """Intializer for the MaxPool2D layer

        Args:
            pool_size (tuple[int, int], optional): Size of the pool. Defaults to (2, 2).
            strides (tuple[int, int], optional): Step the kernel should take. Defaults to (2, 2).
            name (str, optional): Name of the layer. Default to NaxPool2D
        """
        self.pool_size = pool_size
        self.strides = strides
        self.name = name

    def output_shape(self, layers: list, current_layer_index: int) -> tuple:
        input_shape = layers[current_layer_index -
                             1].output_shape(layers, current_layer_index-1)
        self.output_shape_value = tuple([math.floor(
            (input_shape[i] - self.pool_size[i]) / self.strides[i]) + 1 for i in range(2)])

        if len(input_shape) > 2:
            self.output_shape_value += (input_shape[-1],)

        return self.output_shape_value

    def __repr__(self) -> str:
        formatted_output = f'(None, {", ".join(map(str, self.output_shape_value))})'
        return f"{self.name} (MaxPool2D){' ' * (28 - len(self.name) - 11)}{formatted_output}{' ' * (26-len(formatted_output))}0\n"

    def __call__(self, x: np.ndarray) -> np.ndarray:
        """Call function for the MaxPool1D layer. It reduces the size of an array by how much the kernel_size and strides is set to.
        For example let's say we have those parameters:\n
        array X:\n
        [[2, 3, 5, 9],\n
        [4, 5, 2, 6],\n
        [7, 4, 6, 5],\n
        [8, 3, 4, 1]]\n
        both kernel_size and strides set to (2, 2)\n
        The result we'd get is:\n
        [[5, 9],\n
        [8, 6]]\n


        Args:
            x (np.ndarray): Array to reduce the size of

        Returns:
            np.ndarray: Array with reduced size
        """
        self.inputs = x

        x_shape = x.shape
        height = (x_shape[0] - self.pool_size[0]) // self.strides[0] + 1
        width = (x_shape[1] - self.pool_size[1]) // self.strides[1] + 1

        output = np.zeros((height, width))

        if len(x_shape) == 3:
            output = np.zeros((height, width, x_shape[-1]))

        for i in range(height):
            for j in range(width):
                # We are using this method instead of range(0, x.shape[0], self.strides[0]) as then we'd have to
                # keep on what iteration of what we are on and that's just too much useless work for now
                i_start, j_start = i * self.strides[0], j * self.strides[1]
                i_end, j_end = i_start + \
                    self.pool_size[0], j_start + self.pool_size[1]

                output[i, j] = np.max(x[i_start:i_end, j_start:j_end])

        if len(x.shape) == 3:
            output[-1, -1, :] = x[-1, -1, :]

        self.output = output
        return output

    def backpropagate(self, gradient: np.ndarray, optimizer: list[Optimizer, Optimizer]) -> np.ndarray:
        """Backpropagation algorithm for MaxPool2D layer. Note that it's not finished so it doesn't work properly

        Args:
            gradient (np.ndarray): Gradient calculated by loss.compute_derivative() or previous layers output gradient
            optimizer (List[Optimizer, Optimizer]): Optimizer to use for updating the model's parameters. Note that we use 2 different optimizers as then we don't have to check a bunch of times 
            wheter we use 1 or 2 optimizers, and we need 2 optimizers for CNNs

        Returns:
            np.ndarray: Output gradient
        """
        raise Exception(
            "MaxPool2D backpropagation is not implemented yet, if you really need it set the strides in Conv2D to something other than (1, 1)")
        return gradient


class Conv1D(Layer):
    def __init__(self, filters: int = 1, kernel_size: int = 2, strides: int = 1, activation: Activation | str = "relu", regulizer: Regularizer = None, name: str = "Conv1D") -> None:
        """Initalizer for the Conv1D layer

        Args:
            filters (int, optional): Number of filters. Defaults to 1.
            kernel_size (int, optional): Kernel size the model should use. Defaults to 2.
            strides (int, optional): By how much should the kernel move after each operation. Defaults to 1.
            activation (Activation | str, optional): Activation function the layer should use. Defaults to "relu".
            regulizer (Regularizer, optional): Regulizer of the layer. Defaults to None.
            name (str, optional): Name of the layer. Defaults to "Conv1D".
        """
        self.number_of_filters = filters
        self.kernel_size = kernel_size
        self.strides = strides
        self.activation = ACTIVATIONS[activation] if type(
            activation) == str else activation
        self.weights = np.random.randn(filters, self.kernel_size)
        self.name = name
        self.biases = np.random.randn(filters)
        self.regulizer = regulizer

    def output_shape(self, layers: list, current_layer_index: int) -> tuple:
        input_shape = layers[current_layer_index -
                             1].output_shape(layers, current_layer_index-1)
        self.output_shape_value = np.array(
            input_shape).size // self.strides, self.number_of_filters
        return self.output_shape_value

    def __repr__(self) -> str:
        formatted_output = f'(None, {", ".join(map(str, self.output_shape_value))})'
        return f"{self.name} (Conv1D){' ' * (28 - len(self.name) - 8)}{formatted_output}{' ' * (26-len(formatted_output))}{self.weights.size + self.biases.size}\n"

    def __call__(self, x: np.ndarray) -> np.ndarray:
        self.inputs = x

        weighted_sum = np.zeros(
            (x.size // self.strides, self.number_of_filters))

        for i in range(0, x.size, self.strides):
            if i + self.kernel_size > x.size:
                break  # Reached the end of the input

            for j in range(len(self.weights)):
                weighted_sum[i //
                             self.strides, j] = np.sum(x[i:i+self.kernel_size, j:j+self.kernel_size] * self.weights[j])

        weighted_sum = weighted_sum + self.biases

        output = self.activation.compute_loss(weighted_sum)
        self.outputs = np.array([output, weighted_sum])

        return output

    def backpropagate(self, gradient: np.ndarray, optimizer: list[Optimizer, Optimizer]) -> np.ndarray:
        """Backpropagation algorithm for Conv1D layer

        Args:
            gradient (np.ndarray): Gradient calculated by loss.compute_derivative() or previous layers output gradient
            optimizer (List[Optimizer, Optimizer]): Optimizer to use for updating the model's parameters. Note that we use 2 different optimizers as then we don't have to check a bunch of times 
            wheter we use 1 or 2 optimizers, and we need 2 optimizers for CNNs

        Returns:
            np.ndarray: Output gradient
        """
        if self.regulizer:
            gradient = self.regulizer.compute_loss(
                gradient, self.weights, self.biases)

        delta = np.average(
            [gradient * self.activation.compute_derivative(output) for output in self.outputs])

        # weights_gradients = delta * self.weights
        weights_gradients = np.zeros(
            (self.inputs.size // self.strides, self.number_of_filters))

        for i in range(0, self.inputs.size, self.strides):
            if i + self.kernel_size > self.inputs.size:
                break  # Reached the end of the input

            for j in range(len(self.weights)):
                weights_gradients[i //
                                  self.strides, j] = np.sum(self.inputs[i:i+self.kernel_size, j:j+self.kernel_size] * delta)

        self.weights, self.biases = optimizer[0].apply_gradients(weights_gradients, np.array(
            delta, dtype=float), self.weights, self.biases)

        return np.dot(delta, self.weights.T)


class Conv2D(Layer):
    def __init__(self, filters: int = 1, kernel_size: tuple = (2, 2), strides: tuple = (1, 1), activation: Activation | str = "relu", regulizer: Regularizer = None, name: str = "Conv2D") -> None:
        """Intializer for the Conv2D layer

        Args:
            filters (int, optional): Amount of filters in the layer. Defaults to 1.
            kernel_size (tuple, optional): Kernel size the layer should use. Defaults to (2, 2).
            strides (tuple, optional): By how much should the kernel move. Defaults to (1, 1).
            activation (Activation | str, optional): Activation function of the layer. Defaults to "relu".
            regulizer (Regularizer, optional): Regulizer for the layer. Defaults to None.
            name (str, optional): Name of the layer. Defaults to "Conv2D".
        """
        self.number_of_filters = filters
        self.kernel_size = kernel_size
        self.strides = strides
        self.activation = ACTIVATIONS[activation] if type(
            activation) == str else activation
        self.weights = np.array([])
        self.biases = np.array([])
        self.regulizer = regulizer
        self.name = name

    def random_initalization(self, weights: list, input_shape: tuple, weight_data_type: np.float_) -> tuple[np.ndarray, np.ndarray]:
        """Random intitalization strategy used for weights generation. Note that this works for layers that don't use units for weight generation like Conv1d and Conv2d

        Args:
            weights (list): Weights shape of the layer
            input_shape (tuple): Input shape of the layer, it's here as it's in the 2 other intialization startegies and it saves as an if
            weight_data_type (np.float_): Data type of the weights. Remember to use np.float32 or np.float64

        Returns:
            tuple[np.ndarray, np.ndarray]: Weights of the layer
        """
        return np.random.randn(*weights).astype(weight_data_type), np.random.randn(self.number_of_filters).astype(weight_data_type)

    def xavier_intialization(self, weights: list, input_shape: tuple, weight_data_type: np.float_) -> tuple[np.ndarray, np.ndarray]:
        """Xavier intitalization strategy used for weights generation. Note that this works for layers that don't use units for weight generation like Conv1d and Conv2d

        Args:
            weights (list): Weights shape of the layer
            input_shape (tuple): Input shape of the layer, which we use to calculate fan_in
            weight_data_type (np.float_): Data type of the weights. Remember to use np.float32 or np.float64

        Returns:
            tuple[np.ndarray, np.ndarray]: Weights of the layer
        """
        weights = np.random.randn(*weights).astype(weight_data_type)
        weights = 2 * weights - 1
        fan_in = input_shape[-1] * self.kernel_size[0] * self.kernel_size[1]
        weights *= np.sqrt(6/(fan_in + self.number_of_filters))
        return weights, np.zeros(self.number_of_filters).astype(weight_data_type)

    def he_intialization(self, weights: list, input_shape: tuple, weight_data_type: np.float_) -> tuple[np.ndarray, np.ndarray]:
        """He intitalization strategy used for weights generation. Note that this works for layers that don't use units for weight generation like Conv1d and Conv2d

        Args:
            weights (list): Weights shape of the layer
            input_shape (tuple): Input shape of the layer, which we use to calculate fan_in
            weight_data_type (np.float_): Data type of the weights. Remember to use np.float32 or np.float64

        Returns:
            tuple[np.ndarray, np.ndarray]: Weights of the layer
        """
        weights = np.random.randn(*weights).astype(weight_data_type)
        fan_in = input_shape[-1] * self.kernel_size[0] * self.kernel_size[1]
        weights *= np.sqrt(2. / fan_in)
        return weights, np.zeros(self.number_of_filters).astype(weight_data_type)

    def generate_weights(self, layers: list[Layer], current_layer_index: int, weight_initalization: str, weight_data_type: np.float_) -> None:
        LAYER_INTIALIZATIONS = {"random": self.random_initalization,
                                "xavier": self.xavier_intialization, "he": self.he_intialization}

        input_shape = layers[current_layer_index -
                             1].output_shape(layers, current_layer_index-1)

        weights = (self.kernel_size[0], self.kernel_size[1],
                   input_shape[-1], self.number_of_filters)

        self.weights, self.biases = LAYER_INTIALIZATIONS[weight_initalization](
            weights, input_shape, weight_data_type)

    def output_shape(self, layers: list, current_layer_index: int) -> tuple:
        self.input_shape = layers[current_layer_index -
                                  1].output_shape(layers, current_layer_index-1)
        height = (self.input_shape[0] -
                  self.kernel_size[0]) // self.strides[0] + 1
        width = (self.input_shape[1] -
                 self.kernel_size[1]) // self.strides[1] + 1
        channels = self.number_of_filters
        self.output_shape_value = (height, width, channels)
        return self.output_shape_value

    def __repr__(self) -> str:
        formatted_output = f'(None, {", ".join(map(str, self.output_shape_value))})'
        return f"{self.name} (Conv2D){' ' * (28 - len(self.name) - 8)}{formatted_output}{' ' * (26-len(formatted_output))}{self.weights.size + self.biases.size}\n"

    def im2col(self, x: np.ndarray) -> None:
        inputs_shape = x.shape
        height = (inputs_shape[0] - self.kernel_size[0]) // self.strides[0] + 1
        width = (inputs_shape[1] - self.kernel_size[1]) // self.strides[1] + 1
        channels = inputs_shape[-1]

        i0 = np.repeat(np.arange(self.kernel_size[0]), self.kernel_size[1])
        i0 = np.tile(i0, channels)
        i1 = self.strides[0] * np.repeat(np.arange(height), width)
        j0 = np.tile(
            np.arange(self.kernel_size[1]), self.kernel_size[0] * channels)
        j1 = self.strides[1] * np.tile(np.arange(width), height)
        i = i0.reshape(-1, 1) + i1.reshape(1, -1)
        j = j0.reshape(-1, 1) + j1.reshape(1, -1)

        k = np.repeat(np.arange(channels),
                      self.kernel_size[0] * self.kernel_size[1]).reshape(-1, 1)

        return x[i, j, k]

    def __call__(self, x: np.ndarray) -> np.ndarray:
        """Call function also known as feed forward function for the Conv2D layer

        Args:
            x (np.ndarray): X dataset

        Returns:
            np.ndarray: Layers output
        """
        input_shape = x.shape

        self.inputs = x

        x = self.im2col(x)

        height = (input_shape[0] -
                  self.kernel_size[0]) // self.strides[0] + 1
        width = (input_shape[1] -
                 self.kernel_size[1]) // self.strides[1] + 1

        weights_col = self.weights.reshape(self.number_of_filters, -1)

        weighted_sum = np.dot(weights_col, x)

        weighted_sum = weighted_sum.reshape(
            self.number_of_filters, height, width).transpose(1, 2, 0)

        output = self.activation.compute_loss(weighted_sum)
        self.outputs = np.array([output, weighted_sum])

        return output

    def backpropagate(self, gradient: np.ndarray, optimizer: list[Optimizer, Optimizer]) -> np.ndarray:
        """Backpropagate algorithm used for Conv2D layer. It's kinda slow right now so it's not recommended to use it but it will be faster in the future

        Args:
            gradient (np.ndarray): Gradient calculated by loss.compute_derivative() or previous layers output gradient
            optimizer (List[Optimizer, Optimizer]): Optimizer to use for updating the model's parameters. Note that we use 2 different optimizers as then we don't have to check a bunch of times 
            wheter we use 1 or 2 optimizers, and we need 2 optimizers for CNNs

        Returns:
            np.ndarray: Output gradient
        """
        if self.regulizer:
            gradient = self.regulizer.compute_loss(
                gradient, self.weights, self.biases)

        self.outputs = self.activation.compute_derivative(self.outputs)
        delta = np.average([gradient * output for output in self.outputs])

        weights_gradients = np.zeros(
            (self.kernel_size[0], self.kernel_size[1], self.inputs.shape[-1], self.number_of_filters))

        delta_array = np.full_like(self.inputs, delta)

        for i in range(0, self.inputs.shape[0], self.strides[0]):
            for j in range(0, self.inputs.shape[1], self.strides[1]):
                if i + self.kernel_size[0] > self.inputs.shape[0] or j + self.kernel_size[1] > self.inputs.shape[1]:
                    break  # Reached the end of self.inputs

                data_slice = tuple([slice(
                    i, i + self.kernel_size[0]), slice(j, j + self.kernel_size[1]), slice(0, -1)])

                for k in range(self.number_of_filters):
                    weights_gradients[:, :, :, k] += np.tensordot(
                        self.inputs[data_slice], delta_array[data_slice],  axes=([0, 1, 2], [0, 1, 2]))

        self.weights, self.biases = optimizer[1].apply_gradients(
            weights_gradients, delta, self.weights, self.biases)

        output_gradient = np.dot(delta, self.inputs)

        return output_gradient


LAYERS_WITHOUT_UNITS = [
    Flatten, Reshape, MaxPool1D, MaxPool2D, Input]
TRAINABLE_LAYERS = [Dense, Dropout, Conv1D, Conv2D, Input]
