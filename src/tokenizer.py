import json
from pathlib import Path

class Tokenizer:
    def __init__(self, chars: list[str]) -> None:
        self.chars = chars
        self.char_to_id = {c: i for i, c in enumerate(self.chars)}
        self.id_to_char =  {i: c for i, c in enumerate(self.chars)}

    @classmethod
    def from_text(cls, text: str) -> "Tokenizer":
        chars = sorted(list(set(text)))
        return cls(chars)