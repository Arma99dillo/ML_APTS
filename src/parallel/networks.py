import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
import torchvision
import torchvision.transforms as transforms

class BasicBlock(nn.Module):
    expansion = 1
    def __init__(self, in_planes, planes, stride=1):
        super(BasicBlock, self).__init__()
        self.conv1 = nn.Conv2d(in_planes, planes, kernel_size=3, stride=stride, padding=1, bias=False)
        self.bn1 = nn.BatchNorm2d(planes)
        self.conv2 = nn.Conv2d(planes, planes, kernel_size=3, stride=1, padding=1, bias=False)
        self.bn2 = nn.BatchNorm2d(planes)

        self.shortcut = nn.Sequential()
        if stride != 1 or in_planes != self.expansion * planes:
            self.shortcut = nn.Sequential(
                nn.Conv2d(in_planes, self.expansion * planes, kernel_size=1, stride=stride, bias=False),
                nn.BatchNorm2d(self.expansion * planes)
            )

    def forward(self, x):
        out = F.relu(self.bn1(self.conv1(x)))
        out = self.bn2(self.conv2(out))
        out += self.shortcut(x)
        out = F.relu(out)
        return out

class ResNet(nn.Module):
    # Number of layers is 4, number of classes is 10. This is equivalent to the ResNet-18 architecture.
    def __init__(self, block=BasicBlock, num_layers=4, num_classes=10):
        super(ResNet, self).__init__()
        self.in_planes = 64
        self.module = nn.ModuleList()
        self.layer_list = [nn.Conv2d(3, 64, kernel_size=3, stride=1, padding=1, bias=False), nn.BatchNorm2d(64), nn.ReLU()]

        for l in range(num_layers):
            blocks = self._make_layer(block, (l+1)*64, 1, stride=min(2,l+1))
            for b in range(len(blocks)):
                self.layer_list.append(blocks[b])
        self.linear = nn.Sequential(
            nn.AvgPool2d(16),  # Adjust the pooling size to match the input image size
            nn.Flatten(),
            nn.Linear( (l+1) * 64 * block.expansion, num_classes)
        )
        self.layer_list.append(self.linear)
        for l in range(len(self.layer_list)):
            self.module.add_module(f'layer{l}', self.layer_list[l])
        
    def _make_layer(self, block, planes, num_blocks, stride):
        strides = [stride] + [1] * (num_blocks - 1)
        layers = []
        for stride in strides:
            layers.append(block(self.in_planes, planes, stride))
            self.in_planes = planes * block.expansion
        return layers

    def forward(self, x):
        for module in self.module: # Adaptive forward depending on the number of layers and blocks
            print(x.shape)
            x = module(x)
        return x
