"""Step 4: reproduce the CodeBERT baseline of the Stage 2 paper (Tenekeci et al., ASE 2026).

A port of upstream `cross_pred.py` (github.com/smtnkc/CodeSizeBERT, saved in
data/raw/codesizebert/upstream/) that keeps its protocol:
  - input: the released `code` text (flattened, docstrings/comments/triple-quoted strings removed)
  - the upstream shuffled file, split in order into 5 folds with np.array_split
  - microsoft/codebert-base with a 1-output regression head, MSE loss
  - AdamW, lr 2e-5, no weight decay (the old transformers.AdamW default), no scheduler
  - batch size 32, max length 512, 5 epochs per fold, a fresh model per fold, seed 42
  - for each fold, the epoch with the lowest MSE on the test fold supplies the predictions;
    predictions are rounded to integers before scoring

Differences, none of which change the model's math:
  - runs on Apple MPS instead of CUDA
  - batch 32 is built from 4 micro-batches of 8 (gradient accumulation) to fit in 16 GB
  - each micro-batch is padded to its longest input (max 512) instead of always to 512;
    padding is masked out, so outputs are the same
  - seeds are reset per fold (42 + fold) so an interrupted run can resume at a fold boundary
  - every epoch's test predictions are saved, not only the best epoch's, so that the upstream
    epoch selection (which looks at the test fold) can be compared with a fixed epoch

Subsets:
  released  all 1,787 functions (the reproduction)
  usable    the 1,766 functions whose source could be restored (scripts/02); same order and folds
            procedure, so later structure-augmented models can be compared on identical rows

Run:    uv run python scripts/04_baseline_codebert.py --subset released --target entry
Output: data/derived/baseline/<subset>/<target>_epoch_preds.csv  (one row per function x epoch)
        data/derived/baseline/<subset>/<target>_log.csv          (per-epoch metrics)
"""

import argparse
import os
import random
import time
from pathlib import Path

os.environ["TOKENIZERS_PARALLELISM"] = "false"

import numpy as np
import pandas as pd
import torch
from torch.utils.data import DataLoader
from transformers import AutoModelForSequenceClassification, AutoTokenizer
from transformers import logging as hf_logging

hf_logging.set_verbosity_error()

ROOT = Path(__file__).resolve().parents[1]
SHUFFLED = ROOT / "data" / "raw" / "codesizebert" / "code_cosmic-shuffled-data.csv"
REPAIRED = ROOT / "data" / "derived" / "repaired" / "code_cosmic_repaired.csv"
OUT = ROOT / "data" / "derived" / "baseline"

BASE_MODEL = "microsoft/codebert-base"
SEED = 42
FOLDS = 5
EPOCHS = 5
BATCH = 32
MICRO_BATCH = 8
MAX_LENGTH = 512
LR = 2e-5


def load(subset):
    df = pd.read_csv(SHUFFLED)
    repaired = pd.read_csv(REPAIRED, usecols=["id", "code", "usable"])
    df = df.merge(repaired, on="code", how="left", validate="one_to_one")
    assert df.id.notna().all()
    if subset == "usable":
        df = df[df.usable]
    return df.reset_index(drop=True)


def seed_everything(seed):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)


def batches(texts, targets, tokenizer, shuffle, generator=None):
    order = torch.randperm(len(texts), generator=generator).tolist() if shuffle else list(range(len(texts)))
    loader = DataLoader(order, batch_size=MICRO_BATCH)
    for idx in loader:
        idx = idx.tolist()
        enc = tokenizer([texts[i] for i in idx], truncation=True, padding=True, max_length=MAX_LENGTH, return_tensors="pt")
        yield enc, torch.tensor([targets[i] for i in idx], dtype=torch.float).unsqueeze(1)


