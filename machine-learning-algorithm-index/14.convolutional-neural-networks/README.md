# Convolutional Neural Networks (CNN)

## Overview

A CNN is a [neural network](../13.neural-networks/README.md) specialized for **grid-structured data** — most commonly images — built from two operations not found in a plain feedforward network: **convolution** (sliding a small learned filter across the input to detect local patterns) and **pooling** (downsampling to reduce resolution while keeping the most salient signal). These two operations bake in an assumption that turns out to be extremely well-suited to images: a useful pattern (an edge, a texture, an eye) can appear anywhere in the frame, so the same filter should be applied at every position rather than learning a separate weight for every pixel.

---

## Intuition

A plain feedforward network fed a flattened image would need a fully separate set of weights for every input pixel, learned entirely independently — it would have to relearn "detect a vertical edge" separately for the top-left corner and the bottom-right corner of the image, since a fully-connected layer has no notion that those two regions might benefit from the same detector.

A **convolutional filter** fixes this by using the *same small set of weights* at every position in the image, sliding across it like a stencil. If the filter has learned to detect vertical edges, it detects them wherever they occur — this is **weight sharing**, and it's what gives CNNs **translation invariance** (a pattern is recognized regardless of where it appears) with drastically fewer parameters than a fully-connected layer over the same input would need.

