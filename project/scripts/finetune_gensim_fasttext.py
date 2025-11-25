#!/usr/bin/env python3
"""
Fine-tune a gensim FastText model incrementally using collected user inputs.
Usage:
  - Add new user sentences (one per line) to `project/txt/user_inputs.txt`.
  - Run this script to update/create gensim model at `project/model/gensim_fasttext.model`.
This script is safe for small incremental updates and keeps the original
facebook fastText `.bin` untouched.
"""
import os
import argparse
from gensim.models import FastText
from gensim.utils import simple_preprocess

DEFAULT_MODEL_PATH = "project/model/gensim_fasttext.model"
USER_INPUTS = "project/txt/user_inputs.txt"
ALL_WORDS = "project/txt/all_words.txt"


def load_sentences(path):
    if not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf-8") as f:
        lines = [line.strip() for line in f if line.strip()]
    return [simple_preprocess(line) for line in lines]


def main(args):
    model_path = args.model_out or DEFAULT_MODEL_PATH

    sentences = []
    sentences += load_sentences(ALL_WORDS)
    sentences += load_sentences(USER_INPUTS)

    if not sentences:
        print("No sentences found in user inputs or all_words. Nothing to do.")
        return

    if os.path.exists(model_path):
        print(f"Loading existing gensim FastText model: {model_path}")
        model = FastText.load(model_path)
        print("Building vocab (update=True) and training on new sentences...")
        model.build_vocab(sentences, update=True)
        model.train(sentences, total_examples=len(sentences), epochs=args.epochs)
    else:
        print("No existing gensim model found — training a new gensim FastText model...")
        # parameters can be tuned as needed
        model = FastText(sentences=sentences, vector_size=args.dim, window=5, min_count=1, workers=args.workers, epochs=args.epochs)

    os.makedirs(os.path.dirname(model_path), exist_ok=True)
    model.save(model_path)
    print(f"Saved gensim FastText model to: {model_path}")


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--model-out', help='output path for gensim model (default project/model/gensim_fasttext.model)')
    parser.add_argument('--epochs', type=int, default=3, help='number of epochs when training/fine-tuning')
    parser.add_argument('--dim', type=int, default=300, help='vector dimensionality for new model')
    parser.add_argument('--workers', type=int, default=2, help='number of worker threads')
    args = parser.parse_args()
    main(args)
