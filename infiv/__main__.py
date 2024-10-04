import argparse
def parse_args():
    parser = argparse.ArgumentParser(description='infiv')

    sub_parsers = parser.add_subparsers()
    # subcommand - build - used to build the daily report
    sub_parser = sub_parsers.add_parser("build")
    
    # subcommand - unitrun - used to check the single processing function
    sub_parser = sub_parsers.add_parser('unitrun')
    return parser.parse_args()

def main(args: argparse.Namespace):
    print("hello world")

if __name__ == '__main__':
    args = parse_args()
    main(args)