Stacking several convolutional layers lets early layers detect simple local patterns (edges, colors, textures) and later layers combine those into increasingly complex, larger-scale patterns (shapes, object parts, whole objects) — the same "compose simple pieces into complex ones" idea from [Neural Networks: Intuition](../13.neural-networks/README.md#intuition), specialized for spatial data.

---

## Mathematical formulation

### Convolution (technically cross-correlation)

A filter (kernel) $K$ of size $k \times k$ slides across the input $I$, and at each position computes an elementwise product-and-sum:

$$(I * K)[i,j] = \sum_{a=0}^{k-1}\sum_{b=0}^{k-1} I[i+a,\, j+b] \cdot K[a,b]$$

producing one value in the output **feature map** per position. (Deep learning frameworks compute this without flipping the kernel, which technically makes it cross-correlation rather than true mathematical convolution — a naming quirk that doesn't affect what the network can learn, since the kernel's weights are learned either way.)

### Output size, stride, and padding

For an $n \times n$ input, a $k \times k$ kernel, stride $s$, and padding $p$ (extra border pixels, usually zeros, added before convolving):

$$\text{output size} = \left\lfloor \frac{n + 2p - k}{s} \right\rfloor + 1$$

"Valid" padding ($p=0$) shrinks the feature map with every layer; "same" padding chooses $p$ so the output stays the same size as the input.

### Channels

A color image has 3 input channels (R, G, B); a convolutional layer's filter actually spans *all* input channels at once (a $k \times k \times C_{in}$ filter, not just $k \times k$), and a layer typically learns many such filters in parallel, producing $C_{out}$ output feature maps — one per filter.

### Pooling

Max pooling (most common) or average pooling reduces each small neighborhood to a single value, downsampling the feature map and adding a small amount of local translation invariance beyond what convolution alone provides:

$$\text{maxpool}(region) = \max_{(a,b) \in region} I[a,b]$$

### A typical architecture

Convolution → nonlinearity (ReLU) → pooling, repeated several times to build up increasingly abstract, increasingly downsampled feature maps, then flattened into a plain fully-connected layer (or, in modern architectures, global average pooling) for a final classification/regression output — everything downstream of the conv/pool stack is exactly the plain feedforward network from [Neural Networks](../13.neural-networks/README.md).

---

## Typical hyperparameters

### `kernel_size`

The filter's spatial extent (commonly $3\times 3$ in modern architectures). Larger kernels see more context per layer but cost more compute and parameters per filter.

```python
Conv2d(in_channels=3, out_channels=64, kernel_size=3)
```

### `stride`

How far the filter moves between applications. `stride=1` (most common) preserves the most spatial detail; larger strides downsample faster, sometimes used instead of a separate pooling layer.

### `padding`

Whether (and how much) to pad the input before convolving — see [Output size, stride, and padding](#output-size-stride-and-padding). `"same"` padding is common when the network needs many layers without the feature map shrinking away to nothing.

### `out_channels` (number of filters)

How many distinct patterns a layer can learn to detect simultaneously. Typically increases in deeper layers (fewer, larger spatial feature maps early; more, smaller ones later) as the network trades spatial resolution for a richer set of learned features.

### `pool_size`

The pooling neighborhood size (commonly $2\times 2$, halving both spatial dimensions).

### Modeling choices that matter more than any single constructor argument

- **Architecture depth and filter counts**, almost always adapted from a well-established design (ResNet, EfficientNet, etc.) rather than designed from scratch, given how much engineering effort has already gone into what depth/width trade-offs work well.
- **Transfer learning** — starting from a network pretrained on a large image dataset (e.g., ImageNet) and fine-tuning on a smaller task-specific dataset, rather than training from scratch, is the default approach whenever the target dataset is small relative to what a CNN needs to learn good filters from nothing.
- Data augmentation (random crops, flips, color jitter) — since CNNs have no built-in invariance to scale, rotation, or lighting the way they do to translation, augmentation is often what actually supplies robustness to those variations during training.

---

## Advantages

**Far fewer parameters than a fully-connected network on the same input**, thanks to weight sharing — a $3\times 3$ filter has 9 weights (times input/output channels) regardless of the image's resolution, unlike a fully-connected layer, whose parameter count scales with the number of input pixels.

**Built-in translation invariance** — a learned pattern detector fires wherever that pattern appears in the image, without needing to see every possible position during training.

**Hierarchical feature learning** — early layers learn generic, broadly reusable features (edges, textures) that transfer well across many visual tasks, which is exactly what makes transfer learning so effective for CNNs specifically.

**State of the art (or close to it) for a huge range of vision tasks** — classification, detection, segmentation — often with a shared architectural backbone across all three.

---

## Limitations

**No built-in invariance to rotation, scale, or lighting** — only translation invariance comes for free from the convolution operation itself; other invariances have to come from data augmentation or, in some architectures, specialized layers.

**Still needs substantial labeled data (or a good pretrained starting point)** — a CNN trained from scratch on a small dataset will overfit badly, same underlying issue as any large neural network (see [Neural Networks: Limitations](../13.neural-networks/README.md#limitations)), which is why transfer learning is the default rather than the exception.

**Fixed local receptive field per layer** — a single convolutional layer only sees a small neighborhood at a time; capturing long-range spatial relationships requires stacking enough layers for the effective receptive field to grow large enough, or switching to attention-based vision architectures.

**Compute- and memory-intensive**, especially at high resolution or with many channels — usually requires GPU/accelerator hardware for practical training times.

**Interpretability remains an add-on, not a built-in property** — techniques like Grad-CAM can visualize which regions of an image most influenced a prediction, but there's no equivalent to a decision tree's inherently readable structure.

---

## Simple example

A convolution and a max pool, computed by hand on the same small input:

$$I = \begin{pmatrix} 1 & 2 & 3 & 0 \\ 0 & 1 & 2 & 3 \\ 3 & 0 & 1 & 2 \\ 2 & 3 & 0 & 1 \end{pmatrix}$$

**Convolution** with a $3\times 3$ vertical-edge-detecting kernel $K = \begin{pmatrix} 1&0&-1\\1&0&-1\\1&0&-1 \end{pmatrix}$, stride 1, no padding, gives a $2\times 2$ feature map (output size $= (4-3)/1+1=2$). The top-left output value, for instance, is the elementwise product-and-sum over the top-left $3\times 3$ patch of $I$:

$$(1\cdot1+2\cdot0+3\cdot(\text{-}1)) + (0\cdot1+1\cdot0+2\cdot(\text{-}1)) + (3\cdot1+0\cdot0+1\cdot(\text{-}1)) = (1-3)+(0-2)+(3-1) = -2$$

Repeating for all 4 positions gives:

$$\begin{pmatrix} -2 & -2 \\ 2 & -2 \end{pmatrix}$$

**Max pooling** ($2\times 2$, stride 2) applied directly to the original $4\times 4$ input instead reduces it to a $2\times 2$ map by taking the max of each non-overlapping $2\times 2$ block:

$$\begin{pmatrix} \max(1,2,0,1) & \max(3,0,2,3) \\ \max(3,0,2,3) & \max(1,2,0,1) \end{pmatrix} = \begin{pmatrix} 2 & 3 \\ 3 & 2 \end{pmatrix}$$

### Python example

See [`convolutional_neural_network.py`](convolutional_neural_network.py) for the runnable version, which implements both operations **from scratch with plain Python** (no framework) so they match the by-hand arithmetic above exactly:

```python
feature_map = convolve2d(image, kernel)
pooled = max_pool2d(image, size=2, stride=2)

print("Convolution output:", feature_map)
print("Max-pooled output:", pooled)
```

Expected output (matches the hand computation above):

```text
Convolution output: [[-2, -2], [2, -2]]
Max-pooled output: [[2, 3], [3, 2]]
```

---

## Resources

- [PyTorch `Conv2d` documentation](https://pytorch.org/docs/stable/generated/torch.nn.Conv2d.html) — the standard framework-level convolution layer, output-size formula, and parameters.
- [Stanford CS231n: Convolutional Neural Networks for Visual Recognition](https://cs231n.github.io/convolutional-networks/) — a thorough, widely used course-notes treatment of convolution, pooling, and full CNN architectures.
- [LeCun et al., "Gradient-Based Learning Applied to Document Recognition" (1998)](http://yann.lecun.com/exdb/publis/pdf/lecun-01a.pdf) — the original LeNet paper establishing the conv/pool/fully-connected architecture pattern.
- [*Deep Learning* (Goodfellow, Bengio, Courville), Ch. 9](https://www.deeplearningbook.org/) — the mathematical foundations of convolution and pooling in full generality.

### Core fact to retain

> A CNN replaces a fully-connected layer's "one weight per input position" with a small filter reused (weight-shared) at every position, giving translation invariance and far fewer parameters — pooling then downsamples, and stacking conv/pool blocks builds increasingly abstract spatial features layer by layer.
