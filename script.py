import json
import os
from datetime import datetime

import numpy as np
import pandas as pd


def main():
    rows = [
        {"name": "alice", "score": 91},
        {"name": "bob", "score": 87},
    ]
    df = pd.DataFrame(rows)

    payload = {
        "ts": datetime.utcnow().isoformat() + "Z",
        "rows": len(df),
        "mean_score": float(df["score"].mean()),
        "namespace": os.getenv("ADT_DUMMY_NAMESPACE", "(unset)"),
        "numpy_version": np.__version__,
        "pandas_version": pd.__version__,
    }

    print(df)
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
