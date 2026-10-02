import re
from pathlib import Path

GENERIC_CHECKPOINT_WORDS = {
    "epoch",
    "epochs",
    "step",
    "steps",
    "checkpoint",
    "checkpoints",
}


def infer_checkpoint_role(
    checkpoint: Path,
) -> str | None:
    """Infer a checkpoint role from its filename."""

    words = re.findall(
        r"[A-Za-z0-9]+",
        checkpoint.stem.lower(),
    )

    for word in words:
        letter_count = sum(char.isalpha() for char in word)

        if letter_count < 2:
            continue

        if word in GENERIC_CHECKPOINT_WORDS:
            continue

        return word

    return None
