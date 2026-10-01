# Approximate Nearest Neighbors (ANN)

## Overview

Approximate nearest neighbor (ANN) search finds vectors that are **almost certainly** among the closest to a query vector, without comparing the query against every stored vector. It trades a small, tunable amount of accuracy (occasionally missing a true neighbor) for orders-of-magnitude speedups, which is what makes nearest-neighbor search usable on millions or billions of vectors.

It's the retrieval engine underneath semantic search, recommendation systems, image/audio similarity search, and the retrieval step of [Retrieval-Augmented Generation](../18.retrieval-augmented-generation/README.md). It's the same "find the most similar stored items" question as [K-Nearest Neighbors](../6.k-nearest-neighbors/README.md), but ANN is purely about answering that question *fast at scale*. It's an indexing technique, not a predictive model, and it has no training labels and no loss function.

> **On the "behind Google Search" framing:** classic web search runs mainly on **inverted keyword indexes** plus hundreds of ranking signals, not on ANN. ANN powers the **embedding-based retrieval** parts of modern search and recommendation stacks. Google's own ANN library, [ScaNN](https://github.com/google-research/google-research/tree/master/scann), is used in Google products and is sold as Vertex AI Vector Search. Most large search systems now combine both: keyword retrieval and vector retrieval, merged and then reranked.

(Not to be confused with "ANN" as in *artificial neural network*. In a retrieval context, ANN means nearest-neighbor search.)

---

## Intuition

### Level 1: for a high schooler

Imagine every song in the world has a "vibe score" made of a few hundred numbers: how energetic it is, how sad, how much bass, and so on. Each song becomes a dot in a huge invisible space, and songs that feel alike sit close together.

When you say "find me songs like this one," the computer looks for the dots closest to your song's dot. The problem is that there are billions of dots, and measuring the distance to every single one would take far too long.

So the computer cheats a little. Ahead of time, it organizes the dots, a bit like a library sorted into sections. When you ask for something, it goes straight to the right section and only checks the dots there. It might occasionally miss a perfect match hiding in another section. That's the "approximate" part. In exchange, the answer comes back in milliseconds instead of hours.

Then comes **reranking**. The quick search grabs maybe 100 likely candidates. A slower, smarter judge then looks closely at just those 100 and puts them in the best order. It's like a talent show: a quick audition round narrows thousands of contestants down to a few finalists, and then expert judges carefully rank the finalists.

### Level 2: for an adult

**Embeddings.** Modern AI models turn text, images, or products into vectors, which are lists of hundreds or thousands of numbers that capture meaning. "How do I fix a flat tire" and "repairing a punctured bike wheel" end up as nearby vectors even though they share almost no words. Closeness is usually measured with cosine similarity or dot product.

**Why exact search doesn't scale.** Finding the true nearest vectors means comparing the query against every stored vector. At 100 million documents and 1,000 dimensions per vector, that's about $10^8 \times 10^3 = 10^{11}$ (100 billion) multiplications *per query*. That's too slow and too expensive for a live product.

**How ANN gets around it.** ANN builds an index in advance so that each query only needs to look at a small fraction of the data. There are three common families, and production systems often combine them:

- **Clustering (IVF):** group the vectors into thousands of clusters. At query time, find the few clusters nearest the query and search only inside them.
- **Graphs (HNSW):** connect each vector to its close neighbors, forming a network. A search starts somewhere and repeatedly hops to whichever neighbor is closer to the query, like asking for directions from person to person until you arrive. Sparse "express" layers on top let it cross long distances quickly.
- **Compression (quantization):** shrink each vector, for example from 4 KB (1,024 float32 values) to 64 bytes (64 one-byte codes). Far more vectors then fit in memory and comparisons get much faster, at a small cost in precision.

**You tune how hard the search tries.** Checking more clusters or exploring more of the graph improves **recall** (the share of true nearest neighbors you actually find) but costs speed. Typical systems reach 95–99% recall at a small fraction of the cost of exact search.

**Retrieve, then rerank.** Production systems work in stages:

