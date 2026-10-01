"""
Approximate nearest neighbor (ANN) search, built from scratch in numpy.

Companion code for README.md. Two parts:

1. The hand-worked IVF example from README.md's "Simple example" section
   (six 2-D points, two fixed clusters), reproducing the hand-computed
   distances and showing how nprobe=1 misses the true nearest neighbor.

2. A benchmark of the three main ANN index families against exact
   brute-force search on synthetic clustered "embeddings":
     - IVF (inverted file / clustering): sweep nprobe
     - PQ  (product quantization / compression): with and without an exact
           rerank of the top candidates -- the retrieve-then-rerank pattern
     - Graph (a navigable small-world graph, the core idea behind HNSW):
           sweep the search beam width ef

Cost is reported as distance evaluations per query rather than wall-clock
time: the graph search is a pure-Python loop and the others are vectorized
numpy, so timing would measure the interpreter, not the algorithm.

Only numpy is required. Run:
    python approximate_nearest_neighbors.py
"""

from __future__ import annotations

import heapq

import numpy as np

SEED = 0


# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------

def sq_dists(queries: np.ndarray, points: np.ndarray) -> np.ndarray:
    """Squared Euclidean distances, shape (len(queries), len(points))."""
    return (
        (queries ** 2).sum(1)[:, None]
        - 2 * queries @ points.T
        + (points ** 2).sum(1)[None, :]
    )


def kmeans(X: np.ndarray, k: int, iters: int = 20, seed: int = SEED) -> tuple[np.ndarray, np.ndarray]:
    """Plain Lloyd's k-means. Returns (centroids, assignments)."""
    rng = np.random.default_rng(seed)
    centroids = X[rng.choice(len(X), k, replace=False)].copy()
    for _ in range(iters):
        assign = sq_dists(X, centroids).argmin(1)
        for c in range(k):
            members = X[assign == c]
            # Re-seed an empty cluster with a random point instead of leaving it dead.
            centroids[c] = members.mean(0) if len(members) else X[rng.integers(len(X))]
    return centroids, sq_dists(X, centroids).argmin(1)


def recall_at_k(found: np.ndarray, truth: np.ndarray) -> float:
    """Average share of the true top-k neighbors that the index returned."""
    k = truth.shape[1]
    return float(np.mean([len(set(f) & set(t)) / k for f, t in zip(found, truth)]))


# ---------------------------------------------------------------------------
# 1. IVF: cluster the data, search only the nprobe nearest clusters
# ---------------------------------------------------------------------------

class IVFIndex:
    def __init__(self, X: np.ndarray, centroids: np.ndarray):
        self.X = X
        self.centroids = centroids
        assign = sq_dists(X, centroids).argmin(1)
        # The "inverted lists": for each cluster, the ids of the vectors in it.
        self.lists = [np.flatnonzero(assign == c) for c in range(len(centroids))]

    @classmethod
    def train(cls, X: np.ndarray, nlist: int) -> "IVFIndex":
        centroids, _ = kmeans(X, nlist)
        return cls(X, centroids)

    def search(self, q: np.ndarray, k: int, nprobe: int) -> tuple[np.ndarray, int]:
        """Returns (top-k ids, number of distance evaluations)."""
        probe = np.argsort(sq_dists(q[None], self.centroids)[0])[:nprobe]
        cand = np.concatenate([self.lists[c] for c in probe])
        d = sq_dists(q[None], self.X[cand])[0]
        top = cand[np.argsort(d)[:k]]
        return top, len(self.centroids) + len(cand)


# ---------------------------------------------------------------------------
# 2. PQ: compress each vector to m one-byte codes, search on the codes
# ---------------------------------------------------------------------------

