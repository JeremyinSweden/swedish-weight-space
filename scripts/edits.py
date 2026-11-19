"""Weight edits, random controls and steering hooks (Deviation 5).

Edit family (docs/02_hypothesis.md 2.4): for layer l with unit loop direction u (residual stream),
S = the k columns of W_down[l] with the largest u^T W[:, j] (columns that write toward the loop direction),
    W'[:, S] = W[:, S] - alpha * u (u^T W[:, S]).
Random control (C5): same S, same per-column change norm alpha*|u^T W[:, j]|, random unit direction r:
    W'[:, S] = W[:, S] - alpha * r (u^T W[:, S]).
The arithmetic is done in numpy (testable without torch); only apply/restore touch the model.
Edited checkpoints are never saved: only the diff (column indices + delta values) is written to disk.
"""
import numpy as np


def compute_edit(W, u, k, alpha, direction=None):
    """W: (hidden, inter) numpy array; u: (hidden,) unit vector. Returns (S, delta) with delta (hidden, k)."""
    u = np.asarray(u, np.float64)
    scores = u @ np.asarray(W, np.float64)          # (inter,)
    S = np.argsort(-scores, kind="stable")[:k]
    coeff = scores[S]                                # u^T W[:, S]
    d = u if direction is None else np.asarray(direction, np.float64)
    delta = -alpha * np.outer(d, coeff)              # (hidden, k)
    return S.astype(np.int64), delta


def random_unit(dim, seed, layer):
    rng = np.random.default_rng([int(seed), int(layer)])
    r = rng.standard_normal(dim)
    return r / np.linalg.norm(r)


def edit_plan(weights_by_layer, U, layers, k, alpha, random_seed=None):
    """weights_by_layer: {layer: W numpy}; U: (n_layers, hidden). Returns {layer: (S, delta)} and Frobenius norm."""
    plan, sq = {}, 0.0
    for l in layers:
        W = weights_by_layer[l]
        d = None if random_seed is None else random_unit(W.shape[0], random_seed, l)
        S, delta = compute_edit(W, U[l], k, alpha, direction=d)
        plan[l] = (S, delta)
        sq += float((delta ** 2).sum())
    return plan, sq ** 0.5


def save_plan(path, plan, meta):
    arrays = {}
    for l, (S, delta) in plan.items():
        arrays[f"L{l}_idx"] = S
        arrays[f"L{l}_delta"] = delta.astype(np.float32)
    np.savez_compressed(path, meta=np.array(str(meta)), **arrays)


# ------------------------------------------------------------------ torch side


def down_proj(model, layer):
    return model.model.layers[layer].mlp.down_proj.weight


def read_weights(model, layers):
    return {l: down_proj(model, l).detach().float().cpu().numpy() for l in layers}


class AppliedEdit:
    """Context manager: apply a plan in place, restore the original columns on exit."""

    def __init__(self, model, plan):
        self.model, self.plan, self.saved = model, plan, {}

    def __enter__(self):
        import torch
        with torch.no_grad():
            for l, (S, delta) in self.plan.items():
                W = down_proj(self.model, l)
                idx = torch.as_tensor(S, device=W.device)
                self.saved[l] = W[:, idx].clone()
                new = W[:, idx].detach().cpu().double().numpy() + delta  # MPS has no float64: go to CPU first
                W[:, idx] = torch.as_tensor(new, dtype=W.dtype, device=W.device)
        return self

    def __exit__(self, *exc):
        import torch
        with torch.no_grad():
            for l, (S, _) in self.plan.items():
                W = down_proj(self.model, l)
                W[:, torch.as_tensor(S, device=W.device)] = self.saved[l]
        return False


class Steering:
    """Context manager: at each listed layer, h <- h - alpha_s (h . u) u on the decoder layer output."""

    def __init__(self, model, U, layers, alpha_s):
        self.model, self.U, self.layers, self.alpha_s, self.handles = model, U, layers, alpha_s, []

    def __enter__(self):
        import torch
        dev = next(self.model.parameters()).device
        for l in self.layers:
            u = torch.as_tensor(self.U[l], dtype=torch.float32, device=dev)

            def hook(module, inputs, output, u=u):
                h = output[0] if isinstance(output, tuple) else output
                h2 = h - self.alpha_s * (h @ u).unsqueeze(-1) * u
                if isinstance(output, tuple):
                    return (h2,) + tuple(output[1:])
                return h2

            self.handles.append(self.model.model.layers[l].register_forward_hook(hook))
        return self

    def __exit__(self, *exc):
        for h in self.handles:
            h.remove()
        self.handles = []
        return False
