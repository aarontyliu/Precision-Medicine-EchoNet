"""
   Author: Aaron Liu
   Email: tl254@duke.edu
   Created on: June 29 2021
   Code structure reference: https://github.com/milesial/Pytorch-UNet
"""

import torch
import torch.nn as nn
import torch.nn.functional as F


class LevelBlock(nn.Module):
    """(BN ==> ReLU ==> Conv) x 2"""
    def __init__(
            self,
            in_channels,
            out_channels,
            stride=(1, 1),
    ):
        super().__init__()

        self.stride = stride
        self.activation = nn.ReLU(inplace=True)

        self.bn1 = nn.BatchNorm2d(in_channels)
        self.stacked_blocks1 = nn.Conv2d(in_channels,
                                         out_channels,
                                         kernel_size=3,
                                         padding=1,
                                         stride=self.stride[0],
                                         bias=False)
        self.bn2 = nn.BatchNorm2d(out_channels)

        self.stacked_blocks2 = nn.Conv2d(out_channels,
                                         out_channels,
                                         kernel_size=1,
                                         stride=self.stride[1],
                                         bias=False)

    def forward(self, x):
        x = self.stacked_blocks1(self.activation(self.bn1(x)))
        x = self.stacked_blocks2(self.activation(self.bn2(x)))

        return x


class UpSamplingConcatenate(nn.Module):
    """Upscaling"""
    def __init__(self, in_channels, out_channels):
        super().__init__()

        self.up = nn.ConvTranspose2d(in_channels,
                                     out_channels,
                                     kernel_size=2,
                                     stride=2)

    def forward(self, x1, x2):
        x1 = self.up(x1)
        diffY = x2.size()[2] - x1.size()[2]
        diffX = x2.size()[3] - x1.size()[3]
        x1 = F.pad(
            x1,
            [diffX // 2, diffX - diffX // 2, diffY // 2, diffY - diffY // 2])

        x = torch.cat([x2, x1], dim=1)

        return x