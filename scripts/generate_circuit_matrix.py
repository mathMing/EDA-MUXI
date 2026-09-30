"""
Circuit MNA Sparse Matrix Generator & SuiteSparse Downloader.
Generates realistic Modified Nodal Analysis (MNA) circuit matrices with:
- High sparsity (average ~3-8 nnz per row)
- Non-symmetric pattern and values (transistor gm terms)
- Voltage source / inductor branch additions (zeros on diagonal, +/-1 branches)
- Random RHS vector b and ground-truth double-precision reference solution x_ref.
"""

import os
import sys
import numpy as np
import scipy.sparse as sp
import scipy.sparse.linalg as spla

def save_matrix_market(filepath, A):
    """Save scipy sparse matrix A in Matrix Market coordinate format."""
    coo = A.tocoo()
    with open(filepath, "w") as f:
        f.write("%%MatrixMarket matrix coordinate real general\n")
        f.write(f"% Generated Circuit MNA Matrix\n")
        f.write(f"{coo.shape[0]} {coo.shape[1]} {coo.nnz}\n")
        for r, c, v in zip(coo.row, coo.col, coo.data):
            # 1-based indexing for Matrix Market format
            f.write(f"{r + 1} {c + 1} {v:.16e}\n")

def save_vector(filepath, v):
    """Save 1D numpy array in Matrix Market array format."""
    with open(filepath, "w") as f:
        f.write("%%MatrixMarket matrix array real general\n")
        f.write(f"{len(v)} 1\n")
        for val in v:
            f.write(f"{val:.16e}\n")

def generate_circuit_mna(num_nodes=500, num_v_sources=50, seed=42):
    """
    Generate an MNA circuit matrix:
    [ G    B ] [ v ] = [ i ]
    [ C    D ] [ j ]   [ e ]
    where:
    - G is nodal conductance matrix (mostly symmetric, positive diagonally dominant)
    - Transistor transconductance gm terms add non-symmetry to G
    - B and C contain +/-1 connections for independent voltage sources
    - D is zero (for ideal voltage sources) or small conductance
    """
    rng = np.random.default_rng(seed)
    n = num_nodes
    m = num_v_sources
    total_dim = n + m

    # 1. Build passive conductance network (resistors and capacitors to ground/neighbors)
    # Average 3-5 resistor connections per node
    row_idx = []
    col_idx = []
    val_idx = []

    # Diagonal self-conductance
    diag_g = np.zeros(n, dtype=np.float64)

    # Grid / random mesh connections
    num_branches = int(n * 2.5)
    for _ in range(num_branches):
        u = rng.integers(0, n)
        v = rng.integers(0, n)
        if u == v:
            continue
        g_val = rng.uniform(0.01, 10.0) # conductance in Siemens
        # Off-diagonal
        row_idx.extend([u, v])
        col_idx.extend([v, u])
        val_idx.extend([-g_val, -g_val])
        diag_g[u] += g_val
        diag_g[v] += g_val

    # Shunt conductance to ground
    for i in range(n):
        g_ground = rng.uniform(0.001, 0.1)
        diag_g[i] += g_ground
        row_idx.append(i)
        col_idx.append(i)
        val_idx.append(diag_g[i])

    # 2. Add non-symmetric transconductance (MOSFET/BJT gm)
    num_transistors = int(n * 0.4)
    for _ in range(num_transistors):
        drain = rng.integers(0, n)
        gate = rng.integers(0, n)
        source = rng.integers(0, n)
        if drain == gate or gate == source:
            continue
        gm = rng.uniform(1.0, 50.0) # transconductance
        # Current from drain to source controlled by V(gate) - V(source)
        # i_d += gm * (V_g - V_s)
        row_idx.extend([drain, drain])
        col_idx.extend([gate, source])
        val_idx.extend([gm, -gm])

    # 3. Add voltage source branches B (n x m) and C (m x n)
    for k in range(m):
        pos_node = rng.integers(0, n)
        neg_node = rng.integers(0, n)
        branch_idx = n + k
        # B matrix (current entering nodes)
        row_idx.append(pos_node)
        col_idx.append(branch_idx)
        val_idx.append(1.0)

        row_idx.append(neg_node)
        col_idx.append(branch_idx)
        val_idx.append(-1.0)

        # C matrix (voltage equation: V_pos - V_neg = E)
        row_idx.append(branch_idx)
        col_idx.append(pos_node)
        val_idx.append(1.0)

        row_idx.append(branch_idx)
        col_idx.append(neg_node)
        val_idx.append(-1.0)

        # Small internal resistance for voltage source on D diagonal to avoid singular D
        row_idx.append(branch_idx)
        col_idx.append(branch_idx)
        val_idx.append(rng.uniform(1e-4, 1e-2))

    A = sp.coo_matrix((val_idx, (row_idx, col_idx)), shape=(total_dim, total_dim)).tocsr()
    # Sum duplicate entries
    A.sum_duplicates()

    # Generate realistic RHS vector b
    b = rng.standard_normal(total_dim)

    # Solve reference solution using SuperLU (high precision)
    lu = spla.splu(A.tocsc())
    x_ref = lu.solve(b)

    # Verify reference solution residual
    res = np.linalg.norm(A.dot(x_ref) - b) / np.linalg.norm(b)
    print(f"Generated MNA matrix size: {total_dim}x{total_dim}, NNZ: {A.nnz}, Sparsity: {100.0 * A.nnz / (total_dim**2):.3f}%, Ref residual: {res:.2e}")

    return A, b, x_ref

def generate_benchmark_suite(out_dir="x:/EDA/data/matrices"):
    os.makedirs(out_dir, exist_ok=True)
    configs = [
        ("circuit_tiny", 100, 10, 101),
        ("circuit_small", 500, 50, 102),
        ("circuit_medium", 2000, 200, 103),
        ("circuit_large", 8000, 500, 104),
    ]

    for name, n_nodes, n_vsrc, seed in configs:
        print(f"\n--- Generating {name} ---")
        A, b, x_ref = generate_circuit_mna(n_nodes, n_vsrc, seed)
        mat_path = os.path.join(out_dir, f"{name}.mtx")
        rhs_path = os.path.join(out_dir, f"{name}_b.vec")
        ref_path = os.path.join(out_dir, f"{name}_xref.vec")

        save_matrix_market(mat_path, A)
        save_vector(rhs_path, b)
        save_vector(ref_path, x_ref)
        print(f"Saved to: {mat_path}, {rhs_path}, {ref_path}")

if __name__ == "__main__":
    generate_benchmark_suite()
