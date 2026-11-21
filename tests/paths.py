"""Run the complete simple Laura path via its rendered controls."""
from pathlib import Path

LAURA_PATH = Path(__file__).with_name('laura_path.js').read_text()


def complete_laura(page, tier, correct_first=False, stages=5, step_label='Laura'):
    return page.evaluate(LAURA_PATH, dict(tier=tier, correctFirst=correct_first, stages=stages, stepLabel=step_label))
