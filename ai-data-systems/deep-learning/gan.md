# 生成对抗网络 (Generative Adversarial Networks, GAN)

## 简介
生成对抗网络是2014年由Goodfellow提出的深度学习框架，通过生成器和判别器的博弈对抗学习，能够生成高质量的合成数据，在图像生成、风格迁移等领域取得了惊人成果。

## 核心概念

### 基本架构
GAN由两个神经网络组成：
- **生成器（Generator, G）**：学习从潜在空间到数据空间的映射，生成假样本
- **判别器（Discriminator, D）**：区分真实样本和生成样本

### 博弈过程
- 生成器目标：欺骗判别器，让生成的样本被判别为真实
- 判别器目标：准确区分真实样本和生成样本

### 价值函数（Minimax Game）
$$
\min_G \max_D V(D, G) = \mathbb{E}_{x \sim p_{data}(x)}[\log D(x)] + \mathbb{E}_{z \sim p_z(z)}[\log(1 - D(G(z)))]
$$

### 训练过程
1. 固定G，优化D最大化正确分类概率：
   $$\max_D \mathbb{E}_{x}[\log D(x)] + \mathbb{E}_{z}[\log(1 - D(G(z)))]$$

2. 固定D，优化G最小化被识破概率：
   $$\min_G \mathbb{E}_{z}[\log(1 - D(G(z)))]$$
   实践中使用最大化 $\mathbb{E}_{z}[\log D(G(z))]$ 以获得更好梯度。

### 理论保证
当G和D都有足够容量时，在均衡点：
- 判别器输出 $D(x) = 0.5$（无法区分真假）
- 生成器完美拟合数据分布 $p_g = p_{data}$

### 常见变体
- **DCGAN**：使用卷积层，训练更稳定
- **CGAN**：条件GAN，根据标签生成特定类别
- **WGAN**：使用Wasserstein距离，解决训练不稳定
- **CycleGAN**：实现无配对图像到图像翻译
- **StyleGAN**：分层风格控制，生成高质量人脸

## 实现方式

```python
import torch
import torch.nn as nn
import torch.optim as optim
import torchvision
import torchvision.transforms as transforms

# ===== 生成器 =====
class Generator(nn.Module):
    def __init__(self, latent_dim=100, img_size=28, channels=1):
        super(Generator, self).__init__()
        self.latent_dim = latent_dim
        self.img_size = img_size
        self.channels = channels
        
        self.model = nn.Sequential(
            # 输入: latent_dim x 1 x 1
            nn.ConvTranspose2d(latent_dim, 512, kernel_size=4, stride=1, padding=0),
            nn.BatchNorm2d(512),
            nn.ReLU(inplace=True),
            # 512 x 4 x 4
            
            nn.ConvTranspose2d(512, 256, kernel_size=4, stride=2, padding=1),
            nn.BatchNorm2d(256),
            nn.ReLU(inplace=True),
            # 256 x 8 x 8
            
            nn.ConvTranspose2d(256, 128, kernel_size=4, stride=2, padding=1),
            nn.BatchNorm2d(128),
            nn.ReLU(inplace=True),
            # 128 x 16 x 16
            
            nn.ConvTranspose2d(128, channels, kernel_size=4, stride=2, padding=1),
            nn.Tanh()
            # channels x 32 x 32 (会根据需要调整)
        )
        
        # 调整输出大小为28x28
        self.resize = nn.AdaptiveAvgPool2d((img_size, img_size))
    
    def forward(self, z):
        # z: (batch_size, latent_dim)
        z = z.view(z.size(0), z.size(1), 1, 1)
        img = self.model(z)
        img = self.resize(img)
        return img

# ===== 判别器 =====
class Discriminator(nn.Module):
    def __init__(self, img_size=28, channels=1):
        super(Discriminator, self).__init__()
        
        self.model = nn.Sequential(
            # 输入: channels x 28 x 28
            nn.Conv2d(channels, 128, kernel_size=4, stride=2, padding=1),
            nn.LeakyReLU(0.2, inplace=True),
            nn.Dropout2d(0.25),
            # 128 x 14 x 14
            
            nn.Conv2d(128, 256, kernel_size=4, stride=2, padding=1),
            nn.BatchNorm2d(256),
            nn.LeakyReLU(0.2, inplace=True),
            nn.Dropout2d(0.25),
            # 256 x 7 x 7
            
            nn.Conv2d(256, 512, kernel_size=4, stride=2, padding=1),
            nn.BatchNorm2d(512),
            nn.LeakyReLU(0.2, inplace=True),
            nn.Dropout2d(0.25),
            # 512 x 3 x 3
            
            nn.Conv2d(512, 1, kernel_size=3, stride=1, padding=0),
            # 1 x 1 x 1
        )
    
    def forward(self, img):
        validity = self.model(img)
        return torch.sigmoid(validity.view(img.size(0), -1))

# ===== 条件GAN（CGAN）生成器 =====
class ConditionalGenerator(nn.Module):
    def __init__(self, latent_dim=100, num_classes=10, img_size=28):
        super(ConditionalGenerator, self).__init__()
        
        self.label_emb = nn.Embedding(num_classes, latent_dim)
        
        self.model = nn.Sequential(
            nn.Linear(latent_dim * 2, 256),
            nn.LeakyReLU(0.2, inplace=True),
            nn.Linear(256, 512),
            nn.BatchNorm1d(512),
            nn.LeakyReLU(0.2, inplace=True),
            nn.Linear(512, 1024),
            nn.BatchNorm1d(1024),
            nn.LeakyReLU(0.2, inplace=True),
            nn.Linear(1024, 1 * img_size * img_size),
            nn.Tanh()
        )
        self.img_size = img_size
    
    def forward(self, noise, labels):
        label_embedding = self.label_emb(labels)
        gen_input = torch.cat((label_embedding, noise), -1)
        img = self.model(gen_input)
        img = img.view(img.size(0), 1, self.img_size, self.img_size)
        return img

# ===== 训练流程 =====
def train_gan(generator, discriminator, dataloader, num_epochs=50, 
              latent_dim=100, device='cuda'):
    
    # 优化器
    optimizer_G = optim.Adam(generator.parameters(), lr=0.0002, betas=(0.5, 0.999))
    optimizer_D = optim.Adam(discriminator.parameters(), lr=0.0002, betas=(0.5, 0.999))
    
    # 损失函数
    adversarial_loss = nn.BCELoss()
    
    generator.to(device)
    discriminator.to(device)
    
    for epoch in range(num_epochs):
        for i, (imgs, _) in enumerate(dataloader):
            batch_size = imgs.size(0)
            imgs = imgs.to(device)
            
            # 标签
            real = torch.ones(batch_size, 1).to(device)
            fake = torch.zeros(batch_size, 1).to(device)
            
            # ===== 训练判别器 =====
            optimizer_D.zero_grad()
            
            # 真实图像
            real_loss = adversarial_loss(discriminator(imgs), real)
            
            # 生成图像
            z = torch.randn(batch_size, latent_dim).to(device)
            gen_imgs = generator(z)
            fake_loss = adversarial_loss(discriminator(gen_imgs.detach()), fake)
            
            d_loss = (real_loss + fake_loss) / 2
            d_loss.backward()
            optimizer_D.step()
            
            # ===== 训练生成器 =====
            optimizer_G.zero_grad()
            
            # 生成器希望判别器将生成图像判为真实
            g_loss = adversarial_loss(discriminator(gen_imgs), real)
            g_loss.backward()
            optimizer_G.step()
            
            if i % 100 == 0:
                print(f"Epoch {epoch}/{num_epochs}, Batch {i}/{len(dataloader)}, "
                      f"D_loss: {d_loss.item():.4f}, G_loss: {g_loss.item():.4f}")

# 测试模型创建
latent_dim = 100
G = Generator(latent_dim=latent_dim)
D = Discriminator()

z = torch.randn(16, latent_dim)
generated = G(z)
validity = D(generated)

print(f"生成器输出形状: {generated.shape}")
print(f"判别器输出形状: {validity.shape}")
print(f"生成器参数量: {sum(p.numel() for p in G.parameters()):,}")
print(f"判别器参数量: {sum(p.numel() for p in D.parameters()):,}")
```

