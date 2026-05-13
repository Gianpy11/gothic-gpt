import json
from pathlib import Path
import torch

BASE_DIR = Path(__file__).resolve().parent.parent
CORPUS_PATH = BASE_DIR / "data" / "processed" / "corpus.txt"
VOCAB_PATH = BASE_DIR / "data" / "processed" / "vocab.json"
TRAIN_PATH = BASE_DIR / "data" / "processed" / "train.pt"
VAL_PATH = BASE_DIR / "data" / "processed" / "val.pt"
VAL_FRACTION = 0.1
 
class Tokenizer:
    def __init__(self, chars: list[str]) -> None:
        self.chars = chars
        self.char_to_id = {c: i for i, c in enumerate(self.chars)}
        self.id_to_char =  {i: c for i, c in enumerate(self.chars)}

    @classmethod
    def from_text(cls, text: str) -> "Tokenizer":
        chars = sorted(list(set(text)))
        return cls(chars)
    
    def save(self, path: Path) -> None:
        with open(path, 'w', encoding='utf-8') as f:
            json.dump({"chars": self.chars}, f, ensure_ascii=False, indent=2)

    @classmethod
    def from_json(cls, path:Path) -> "Tokenizer":
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        return cls(data["chars"])
    
    def encode(self, s: str) -> list[int]:
        return [self.char_to_id[c] for c in s]
    
    def decode(self, ids: list[int]) -> str:
        return "".join([self.id_to_char[i] for i in ids])
    
    @property
    def vocab_size(self) -> int:
        return len(self.chars)


def main() -> None:

    # Reading the content
    print(f"Reading corpus from: {CORPUS_PATH}")
    text = CORPUS_PATH.read_text(encoding="utf-8")

    # Build istance
    tokenizer = Tokenizer.from_text(text)
        
    # Print controls: I use repr to show explictly each character.
    print(f"Vocabulary size: {tokenizer.vocab_size}")
    vocabulary_str = "".join(tokenizer.chars)
    print(f"Vocabulary complete: {repr(vocabulary_str)}")

    # Save vocabulary
    tokenizer.save(VOCAB_PATH)
    print(f"Vocabulary saved in: {VOCAB_PATH}")

    # Encoding entire corpus
    ids = tokenizer.encode(text)
    print(f"Total encode token: {len(ids)}")

    # Convert the list of IDs into a Pytorch tensor
    # Using uint8 to save disk space (1 byte per token)
    # Note: we will cast it to torch.long() during the training loop.
    data = torch.tensor(ids, dtype=torch.uint8) 
    print(f"Full tensor created. Shape: {data.shape}")

    # Calculate the split index (90% train, 10% validation)
    n = int(len(data) * (1 - VAL_FRACTION))

    # Split the tensor into two slices
    # Using .clone() to avoid wasting disk space
    train_data = data[:n].clone()
    val_data = data[n:].clone()
    print(f"Train data: {len(train_data)} tokens")
    print(f"Val data: {len(val_data)} tokens")

    # Save the tensors to disk
    torch.save(train_data, TRAIN_PATH)
    torch.save(val_data, VAL_PATH)
    print(f"Train set saved to: {TRAIN_PATH}")
    print(f"Val set saved to: {VAL_PATH}")


if __name__ == "__main__":
    main()