1. **Retrieve.** ANN quickly pulls the top 100–1,000 candidates. Speed matters most here, and a few misses are acceptable.
2. **Rerank.** A more expensive model scores only those candidates. Often this is a **cross-encoder**, which reads the query and each document *together* and judges relevance much more accurately than comparing two separately computed vectors.
3. **Return** the best 5–10 results to the user or to an LLM.

The logic is that you can afford an expensive judgment on 200 items, but not on 200 million.

---

## Mathematical formulation

### The problem

Given a database $X = \{x_1, \ldots, x_n\} \subset \mathbb{R}^d$, a query $q$, and a distance $\delta$, exact $k$-NN returns

$$N_k(q) = \underset{S \subseteq X,\ |S| = k}{\arg\min} \sum_{x \in S} \delta(q, x)$$

at a cost of $O(nd)$ per query. An ANN index returns a set $\hat{N}_k(q)$ much more cheaply, and is judged by

$$\text{recall@}k = \frac{|\hat{N}_k(q) \cap N_k(q)|}{k}$$

averaged over queries, plotted against cost (latency, distance evaluations, or memory). There is no single "accuracy." Every ANN method is a **recall-vs-cost curve**, and its hyperparameters choose a point on that curve.

### Cosine, dot product, and Euclidean distance

For unit-normalized vectors, $\|a - b\|^2 = 2 - 2\cos(a, b)$, so ranking by Euclidean distance and ranking by cosine similarity give **identical** results. That's why most vector databases normalize embeddings and then use whichever metric is fastest. Maximum inner product search (MIPS) on *unnormalized* vectors is a genuinely different problem; ScaNN is built specifically for it.

### IVF (inverted file index)

Train $C$ centroids $\mu_1, \ldots, \mu_C$ with [k-means](../8.k-means-clustering/README.md) and assign each vector to its nearest centroid, producing $C$ "inverted lists." A query compares itself to all centroids, then scans only the lists of its `nprobe` nearest centroids:

$$\text{cost} \approx C + \text{nprobe} \cdot \frac{n}{C}$$

This is far cheaper than $n$ when $\text{nprobe} \ll C$. The failure mode is a true neighbor sitting just across a cluster boundary in a list that wasn't probed (see the [Simple example](#simple-example)).

### Product quantization (PQ)

Split each $d$-dimensional vector into $m$ sub-vectors of $d/m$ dimensions, and train a separate k-means codebook of $k_s$ codewords (typically 256) in each subspace. Each vector is stored as $m$ codeword ids, i.e. $m \log_2 k_s$ bits, or **$m$ bytes** when $k_s = 256$.

At query time, **asymmetric distance computation** keeps the query exact and approximates only the database side:

$$\delta(q, x)^2 \approx \sum_{j=1}^{m} \left\| q^{(j)} - c^{(j)}_{\,\text{code}_j(x)} \right\|^2$$

The $m \times k_s$ table of $\|q^{(j)} - c^{(j)}_i\|^2$ is computed once per query, so every database distance becomes **$m$ table lookups and additions** instead of $d$ multiply-adds. PQ distances are coarse, which is why PQ is almost always paired with an **exact rerank** of its top candidates using full-precision vectors.

### Graph search (NSW / HNSW)

Build a graph in which each vector links to approximately its nearest neighbors. Search keeps two sets: a min-heap of **candidates** to expand and a bounded max-heap of the best **ef** results found so far. Repeatedly expand the closest candidate, adding any unvisited neighbor that beats the worst current result. Stop when the closest remaining candidate is farther than the worst result, because nothing reachable from it can improve the list.

**HNSW** (Hierarchical Navigable Small World) stacks this into layers. Each vector appears in layer $\ell$ with probability decaying exponentially in $\ell$, so the upper layers are sparse "express" graphs with long links. A search greedily descends from the top layer to the dense bottom layer, which gives roughly logarithmic search cost in practice.

---

## Typical hyperparameters

### IVF: `nlist` and `nprobe`

- **`nlist`**: number of clusters. A common rule of thumb is $\sim\!4\sqrt{n}$ up to $\sim\!16\sqrt{n}$. More clusters mean smaller lists to scan but more boundary misses.
- **`nprobe`**: clusters searched per query. **This is the main recall/speed knob.** It is set at query time, so it can be tuned without rebuilding the index.

