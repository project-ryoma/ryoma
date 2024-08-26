import numpy as np


class Layer:
    def __init__(self, indim, outdim, activation):
        self.weight = np.random.randn(indim, outdim) * np.sqrt(
            2 / indim
        )  # (input_dim, output_dim)
        self.bias = np.zeros(outdim)  # (output_dim)
        self.grad_w = None
        self.grad_b = None
        self.activation = activation

    def __call__(self, x):
        self.out = np.dot(x, self.weight) + self.bias  # (batch_size, output_dim)
        self.act = self.call_activation(self.out, self.activation)
        return self.act

    def backprop(self, x, dout):
        dact = self.activation_derivative(self.act, self.activation)
        dout *= dact
        dw = np.dot(x.T, dout)
        db = np.sum(dout, axis=0)
        dx = np.dot(dout, self.weight.T)
        # Clip gradients to avoid exploding gradients
        np.clip(dw, -1, 1, out=dw)
        np.clip(db, -1, 1, out=db)

        return dw, db, dx

    def call_activation(self, x, method):
        if method == "relu":
            return x * (x > 0)
        if method == "sig":
            return 1 / (np.exp(-x) + 1)

    def activation_derivative(self, x, activation):
        if activation == "relu":
            return (x > 0).astype("float")
        if activation == "sig":
            return x * (1 - x)


class MLP:
    def __init__(self, lr, indim, outdims, activations):
        self.layers = []
        self.lr = lr
        self.outs = []

        for i in range(len(outdims)):
            layer = Layer(indim, outdims[i], activations[i])
            self.layers.append(layer)
            indim = outdims[i]

    def forward(self, x):
        out = x
        self.outs = [out]
        for layer in self.layers:
            out = layer(out)
            self.outs.append(out)
        return out

    def backward(self, t):
        # Assume mean squared error loss
        d_out = 2 * (self.outs[-1] - t) / t.shape[0]  # Derivative of the loss

        for i in reversed(range(len(self.layers))):
            layer = self.layers[i]
            d_w, d_b, d_out = layer.backprop(self.outs[i], d_out)

            layer.grad_w = d_w
            layer.grad_b = d_b

            layer.weight -= self.lr * layer.grad_w
            layer.bias -= self.lr * layer.grad_b

    def loss(self, pred, t):
        return np.mean((pred - t) ** 2)


# Example usage:
if __name__ == "__main__":
    # Define the network architecture
    input_dim = 4
    output_dims = [5, 3, 1]
    activations = ["relu", "relu", "sig"]
    learning_rate = 0.01

    # Create the MLP
    mlp = MLP(learning_rate, input_dim, output_dims, activations)

    # Sample data
    x = np.array([[1, 0, 3, 4], [2, 3, 1, 1], [4, 1, 5, 3]])
    y = np.array([[1], [0], [0]])

    # Training loop
    epochs = 1000
    for epoch in range(epochs):
        pred = mlp.forward(x)
        mlp.backward(y)
        if epoch % 100 == 0:
            current_loss = mlp.loss(pred, y)
            print(f"Epoch {epoch}, Loss: {current_loss}")
    print(pred)
