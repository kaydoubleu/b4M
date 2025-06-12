import time
from sklearn.datasets import load_breast_cancer
from sklearn.model_selection import train_test_split
from mpyc.runtime import mpc

mpc.start()

# Timer functions
timers = {}
def start_timer(timer_id):
    timers[timer_id] = time.time()

def stop_timer(timer_id):
    elapsed = time.time() - timers[timer_id]
    print(f"Timer {timer_id}: {elapsed:.4f} seconds")

start_timer(1)
start_timer(2)

# Load dataset
X, y = load_breast_cancer(return_X_y=True)

X /= X.max(axis=0)
X_train, X_test, y_train, y_test = train_test_split(X, y, random_state=0)

secfxp = mpc.SecFxp()

# Convert data to secure types
def create_secure_matrix(data):
    rows, cols = data.shape
    return [[secfxp(float(data[i][j])) for j in range(cols)] for i in range(rows)]

def create_secure_vector(data):
    return [secfxp(float(val)) for val in data]

# Convert training and test data to secure types
X_train_sec = create_secure_matrix(X_train)
y_train_sec = create_secure_vector(y_train)
X_test_sec = create_secure_matrix(X_test)
y_test_sec = create_secure_vector(y_test)

stop_timer(2)
start_timer(3)

# Logistic Regression with SGD implementation
class SGDLogistic:
    def __init__(self, n_iter=20, batch_size=2):
        self.n_iter = n_iter
        self.batch_size = batch_size
        self.weights = None
        self.bias = None

    def sigmoid(self, x):
        return 0.5 + 0.25 * x

    def fit(self, X, y):
        n_samples = len(X)
        n_features = len(X[0])

        # Initialize weights and bias
        self.weights = [secfxp(0.01) for _ in range(n_features)]
        self.bias = secfxp(0.0)

        learning_rate = 0.1

        for _ in range(self.n_iter):
            # Simple batch implementation
            for i in range(0, n_samples, self.batch_size):
                end = min(i + self.batch_size, n_samples)
                batch_size = end - i

                batch_preds = []
                for j in range(i, end):
                    z = self.bias
                    for k in range(n_features):
                        z += self.weights[k] * X[j][k]

                    pred = self.sigmoid(z)
                    batch_preds.append(pred)

                for j in range(n_features):
                    gradient = secfxp(0)
                    for k in range(batch_size):
                        error = y[i+k] - batch_preds[k]
                        gradient += error * X[i+k][j]
                    gradient = gradient / batch_size
                    self.weights[j] += learning_rate * gradient

                bias_gradient = secfxp(0)
                for k in range(batch_size):
                    error = y[i+k] - batch_preds[k]
                    bias_gradient += error
                bias_gradient = bias_gradient / batch_size
                self.bias += learning_rate * bias_gradient

    def predict(self, X):
        predictions = []
        for i in range(len(X)):
            z = self.bias
            for j in range(len(self.weights)):
                z += self.weights[j] * X[i][j]

            # Convert probability to class (0 or 1)
            pred = mpc.if_else(self.sigmoid(z) >= 0.5, 1, 0)
            predictions.append(pred)

        return predictions

# Create and train the model
model = SGDLogistic(n_iter=20, batch_size=2)
model.fit(X_train_sec, y_train_sec)

predictions = model.predict(X_test_sec)
differences = [pred - actual for pred, actual in zip(predictions, y_test_sec)]

stop_timer(3)

# Sanity check
correct = 0
for i in range(len(y_test)):
    pred = mpc.run(mpc.output(predictions[i]))
    if pred == y_test[i]:
        correct += 1
print(f"Secure accuracy: {correct}/{len(y_test)}")

weights_revealed = mpc.run(mpc.output(model.weights))
bias_revealed = mpc.run(mpc.output(model.bias))

stop_timer(1)
mpc.shutdown()
