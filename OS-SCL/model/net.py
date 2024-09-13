"""
modification made on the basis of link:https://github.com/liuyoude/STgram-MFN
"""
import math
from torch import nn
import torch
from losses import ArcMarginProduct
from model.waveq import TFgram

import torch.nn.functional as F
from model.AF import (
    BasicHead, LeakyReLUHead
)


class Bottleneck(nn.Module):
    def __init__(self, inp, oup, stride, expansion):
        super(Bottleneck, self).__init__()
        self.connect = stride == 1 and inp == oup
        #
        self.conv = nn.Sequential(
            # pw
            nn.Conv2d(inp, inp * expansion, 1, 1, 0, bias=False),
            nn.BatchNorm2d(inp * expansion),
            nn.PReLU(inp * expansion),
            # dw
            nn.Conv2d(inp * expansion, inp * expansion, 3, stride, 1, groups=inp * expansion, bias=False),
            nn.BatchNorm2d(inp * expansion),
            nn.PReLU(inp * expansion),

            # pw-linear
            nn.Conv2d(inp * expansion, oup, 1, 1, 0, bias=False),
            nn.BatchNorm2d(oup),
        )

    def forward(self, x):
        if self.connect:
            return x + self.conv(x)
        else:
            return self.conv(x)


class ConvBlock(nn.Module):
    def __init__(self, inp, oup, k, s, p, dw=False, linear=False):
        super(ConvBlock, self).__init__()
        self.linear = linear
        if dw:
            self.conv = nn.Conv2d(inp, oup, k, s, p, groups=inp, bias=False)
        else:
            self.conv = nn.Conv2d(inp, oup, k, s, p, bias=False)
        self.bn = nn.BatchNorm2d(oup)
        if not linear:
            self.prelu = nn.PReLU(oup)

    def forward(self, x):
        x = self.conv(x)
        x = self.bn(x)
        if self.linear:
            return x
        else:
            return self.prelu(x)


# https://dcase.community/documents/challenge2022/technical_reports/DCASE2022_Liu_8_t2.pdf
Mobilefacenet_bottleneck_setting = [
    # t, c , n ,s
    [2, 128, 2, 2],
    [4, 128, 2, 2],
    [4, 128, 2, 2],

]


class MobileFaceNet(nn.Module):
    def __init__(self,
                 num_class,
                 bottleneck_setting=Mobilefacenet_bottleneck_setting,
                 cfg=None):
        super(MobileFaceNet, self).__init__()

        if cfg["fussion"] == 3 or cfg["fussion"] == 6:
            print("fussion 3/6 test")
            self.conv1 = ConvBlock(1, 64, 3, 2, 1)
        elif cfg["fussion"] == 7:
            self.conv1 = ConvBlock(2, 64, 3, 2, 1)
        else:
            self.conv1 = ConvBlock(3, 64, 3, 2, 1)

        self.dw_conv1 = ConvBlock(64, 64, 3, 1, 1, dw=True)

        self.inplanes = 64
        block = Bottleneck
        self.blocks = self._make_layer(block, bottleneck_setting)

        self.conv2 = ConvBlock(bottleneck_setting[-1][1], 512, 1, 1, 0)
        # 20(10), 4(2), 8(4)
        self.linear7 = ConvBlock(512, 512, (8, 20), 1, 0, dw=True, linear=True)

        self.linear1 = ConvBlock(512, 128, 1, 1, 0, linear=True)

        self.fc_out = nn.Linear(128, num_class)
        # init
        for m in self.modules():
            if isinstance(m, nn.Conv2d):
                n = m.kernel_size[0] * m.kernel_size[1] * m.out_channels
                m.weight.data.normal_(0, math.sqrt(2. / n))
            elif isinstance(m, nn.BatchNorm2d):
                m.weight.data.fill_(1)
                m.bias.data.zero_()

    def _make_layer(self, block, setting):
        layers = []
        for t, c, n, s in setting:
            for i in range(n):
                if i == 0:
                    layers.append(block(self.inplanes, c, s, t))
                else:
                    layers.append(block(self.inplanes, c, 1, t))
                self.inplanes = c

        return nn.Sequential(*layers)

    def forward(self, x):
        x = self.conv1(x)  # （32，64，64，157）
        x = self.dw_conv1(x)  # （32，64，64，157）
        x = self.blocks(x)  # （32，128，8，20）
        x = self.conv2(x)  # （32，512，8，20）
        x = self.linear7(x)  # （32，512，1，1）
        x = self.linear1(x)  # （32，128，1，1）
        feature = x.view(x.size(0), -1)  # （32，128）
        out = self.fc_out(feature)
        return out, feature