class PQIndex:
    def __init__(self, X: np.ndarray, m: int, ks: int = 256):
        n, d = X.shape
        assert d % m == 0, "dimension must split evenly into m subspaces"
        self.X = X  # kept only so the rerank stage can use full-precision vectors
        self.m, self.ks, self.sub = m, ks, d // m
        self.codebooks = []
        codes = np.empty((n, m), dtype=np.uint8)
        for j in range(m):
            block = X[:, j * self.sub:(j + 1) * self.sub]
            cb, assign = kmeans(block, ks, iters=15, seed=SEED + j)
            self.codebooks.append(cb)
            codes[:, j] = assign
        self.codes = codes

    def bytes_per_vector(self) -> int:
        return self.m  # one uint8 code per subspace

    def search(self, q: np.ndarray, k: int, rerank: int = 0) -> tuple[np.ndarray, int]:
        """Asymmetric distance: the query stays exact, the database is compressed.

        Build one (m x ks) lookup table of query-to-codeword distances, then
        every database distance is just m table lookups summed. With rerank > 0,
        the top `rerank` PQ candidates are re-scored with exact distances.
        """
        table = np.stack([
            sq_dists(q[None, j * self.sub:(j + 1) * self.sub], self.codebooks[j])[0]
            for j in range(self.m)
        ])  # shape (m, ks)
        approx = table[np.arange(self.m)[None, :], self.codes].sum(1)
        table_cost = self.m * self.ks  # sub-distance evaluations to fill the table
        if not rerank:
            return np.argsort(approx)[:k], table_cost
        cand = np.argpartition(approx, rerank)[:rerank]
        exact = sq_dists(q[None], self.X[cand])[0]
        return cand[np.argsort(exact)[:k]], table_cost + rerank


# ---------------------------------------------------------------------------
# 3. Graph: greedy beam search over a navigable neighbor graph (HNSW's core)
# ---------------------------------------------------------------------------

class GraphIndex:
    def __init__(self, X: np.ndarray, degree: int = 16, long_links: int = 2, chunk: int = 2000):
        """Each node links to its `degree` nearest neighbors (made bidirectional)
        plus `long_links` random far-away nodes.

        The random long links matter: on clustered data a pure nearest-neighbor
        graph can be disconnected between clusters, stranding a greedy search.
        Long links are the "small-world" shortcut; HNSW gets the same effect
        more systematically with its sparse upper layers.
        """
        n = len(X)
        rng = np.random.default_rng(SEED)
        self.X = X
        nbrs: list[set[int]] = [set() for _ in range(n)]
        for start in range(0, n, chunk):
            d = sq_dists(X[start:start + chunk], X)
            idx = np.argpartition(d, degree + 1, axis=1)[:, :degree + 1]
            for row, cand in enumerate(idx):
                i = start + row
                for j in cand:
                    if j != i:
                        nbrs[i].add(int(j))
                        nbrs[int(j)].add(i)
        for i in range(n):
            for j in rng.integers(0, n, long_links):
                if j != i:
                    nbrs[i].add(int(j))
                    nbrs[int(j)].add(i)
        self.nbrs = [np.fromiter(s, dtype=np.int64) for s in nbrs]
        self.entry = int(sq_dists(X.mean(0, keepdims=True), X)[0].argmin())  # start near the middle

    def search(self, q: np.ndarray, k: int, ef: int) -> tuple[np.ndarray, int]:
        """Best-first search keeping the `ef` closest nodes seen so far.

        Stops when the closest unexplored candidate is farther than the worst
        of the current ef results -- nothing reachable from it can improve them.
        This is HNSW's per-layer search routine, run on a single layer.
        """
        def dist(i):
            diff = self.X[i] - q
            return float(diff @ diff)

        d0 = dist(self.entry)
        evals = 1
        visited = {self.entry}
        candidates = [(d0, self.entry)]   # min-heap: closest unexplored first
        results = [(-d0, self.entry)]     # max-heap (negated): worst kept result on top
        while candidates:
            d, i = heapq.heappop(candidates)
            if d > -results[0][0]:
                break
            fresh = [int(j) for j in self.nbrs[i] if j not in visited]
            visited.update(fresh)
            if not fresh:
                continue
            diffs = self.X[fresh] - q
            ds = np.einsum("ij,ij->i", diffs, diffs)
            evals += len(fresh)
            for j, dj in zip(fresh, ds):
                if len(results) < ef or dj < -results[0][0]:
                    heapq.heappush(candidates, (dj, j))
                    heapq.heappush(results, (-dj, j))
                    if len(results) > ef:
                        heapq.heappop(results)
        best = sorted((-nd, i) for nd, i in results)[:k]
        return np.array([i for _, i in best]), evals


# ---------------------------------------------------------------------------
# Part 1: the hand-worked example from README.md
# ---------------------------------------------------------------------------