## 应用场景
- **图像生成**：人脸生成、艺术创作、数据增强
- **图像编辑**：超分辨率、图像修复、风格迁移
- **文本到图像**：DALL-E、Stable Diffusion、Midjourney
- **视频生成**：DeepFake、视频预测
- **药物发现**：分子生成、蛋白质设计
- **音乐生成**：作曲、音色合成

## 面试要点

1. **Q: GAN训练不稳定的原因是什么？如何改善？**
   A: 原因：1) 生成器和判别器训练不平衡；2) 梯度消失/爆炸；3) 模式崩溃。改善：使用WGAN/GP、谱归一化、渐进式训练、标签平滑、TTUR（调整学习率）。

2. **Q: 什么是模式崩溃（Mode Collapse）？如何解决？**
   A: 模式崩溃指生成器只学会生成少数几类样本，多样性不足。解决方法：WGAN（使用Wasserstein距离）、Unrolled GAN、Minibatch Discrimination、多样性正则项。

3. **Q: WGAN相比原始GAN的改进？**
   A: WGAN使用Wasserstein距离（推土机距离）替代JS散度，解决了梯度消失问题，训练更稳定。通过权重裁剪或梯度惩罚（WGAN-GP）保证判别器满足Lipschitz约束。

4. **Q: 如何评估GAN生成图像的质量？**
   A: 常用指标：1) Inception Score (IS)：衡量生成质量和多样性；2) FID (Fréchet Inception Distance)：衡量生成分布与真实分布的距离；3) Precision/Recall：分别衡量质量和多样性。

## 相关概念

### AI & Data Systems
- [变分自编码器](./vae.md)
- [扩散模型](./diffusion-models.md)
- [神经网络基础](./neural-networks.md)
- [卷积神经网络](./cnn.md)
- [风格迁移](./style-transfer.md)
- [图像生成](./image-generation.md)

### 数学基础
- [概率论与统计](../../mathematics/probability-statistics.md)
- [最优化方法](../../mathematics/optimization.md)
- [博弈论](../../mathematics/game-theory.md)
- [概率分布距离](../../mathematics/distribution-distances.md)