class MobileFaceNet2(nn.Module):
    def __init__(self,
                 num_class,
                 bottleneck_setting=Mobilefacenet_bottleneck_setting,
                 cfg=None):
        super(MobileFaceNet2, self).__init__()

        self.conv1 = ConvBlock(2, 64, 3, 2, 1)

        self.dw_conv1 = ConvBlock(64, 64, 3, 1, 1, dw=True)

        self.inplanes = 64
        block = Bottleneck
        self.blocks = self._make_layer(block, bottleneck_setting)

        self.conv2 = ConvBlock(bottleneck_setting[-1][1], 512, 1, 1, 0)
        # 20(10), 4(2), 8(4)
        self.linear7 = ConvBlock(512, 512, (8, 20), 1, 0, dw=True, linear=True)

        self.linear1 = ConvBlock(512, 128, 1, 1, 0, linear=True)

        self.fc_out = nn.Linear(128, num_class)
        # init
        for m in self.modules():
            if isinstance(m, nn.Conv2d):
                n = m.kernel_size[0] * m.kernel_size[1] * m.out_channels
                m.weight.data.normal_(0, math.sqrt(2. / n))
            elif isinstance(m, nn.BatchNorm2d):
                m.weight.data.fill_(1)
                m.bias.data.zero_()

    def _make_layer(self, block, setting):
        layers = []
        for t, c, n, s in setting:
            for i in range(n):
                if i == 0:
                    layers.append(block(self.inplanes, c, s, t))
                else:
                    layers.append(block(self.inplanes, c, 1, t))
                self.inplanes = c

        return nn.Sequential(*layers)

    def forward(self, x):
        x = self.conv1(x)  # （32，64，64，157）
        x = self.dw_conv1(x)  # （32，64，64，157）
        x = self.blocks(x)  # （32，128，8，20）
        x = self.conv2(x)  # （32，512，8，20）
        x = self.linear7(x)  # （32，512，1，1）
        x = self.linear1(x)  # （32，128，1，1）
        feature = x.view(x.size(0), -1)  # （32，128）
        out = self.fc_out(feature)
        return out, feature


class TgramNet(nn.Module):
    def __init__(self, num_layer=3, mel_bins=128, win_len=1024, hop_len=512):
        super(TgramNet, self).__init__()
        # if "center=True" of stft, padding = win_len / 2
        self.conv_extrctor = nn.Conv1d(1, mel_bins, win_len, hop_len, win_len // 2, bias=False)
        self.conv_encoder = nn.Sequential(
            *[nn.Sequential(
                # 313(10) , 63(2), 126(4)
                nn.LayerNorm(313),
                nn.LeakyReLU(0.2, inplace=True),
                nn.Conv1d(mel_bins, mel_bins, 3, 1, 1, bias=False),
            ) for _ in range(num_layer)])

    def forward(self, x):
        out = self.conv_extrctor(x)
        out = self.conv_encoder(out)
        return out


class SCLTFSTgramMFN(nn.Module):

    def __init__(self, num_classes, mode, cfg,
                 c_dim=128,
                 win_len=1024,
                 hop_len=512,
                 bottleneck_setting=Mobilefacenet_bottleneck_setting,
                 margin='arcface', m=0.7, s=30, sub=1, nsc=32,
                 ):
        super().__init__()

        self.margin = margin
        self.cfg = cfg
        print(m)

        self.arcface = ArcMarginProduct(in_features=c_dim, out_features=num_classes,
                                        m=m, s=s, sub=sub)

        self.tgramnet = TgramNet(mel_bins=c_dim, win_len=win_len, hop_len=hop_len)
        self.mobilefacenet = MobileFaceNet(num_class=num_classes,
                                           bottleneck_setting=bottleneck_setting,
                                           cfg=cfg)
        self.mode = mode

        self.TFgramNet = TFgram(classes_num=41)
        head_type = cfg["ht"]
        if head_type == 'basic':
            self.head = BasicHead()
        elif head_type == 'leaky_relu':
            self.head = LeakyReLUHead(cfg)

    def get_tgram(self, x_wav):
        return self.tgramnet(x_wav)

    def forward(self, x_wav, x_mel, label, train=True):
        x_t = self.tgramnet(x_wav).unsqueeze(1)  # (32,1,128,313)

        x_tf = self.TFgramNet(x_wav, train).unsqueeze(1)

        if self.cfg['fussion'] == 1:
            # f=1
            x = torch.cat((x_mel, x_t, x_tf), dim=1)

        elif self.cfg['fussion'] == 2:
            # f=2
            x = x_mel

        out, feature = self.mobilefacenet(x)

        feature = F.normalize(self.head(feature), dim=1)
        # feature = F.normalize(feature, dim=1)                 #no head
        out = self.arcface(feature, label, training=train)
        return out, feature
