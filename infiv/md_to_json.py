import json
from datetime import datetime, timezone
def main(args):
    with open("output.md", "r") as f:
        md_string = f.read()

    with open("output.json", "w") as f:
        time_string = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S %Z")
        data_dict = {
            "title": f"Daily News @ {time_string}",
            "body": md_string,
            "labels": ["report"]
        }
        json.dump(data_dict, f)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    main(parser.parse_args())