def hand_example() -> None:
    print("=" * 70)
    print("Part 1: hand-worked IVF example (see README.md 'Simple example')")
    print("=" * 70)
    X = np.array([[-1, 0], [1, 1], [2, -1], [3.4, 0], [5, 1], [7, 0]], dtype=float)
    names = ["p1", "p2", "p3", "p4", "p5", "p6"]
    centroids = np.array([[0, 0], [6, 0]], dtype=float)  # cluster A, cluster B
    q = np.array([2.8, 0.0])

    index = IVFIndex(X, centroids)
    for c, label in enumerate("AB"):
        print(f"cluster {label} (centroid {centroids[c].tolist()}): "
              f"{[names[i] for i in index.lists[c]]}")

    exact = np.sqrt(sq_dists(q[None], X)[0])
    print("\nexact distances from q=(2.8, 0):")
    for name, d in sorted(zip(names, exact), key=lambda t: t[1]):
        print(f"  {name}: {d:.4f}")

    for nprobe in (1, 2):
        top, _ = index.search(q, k=2, nprobe=nprobe)
        print(f"\nnprobe={nprobe}: top-2 = {[names[i] for i in top]}")


# ---------------------------------------------------------------------------
# Part 2: benchmark on synthetic clustered embeddings
# ---------------------------------------------------------------------------

def make_embeddings(n: int, d: int, n_topics: int, n_queries: int) -> tuple[np.ndarray, np.ndarray]:
    """Unit-normalized vectors drawn around random 'topic' directions -- a rough
    stand-in for real text embeddings, which are clustered, not uniform.

    On unit vectors, ranking by Euclidean distance is identical to ranking by
    cosine similarity (||a-b||^2 = 2 - 2cos), so L2 is used throughout.
    """
    rng = np.random.default_rng(SEED)
    topics = rng.normal(size=(n_topics, d))
    labels = rng.integers(0, n_topics, n + n_queries)
    V = topics[labels] + 0.6 * rng.normal(size=(n + n_queries, d))
    V /= np.linalg.norm(V, axis=1, keepdims=True)
    return V[:n].astype(np.float32), V[n:].astype(np.float32)


def benchmark() -> None:
    n, d, k = 20_000, 64, 10
    X, Q = make_embeddings(n=n, d=d, n_topics=50, n_queries=200)

    print("\n" + "=" * 70)
    print(f"Part 2: benchmark -- {n:,} vectors x {d} dims, {len(Q)} queries, recall@{k}")
    print("=" * 70)

    truth = np.argsort(sq_dists(Q, X), axis=1)[:, :k]
    print(f"\nExact brute force: recall 1.000, {n:,} distance evals/query, "
          f"{d * 4} bytes/vector (float32)")

    # --- IVF ---
    nlist = 128
    ivf = IVFIndex.train(X, nlist=nlist)
    print(f"\nIVF (nlist={nlist}):")
    print(f"  {'nprobe':>6}  {'recall':>6}  {'dist evals/query':>17}  {'% of exact':>10}")
    for nprobe in (1, 2, 4, 8, 16, 32):
        res = [ivf.search(q, k, nprobe) for q in Q]
        evals = np.mean([e for _, e in res])
        r = recall_at_k(np.array([t for t, _ in res]), truth)
        print(f"  {nprobe:>6}  {r:>6.3f}  {evals:>17,.0f}  {evals / n:>9.1%}")

    # --- PQ ---
    m = 8
    pq = PQIndex(X, m=m)
    print(f"\nPQ (m={m} subspaces x 256 codewords): {pq.bytes_per_vector()} bytes/vector "
          f"({d * 4 // pq.bytes_per_vector()}x smaller than float32)")
    print(f"  {'mode':<26}  {'recall':>6}")
    for label, rerank in (("PQ codes only", 0), ("PQ top-100 + exact rerank", 100),
                          ("PQ top-500 + exact rerank", 500)):
        found = np.array([pq.search(q, k, rerank=rerank)[0] for q in Q])
        print(f"  {label:<26}  {recall_at_k(found, truth):>6.3f}")
    print("  (PQ scores every vector via table lookups -- cheap, but still O(n);"
          " production systems pair it with IVF, i.e. IVF-PQ)")

    # --- Graph ---
    graph = GraphIndex(X, degree=16, long_links=2)
    avg_deg = np.mean([len(nb) for nb in graph.nbrs])
    print(f"\nGraph (16-NN links + 2 random long links per node, avg degree {avg_deg:.1f}):")
    print(f"  {'ef':>6}  {'recall':>6}  {'dist evals/query':>17}  {'% of exact':>10}")
    for ef in (10, 20, 40, 80, 160):
        res = [graph.search(q, k, ef) for q in Q]
        evals = np.mean([e for _, e in res])
        r = recall_at_k(np.array([t for t, _ in res]), truth)
        print(f"  {ef:>6}  {r:>6.3f}  {evals:>17,.0f}  {evals / n:>9.1%}")


if __name__ == "__main__":
    hand_example()
    benchmark()
