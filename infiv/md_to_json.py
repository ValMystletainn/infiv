import json
from datetime import datetime, timezone
import re
def main(args):
    with open("output.md", "r") as f:
        md_string = f.read()
        ## cutting at 60k characters and keep the section with head level 3
        ## find all head level 3
        if len(md_string) > 65535:
            head_level_3_pattern = re.compile(r"^### (.+)$", re.MULTILINE)
            head_level_3_list = head_level_3_pattern.finditer(md_string)
            cutting_index = 0
            for match in head_level_3_list:
                cutting_index = match.start()
                if match.end() > 60000:
                    md_string = md_string[:cutting_index]
                    break
        ## do the cutting at nearest to 60k characters

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