def run_fold(fold, train_df, test_df, target, tokenizer, device):
    seed_everything(SEED + fold)
    model = AutoModelForSequenceClassification.from_pretrained(BASE_MODEL, num_labels=1, problem_type="regression").to(device)
    optimizer = torch.optim.AdamW(model.parameters(), lr=LR, weight_decay=0.0)
    loss_fn = torch.nn.MSELoss()
    accum = BATCH // MICRO_BATCH
    train_texts, train_y = train_df.code.tolist(), train_df[target].tolist()
    test_texts = test_df.code.tolist()
    gen = torch.Generator().manual_seed(SEED + fold)

    preds_by_epoch, logs = [], []
    for epoch in range(1, EPOCHS + 1):
        start = time.time()
        model.train()
        total, steps = 0.0, 0
        micro = list(batches(train_texts, train_y, tokenizer, shuffle=True, generator=gen))
        # Group micro-batches into batches of BATCH examples, as in upstream.
        for b in range(0, len(micro), accum):
            group = micro[b : b + accum]
            n = sum(len(y) for _, y in group)
            optimizer.zero_grad()
            batch_loss = 0.0
            for enc, y in group:
                out = model(**{k: v.to(device) for k, v in enc.items()})
                loss = loss_fn(out.logits, y.to(device)) * len(y) / n
                loss.backward()
                batch_loss += loss.item()
            optimizer.step()
            total += batch_loss
            steps += 1

        model.eval()
        preds = []
        with torch.no_grad():
            for enc, _ in batches(test_texts, [0] * len(test_texts), tokenizer, shuffle=False):
                preds.extend(model(**{k: v.to(device) for k, v in enc.items()}).logits.squeeze(-1).cpu().tolist())
        preds = np.array(preds)
        actual = test_df[target].to_numpy()
        mse = float(np.mean((preds - actual) ** 2))
        acc = float(np.mean(np.round(preds) == actual))
        logs.append({"fold": fold + 1, "epoch": epoch, "train_loss": total / steps, "mse": mse, "acc": acc, "seconds": round(time.time() - start)})
        preds_by_epoch.append(pd.DataFrame({"id": test_df.id, "fold": fold + 1, "epoch": epoch, "actual": actual, "pred": preds}))
        print(f"  fold {fold + 1} epoch {epoch}: loss {total / steps:.4f}  mse {mse:.4f}  acc {acc:.4f}  ({time.time() - start:.0f}s)", flush=True)
    return pd.concat(preds_by_epoch), pd.DataFrame(logs)


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--subset", choices=["released", "usable"], required=True)
    parser.add_argument("--target", choices=["entry", "read", "write", "exit"], required=True)
    args = parser.parse_args()

    device = torch.device("mps" if torch.backends.mps.is_available() else "cpu")
    out_dir = OUT / args.subset
    out_dir.mkdir(parents=True, exist_ok=True)
    preds_path = out_dir / f"{args.target}_epoch_preds.csv"
    log_path = out_dir / f"{args.target}_log.csv"

    df = load(args.subset)
    # Same contiguous folds as upstream np.array_split(df, 5), which newer pandas no longer supports.
    splits = [df.iloc[idx] for idx in np.array_split(np.arange(len(df)), FOLDS)]
    done = pd.read_csv(preds_path) if preds_path.exists() else pd.DataFrame(columns=["fold"])
    logs = pd.read_csv(log_path) if log_path.exists() else pd.DataFrame()
    tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL)
    print(f"{args.subset} / {args.target}: {len(df)} functions on {device}", flush=True)

    for fold in range(FOLDS):
        if (fold + 1) in set(done.fold):
            print(f"  fold {fold + 1} already done, skipping", flush=True)
            continue
        test_df = splits[fold]
        train_df = pd.concat([splits[i] for i in range(FOLDS) if i != fold])
        preds, log = run_fold(fold, train_df, test_df, args.target, tokenizer, device)
        done = pd.concat([done, preds], ignore_index=True)
        logs = pd.concat([logs, log], ignore_index=True)
        # Written after every fold so an interrupted run resumes at the next fold.
        done.to_csv(preds_path, index=False)
        logs.to_csv(log_path, index=False)


if __name__ == "__main__":
    main()
