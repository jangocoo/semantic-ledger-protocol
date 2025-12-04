from __future__ import annotations
import sys
import time
import json
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from fastdtw import fastdtw
from scipy.spatial.distance import cosine

DB_FILE = "trajectories.jsonl"
MODEL_NAME = "microsoft/phi-2"

tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForCausalLM.from_pretrained(
    MODEL_NAME,
    output_hidden_states=True,
    torch_dtype=torch.float32,
    device_map="auto"
)


def token_trajectory(text: str):
    tokens = tokenizer(text, return_tensors="pt")
    with torch.no_grad():
        out = model(**tokens)
    
    # hidden_states: tuple of (layer0, layer1, ..., layer_last)
    final_layer_hidden = out.hidden_states[-1][0]  # shape: [T, D]

    # Convert to list of CPU numpy vectors
    traj = [v.cpu().float().numpy() for v in final_layer_hidden]
    return traj


def dtw_distance(traj_a, traj_b):
    distance, path = fastdtw(traj_a, traj_b, dist=cosine)
    return distance



def save_trajectory(text, traj):
    record = {
        "text": text,
        "timestamp": time.time(),
        "trajectory": [v.tolist() for v in traj],
    }
    with open(DB_FILE, "a") as f:
        f.write(json.dumps(record) + "\n")


def load_db():
    items = []
    with open(DB_FILE, "r") as f:
        for line in f:
            items.append(json.loads(line))
    return items


def find_parent(new_traj, db):
    best_score = float("inf")
    best_item = None

    for item in db:
        score = dtw_distance(
            new_traj, 
            [torch.tensor(v).numpy() for v in item["trajectory"]]
        )
        if score < best_score:
            best_score = score
            best_item = item
    
    return best_item, best_score


def novelty(new_traj, db):
    parent, score = find_parent(new_traj, db)
    return score


def main() -> None:
    

    print("Semantic Ledger Protocol - Core Prototype Shell")
    print("Type text and press Enter to submit as a concept.")
    print("Commands: /quit or /exit to leave, /help for help.\n")

    for line in sys.stdin:
        text = line.rstrip("\n")
        if not text:
            continue
        if text in ("/quit", "/exit"):
            break
        if text == "/help":
            print("Enter any non-empty line to submit it as a new concept.")
            print("The system will output a novelty score and lineage chain.\n")
            continue

        db = load_db()
        q_traj = token_trajectory(text)
        parent, score = find_parent(q_traj, db)

        print("Parent text:", parent["text"])
        print("Novelty:", score)

        save_trajectory(text, q_traj)



    print("Exiting SLP Core shell.")


if __name__ == "__main__":
    main()


