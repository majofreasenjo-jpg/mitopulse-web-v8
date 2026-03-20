import json

from mitopulse_live.normalization.multi_asset import build_multi_asset_snapshot
from mitopulse_live.utils.config import DEFAULT_SYMBOLS


def main() -> None:
    snapshot = build_multi_asset_snapshot(DEFAULT_SYMBOLS[:10])
    print(json.dumps(snapshot, indent=2))


if __name__ == "__main__":
    main()
