import argparse
import logging

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
# logging.getLogger("requests").setLevel(logging.WARNING)
# logging.getLogger("urllib3").setLevel(logging.WARNING)

def parse_args():
    parser = argparse.ArgumentParser(description="infiv")

    sub_parsers = parser.add_subparsers(dest="command")
    # subcommand - build - used to build the daily report
    sub_parser = sub_parsers.add_parser("build", help="build the markdown daily report")
    sub_parser.add_argument(
        "--src_config", type=str, help="the path of the source config file",
        default="./configs/source.yaml"
    )
    sub_parser.add_argument(
        "--use_embed", action="store_true", help="whether to use embed mode",
        default=False
    )

    # subcommand - unitrun - used to check the single processing function
    sub_parser = sub_parsers.add_parser(
        "unitrun", help="run the unit test for a single spider"
    )
    # subcommand - md2json - used to convert the markdown file to json file
    sub_parser = sub_parsers.add_parser(
        "md2json", help="convert the markdown file to json file"
    )
    return parser.parse_args()


def main(args: argparse.Namespace):
    if args.command == "unitrun":
        # TODO test
        from infiv.spiders.rsshub.cool_paper_arxiv import get_info

        get_info("")
    elif args.command == "build":
        from infiv.build import main

        main(args)
    elif args.command == "md2json":
        from infiv.md_to_json import main
        main(args)
    


if __name__ == "__main__":
    args = parse_args()
    main(args)