```python
# FAISS
index = faiss.IndexIVFFlat(quantizer, d, nlist)
index.nprobe = 16
```

### HNSW: `M`, `efConstruction`, `efSearch`

- **`M`**: links per node (typical 16–64). Higher means better recall and more memory.
- **`efConstruction`**: beam width while building (typical 100–400). Higher means a better graph and a slower build.
- **`efSearch`** (`ef`): beam width while querying. **This is the main recall/speed knob**, set at query time, and it must be $\ge k$.

```python
# hnswlib
index = hnswlib.Index(space="cosine", dim=d)
index.init_index(max_elements=n, M=16, ef_construction=200)
index.set_ef(64)
```

### PQ: `m` and `nbits`

- **`m`**: number of subspaces, which sets the code size in bytes. It must divide $d$. More subspaces means better precision and more memory.
- **`nbits`**: bits per code (almost always 8, i.e. 256 codewords per subspace).

### Reranking depth

How many ANN candidates get re-scored by the exact distance or a cross-encoder. Deeper reranking recovers recall lost to compression but costs more per query (see the PQ results in the [Simple example](#benchmark-from-the-script)).

### Modeling choices that matter more than any single constructor argument

- **The embedding model.** ANN can only find what the embeddings say is close. A perfect index over poor embeddings returns the wrong documents quickly. Retrieval quality is mostly decided here.
- **Normalization and metric** (see [Cosine, dot product, and Euclidean distance](#cosine-dot-product-and-euclidean-distance)). They must match how the embedding model was trained.
- **Index family vs. constraints:** HNSW when the data fits in RAM and latency is critical; IVF-PQ when memory is the binding constraint (billions of vectors); disk-based graphs (DiskANN) when the data exceeds RAM.
- **Updates and filtering:** HNSW handles inserts well but deletes poorly; IVF handles both but drifts as the data distribution shifts away from its trained centroids. Metadata filters ("only documents from 2025") interact badly with all of them.

---

## Advantages

**Sublinear query cost.** Recall in the 95–99% range typically costs a small percentage of the distance computations of brute force. The script's benchmark reaches 0.995 recall@10 while scanning 3.8% of the data.

**Tunable at query time.** `nprobe` and `efSearch` can be raised for a high-stakes query or lowered under load, without rebuilding anything.

**Memory compression.** PQ shrinks vectors 16–64×, which is what lets billion-scale collections fit on a single machine.

**Mature, battle-tested tooling.** FAISS (Meta), ScaNN (Google), hnswlib, Annoy (Spotify), and the indexes built into vector databases (pgvector, Milvus, Qdrant, Weaviate, Pinecone) all implement these same few families.

**Model-agnostic.** It works on any embedding: text, images, audio, users, products.

---

## Limitations

**Approximate by definition.** Some true neighbors will be missed, and *which* ones are missed isn't uniform. Points near cluster boundaries or in sparse regions are missed more often, so recall can be noticeably worse for unusual queries than the average suggests.

**Build cost and memory overhead.** HNSW graphs can use more memory than the raw vectors, and building them is slow. IVF and PQ need a training pass over representative data.

**Hyperparameters interact and are data-dependent.** The same `nprobe` gives very different recall on different datasets, so settings have to be measured against brute-force ground truth on your own data. They can't be copied from someone else's benchmark.

**Updates, deletes, and filters are awkward.** See [Typical hyperparameters](#modeling-choices-that-matter-more-than-any-single-constructor-argument).

**The curse of dimensionality still applies.** In very high dimensions, distances concentrate (see [KNN: Limitations](../6.k-nearest-neighbors/README.md#limitations)). ANN works well on real embeddings only because they occupy a much lower-dimensional, clustered structure than their nominal dimension suggests. On truly uniform random high-dimensional data, every ANN method degrades toward brute force.

**Vector closeness isn't relevance.** Nearest in embedding space is not always most useful, especially for exact identifiers, numbers, or rare names. This is why production search pairs vector retrieval with keyword retrieval ("hybrid search") and a reranker.

---

## Simple example

### Hand-worked IVF example: why "approximate" happens

Six 2-D points, already clustered with two fixed centroids, $A = (0, 0)$ and $B = (6, 0)$. Each point is assigned to its nearest centroid:

| Point | Coordinates | Dist. to A | Dist. to B | Cluster |
|---|---|---:|---:|:---:|
| p1 | (−1, 0) | 1.000 | 7.000 | A |
| p2 | (1, 1) | 1.414 | 5.099 | A |
| p3 | (2, −1) | 2.236 | 4.123 | A |
| p4 | (3.4, 0) | 3.400 | 2.600 | **B** |
| p5 | (5, 1) | 5.099 | 1.414 | B |
| p6 | (7, 0) | 7.000 | 1.000 | B |

Query $q = (2.8, 0)$. Its distance to centroid A is $2.8$ and to centroid B is $3.2$, so **A is the nearest cluster**.

Exact distances from $q$ to every point:

| Point | Computation | Distance |
|---|---|---:|
| p4 | $\sqrt{0.6^2 + 0^2}$ | **0.6000** |
| p3 | $\sqrt{0.8^2 + 1^2} = \sqrt{1.64}$ | 1.2806 |
| p2 | $\sqrt{1.8^2 + 1^2} = \sqrt{4.24}$ | 2.0591 |
| p5 | $\sqrt{2.2^2 + 1^2} = \sqrt{5.84}$ | 2.4166 |
| p1 | $\sqrt{3.8^2}$ | 3.8000 |
| p6 | $\sqrt{4.2^2}$ | 4.2000 |

So the true top-2 is **{p4, p3}**.

- **`nprobe = 1`:** search only cluster A (p1, p2, p3). Top-2 = **{p3, p2}**. The true nearest neighbor p4 is missed entirely, because it sits just across the boundary in cluster B. Recall@2 = 1/2 = **0.5**. Cost: 2 centroid comparisons + 3 point comparisons.
- **`nprobe = 2`:** search both clusters. Top-2 = **{p4, p3}**. Recall@2 = **1.0**, but this is now just brute force plus overhead.

On real data, `nprobe` is a small fraction of thousands of clusters, so the boundary misses are rare and the savings are huge. The miss here is the same effect, made visible.

### Python example

See [`approximate_nearest_neighbors.py`](approximate_nearest_neighbors.py). It's numpy-only and implements IVF, product quantization (with an exact-rerank stage), and a navigable-graph search from scratch, so the mechanics are readable rather than hidden behind a library call. The IVF core:

```python
class IVFIndex:
    def __init__(self, X, centroids):
        self.X, self.centroids = X, centroids
        assign = sq_dists(X, centroids).argmin(1)
        self.lists = [np.flatnonzero(assign == c) for c in range(len(centroids))]

    def search(self, q, k, nprobe):
        probe = np.argsort(sq_dists(q[None], self.centroids)[0])[:nprobe]
        cand = np.concatenate([self.lists[c] for c in probe])
        d = sq_dists(q[None], self.X[cand])[0]
        return cand[np.argsort(d)[:k]]
```

Part 1 of the script reproduces the hand-worked example above:

```text
cluster A (centroid [0.0, 0.0]): ['p1', 'p2', 'p3']
cluster B (centroid [6.0, 0.0]): ['p4', 'p5', 'p6']

exact distances from q=(2.8, 0):
  p4: 0.6000
  p3: 1.2806
  p2: 2.0591
  p5: 2.4166
  p1: 3.8000
  p6: 4.2000

nprobe=1: top-2 = ['p3', 'p2']

nprobe=2: top-2 = ['p4', 'p3']
```

### Benchmark from the script

Part 2 benchmarks all three families against brute-force ground truth: 20,000 unit-normalized 64-dim vectors drawn around 50 random "topic" directions (a rough stand-in for real embeddings, which are clustered), 200 queries, recall@10, fixed seed. Cost is counted in **distance evaluations per query**, not wall-clock time, because the graph search is a pure-Python loop while the other methods are vectorized numpy, so timing would measure the interpreter rather than the algorithm.

**IVF** (`nlist = 128`):

| nprobe | recall@10 | dist evals / query | % of brute force |
|---:|---:|---:|---:|
| 1 | 0.647 | 343 | 1.7% |
| 2 | 0.882 | 497 | 2.5% |
| 4 | 0.995 | 767 | 3.8% |
| 8 | 1.000 | 1,373 | 6.9% |
| 16 | 1.000 | 2,625 | 13.1% |
| 32 | 1.000 | 5,154 | 25.8% |

**Graph** (16 nearest-neighbor links + 2 random long-range links per node, made bidirectional; avg degree 29.3):

| ef | recall@10 | dist evals / query | % of brute force |
|---:|---:|---:|---:|
| 10 | 0.742 | 440 | 2.2% |
| 20 | 0.907 | 602 | 3.0% |
| 40 | 0.985 | 758 | 3.8% |
| 80 | 1.000 | 935 | 4.7% |
| 160 | 1.000 | 1,238 | 6.2% |

**PQ** (`m = 8` subspaces × 256 codewords = **8 bytes/vector vs. 256 bytes** float32, 32× smaller):

| Mode | recall@10 |
|---|---:|
| PQ codes only | 0.190 |
| PQ top-100 + exact rerank | 0.739 |
| PQ top-500 + exact rerank | 1.000 |

How to read these:

- **Both IVF and the graph show the classic curve.** Recall climbs steeply with the first few extra clusters or beam slots, then flattens. Past ~99% recall you pay for diminishing returns.
- **PQ alone is a poor ranker but a good filter.** 8-byte codes can't order the top 10 precisely (0.190), but the true neighbors are reliably *somewhere* in its top few hundred, so an exact rerank of those candidates recovers full recall. This is retrieve-then-rerank in miniature: a cheap, lossy first stage followed by an accurate second stage on a short list.
- **The graph's random long links are not decoration.** On clustered data, a pure nearest-neighbor graph can be disconnected between clusters, stranding a greedy search in the wrong one. Long links are the "small-world" shortcut. HNSW achieves the same thing more systematically with its sparse upper layers.
- **This synthetic data is friendlier than real embeddings.** It is cleanly clustered, which is why IVF hits 1.000 recall at `nprobe = 8`. Real corpora have fuzzier cluster structure, so expect to need a larger fraction scanned for the same recall. That's why ANN parameters must be validated on your own data.

---

## Resources

- [Malkov & Yashunin, "Efficient and Robust Approximate Nearest Neighbor Search Using Hierarchical Navigable Small World Graphs" (2016/2018)](https://arxiv.org/abs/1603.09320): the HNSW paper.
- [Jégou, Douze & Schmid, "Product Quantization for Nearest Neighbor Search" (2011)](https://ieeexplore.ieee.org/document/5432202): the PQ and IVF-ADC paper behind most compressed vector indexes.
- [Guo et al., "Accelerating Large-Scale Inference with Anisotropic Vector Quantization" (2020)](https://arxiv.org/abs/1908.10396): the ScaNN paper, Google's quantization approach for maximum inner product search.
- [Subramanya et al., "DiskANN" (NeurIPS 2019), reference implementation](https://github.com/microsoft/DiskANN): graph-based ANN for billion-scale data that doesn't fit in RAM.
- [FAISS wiki](https://github.com/facebookresearch/faiss/wiki): practical index-selection guidance (IVF, PQ, HNSW, and their combinations).
- [ann-benchmarks.com](https://ann-benchmarks.com): standardized recall-vs-queries-per-second curves for most major ANN libraries.
- [Nogueira & Cho, "Passage Re-ranking with BERT" (2019)](https://arxiv.org/abs/1901.04085): the cross-encoder reranking pattern.
- In this index: [K-Nearest Neighbors](../6.k-nearest-neighbors/README.md) (the exact version of the same question), [K-Means Clustering](../8.k-means-clustering/README.md) (the building block of IVF and PQ), and [Retrieval-Augmented Generation](../18.retrieval-augmented-generation/README.md) (the most common place ANN shows up today).

### Core fact to retain

> ANN makes nearest-neighbor search fast at scale by organizing vectors in advance (clusters, graphs, or compressed codes) so each query examines only a small fraction of them. You trade a little recall for orders-of-magnitude speed, tune that trade at query time, and use a cheap approximate first stage followed by an accurate rerank of a short list.
