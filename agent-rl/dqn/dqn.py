import torch.nn as nn

class CustomDeepQNetwork(nn.Module):
    def __init__(self):
        super(CustomDeepQNetwork, self).__init__()

        # Define the fully connected dense layers
        self.fc1 = nn.Sequential(nn.Linear(4, 64), nn.ReLU(inplace=True))
        self.fc2 = nn.Sequential(nn.Linear(64, 64), nn.ReLU(inplace=True))
        self.out_layer = nn.Sequential(nn.Linear(64, 1))

        self.initialize_weights()

    def initialize_weights(self):
        # Loop through modules and initialize weights for linear layers
        for module in self.modules():
            if isinstance(module, nn.Linear):
                nn.init.xavier_uniform_(module.weight)
                nn.init.constant_(module.bias, 0)

    def forward(self, x):
        # Pass the input through the connected layers
        x = self.fc1(x)
        x = self.fc2(x)
        x = self.out_layer(x)

        return x
