"""
Convolution and max pooling — minimal from-scratch implementation.

Companion code for README.md's "Simple example" section: a 4x4 input run
through a 3x3 edge-detecting kernel (convolution) and, separately, through
2x2 max pooling. Implemented with plain Python (no ML framework) so the
arithmetic matches the hand computation in README.md exactly, rather than
relying on a framework's internals.

Run:
    python convolutional_neural_network.py
"""


def convolve2d(image: list, kernel: list) -> list:
    """Valid (no padding), stride-1 2D convolution (cross-correlation)."""
    ih, iw = len(image), len(image[0])
    kh, kw = len(kernel), len(kernel[0])
    oh, ow = ih - kh + 1, iw - kw + 1

    output = [[0] * ow for _ in range(oh)]
    for i in range(oh):
        for j in range(ow):
            total = 0
            for a in range(kh):
                for b in range(kw):
                    total += image[i + a][j + b] * kernel[a][b]
            output[i][j] = total
    return output


def max_pool2d(image: list, size: int = 2, stride: int = 2) -> list:
    """Non-overlapping (when stride == size) max pooling."""
    ih, iw = len(image), len(image[0])
    oh, ow = (ih - size) // stride + 1, (iw - size) // stride + 1

    output = [[0] * ow for _ in range(oh)]
    for i in range(oh):
        for j in range(ow):
            block = [
                image[i * stride + a][j * stride + b]
                for a in range(size) for b in range(size)
            ]
            output[i][j] = max(block)
    return output


if __name__ == "__main__":
    image = [
        [1, 2, 3, 0],
        [0, 1, 2, 3],
        [3, 0, 1, 2],
        [2, 3, 0, 1],
    ]
    kernel = [  # vertical-edge detector
        [1, 0, -1],
        [1, 0, -1],
        [1, 0, -1],
    ]

    print("Convolution output:", convolve2d(image, kernel))
    print("Max-pooled output:", max_pool2d(image, size=2, stride=2))
