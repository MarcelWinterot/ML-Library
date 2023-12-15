import numpy as np
from nano_keras.optimizers import Optimizer


class AdaMax(Optimizer):
    def __init__(self, learning_rate: float = 0.001, beta1: float = 0.9, beta2: float = 0.999, epsilon: float = 1e-7, adjust_biases_shape: bool = False) -> None:
        """Intializer to the AdaMax(Infinite Norm Adaptive Moment Estimation) optimizer.

        Args:
            learning_rate (float, optional): Paramter that specifies how fast the model will learn. Defaults to 0.001.
            beta1 (float, optional): Paramter that controls the exponential moving average of the first moment of the gradient. Defaults to 0.9.
            beta2 (float, optional): Paramter that contorls the exponential moving average of the second moment of the gradient. Defaults to 0.999.
            epsilon (float, optional): Paramter that ensures we don't divide by 0 and adds numerical stability to learning rate. Defaults to 1e-7.
            adjust_biases_shape (bool, optional): Paramter that controles wheter we adjuts the bias gradients and moving averages for biases shapes. Default to False.
        """
        self.learning_rate: float = learning_rate
        self.beta1: float = beta1
        self.beta2: float = beta2
        self.e: float = epsilon
        self.adjust_biases_shape: bool = adjust_biases_shape

        self.m_w: np.ndarray = np.array([])
        self.u_w: np.ndarray = np.array([])
        self.m_b: np.ndarray = np.array([])
        self.u_b: np.ndarray = np.array([])
        self.t: int = 0

    def apply_gradients(self, weightGradients: np.ndarray, biasGradients: np.ndarray, weights: np.ndarray, biases: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        """Function that updates params using provided gradients and AdaMax algorithm. You can read more about it
        at https://paperswithcode.com/method/adamax

        Args:
            weights_gradients (np.ndarray): Weight gradients you've calculated
            bias_gradients (np.ndarray): Bias gradients you've calculated
            weights (np.ndarray): Model or layers weights you want to update
            biases (np.ndarray): Model or layers biases you want to update

        Returns:
            tuple[np.ndarray, np.ndarray]: Updated weights and biases. First element are the weights and second are the biases.
        """
        self.t += 1
        beta1T = self.beta1 ** self.t

        if self.m_w.size == 0:
            self.m_w = np.zeros_like(weights)
            self.u_w = np.zeros_like(weights)
            self.m_b = np.zeros_like(biases)
            self.u_b = np.zeros_like(biases)

        target_shape = weights.shape

        # Adjusting shapes before calculations
        slices = [slice(0, shape) for shape in target_shape]

        self.m_w = self._fill_array(self.m_w, target_shape)[tuple(slices)]
        self.u_w = self._fill_array(self.u_w, target_shape)[tuple(slices)]

        if self.adjust_biases_shape:
            target_shape = biases.shape
            self.m_b = self._fill_array(self.m_b, target_shape)[
                :target_shape[0]]
            self.u_b = self._fill_array(self.u_b, target_shape)[
                :target_shape[0]]

        self.m_w = self.beta1 * self.m_w + (1 - self.beta1) * weightGradients
        self.u_w = np.maximum(self.beta2 * self.u_w, np.abs(weightGradients))

        self.m_b = self.beta1 * self.m_b + (1 - self.beta1) * biasGradients
        self.u_b = np.maximum(self.beta2 * self.u_b, np.abs(biasGradients))

        weights += (self.learning_rate / (1 - beta1T)) * \
            (self.m_w / (self.u_w + self.e))
        biases += (self.learning_rate / (1 - beta1T)) * \
            (self.m_b / (self.u_b + self.e))

        return (weights, biases)
    