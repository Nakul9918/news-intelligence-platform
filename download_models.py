import os
import sys

# Redirect C-level stderr to devnull before torch/gliner import
try:
    null_fd = os.open(os.devnull, os.O_WRONLY)
    os.dup2(null_fd, 2)
    os.close(null_fd)
except Exception:
    pass
import warnings

os.environ["PYTHONWARNINGS"] = "ignore"
os.environ["TORCH_CPP_LOG_LEVEL"] = "ERROR"
warnings.filterwarnings("ignore")

try:
    from gliner import GLiNER
    print("Downloading GLiNER model...")
    model = GLiNER.from_pretrained("urchade/gliner_small-v2.1")
    print("Done! GLiNER model ready.")
except Exception as e:
    print(f"GLiNER initialization notice: {e}")

sys.exit(0)