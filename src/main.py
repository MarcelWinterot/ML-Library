import numpy as np
import matplotlib.pyplot as plt
from activations import *
from losses import *
from optimizers import *
from regulizers import *


def printProgress(epoch: int, totalEpochs: int, loss: float) -> None:
    barLength = 30
    progress = int(barLength * epoch / totalEpochs)

    progress_bar = "[" + "=" * progress + \
        ">" + "." * (barLength - progress) + "]"
    print(
        f"\r{epoch}/{totalEpochs} {progress_bar} - loss: {loss:.12f}", end='')


class Layer:
    def __init__(self, units: int, activation, regulizer=None, name: str = "Layer") -> None:
        __activations = {'sigmoid': sigmoid(), 'tanh': tanh(
        ), 'relu': ReLU(), 'leaky_relu': LeakyReLU(), 'elu': ELU()}
        self.units = units
        self.name = name
        self.weights = np.array([])
        self.biases = np.random.randn(units)
        if type(activation) == str:
            self.activation = __activations[activation]
        else:
            self.activation = activation
        self.regulizer = regulizer

    def summary(self) -> None:
        print(
            f"{self.name}: {self.units} units.")

    def feedForward(self, x: np.ndarray) -> tuple:
        weightedSum = np.dot(x, self.weights) + self.biases
        output = self.activation.compute_loss(weightedSum)
        return output, weightedSum

    def backpropagate(self, loss: np.ndarray, outputs: np.ndarray, inputs: np.ndarray, optimizer) -> np.ndarray:
        if self.regulizer is not None:
            loss = self.regulizer.computeLoss(loss, self.weights, self.biases)
        delta = np.mean(self.activation.compute_derivative(
            outputs) * loss, axis=0)
        weightsGradients = np.outer(inputs, delta)
        # print(f"Delta: {delta}, weightsGradients: {weightsGradients}")
        weights, biases = optimizer.applyGradients(
            weightsGradients, np.array([delta], dtype=float), self.weights, self.biases)
        self.weights = weights
        self.biases = biases
        loss = np.dot(delta, self.weights.T)
        return loss


class NN:
    def __init__(self, name: str = "NN"):
        self.name = name
        self.layers = []

    def add(self, layer: Layer):
        self.layers.append(layer)

    def summary(self, lineLenght: int = 50) -> None:
        print(f"{self.name}:\n{'='*lineLenght}")
        for layer in self.layers:
            layer.summary()
        print('='*lineLenght)

    def generateWeights(self) -> None:
        for i in range(1, len(self.layers)):
            prevUnits = self.layers[i-1].units
            currUnits = self.layers[i].units
            weights = np.random.randn(prevUnits, currUnits)
            self.layers[i].weights = weights

    def compile(self, lossFunction, optimizer) -> None:
        self.generateWeights()
        self.lossFunction = lossFunction
        self.optimizer = optimizer

    def feedForward(self, x: np.ndarray) -> tuple:
        output = x
        outputs, inputs = [], []
        for layer in self.layers[1:]:
            inputs.append(output)
            output, weightedSum = layer.feedForward(output)
            outputs.append([output, weightedSum])

        return output, outputs, inputs

    def train(self, X: np.ndarray, y: np.ndarray, epochs: int, batchSize: int = 1, verbose: int = 1) -> np.ndarray:
        """Function to train NNs generated using this library. 

        Args:
            X (np.ndarray): X dataset
            y (np.ndarray): y dataset
            epochs (int): number of iterations a model should do while learning
            batchSize (int, optional): amount of information a model will predict before calling the backpropagate function. Defaults to 1.
            verbose (int, optional): controls wheter to display information during training. If set to 0 no information will be provided. Defaults to 1.

        Returns:
            np.ndarray: losses model had during training
        """
        if len(X) != len(y):
            raise "X and y must have the same size"

        if batchSize > len(X):
            raise "Batch size must be equal or smaller than X"

        losses = np.zeros(epochs)
        for epoch in range(epochs):
            for batch in range(0, len(X), batchSize):
                yPred, outputs, inputs = self.feedForward(
                    X[batch:batch+batchSize])

                # print(yPred, outputs, inputs)
                loss = self.lossFunction.computeDerivative(
                    y[batch:batch+batchSize], yPred)

                # Backpropagate
                for i in reversed(range(1, len(self.layers))):
                    loss = self.layers[i].backpropagate(loss, np.array(
                        outputs[i-1]), np.array(inputs[i-1]), self.optimizer)

            loss = self.evaluate(X, y)
            losses[epoch] = loss
            if verbose == 1:
                printProgress(epoch+1, epochs, loss)

        return losses

    def evaluate(self, X: np.ndarray, y: np.ndarray, showPreds: bool = False) -> float:
        yPreds = np.ndarray((X.shape[0], self.layers[-1].units))

        for i, x in enumerate(X):
            result, _, _ = self.feedForward(x)
            yPreds[i] = result

        if showPreds:
            print(np.round(yPreds, 4))
        return self.lossFunction.computeLoss(y, yPreds)


if __name__ == "__main__":
    np.random.seed(1337)
    Network = NN()

    regulizaer = L1L2(1e-4, 1e-5)

    Network.add(Layer(2, "sigmoid", name="Input"))
    Network.add(Layer(2, "leaky_relu", name="Hidden", regulizer=regulizaer))
    Network.add(Layer(1, "sigmoid", name="Output"))

    optimizer = Adam(learningRate=0.2)
    loss = MSE()

    Network.compile(loss, optimizer)
    Network.summary()

    # AND
    X = np.array([[0, 0], [1, 0], [0, 1], [1, 1]])
    y = np.array([[0], [0], [0], [1]])

    print("\n\n STARTING TRAINING \n\n")

    losses = Network.train(X, y, 2500, 2)

    print("\n\n TRAINING FINISHED \n\n")

    Network.evaluate(X, y, showPreds=True)

    plt.plot(range(1, len(losses) + 1), losses)
    plt.xlabel("Epochs")
    plt.ylabel("Loss")
    plt.title("Loss over time")
    plt.show()
