from instagram_scraper import InstagramScraper
import argparse
import re
import sys


class FollowingCrawler:
    def __init__(self):
        self.scraper_instance, self.scraper_args = self.get_scraper_instance()

    def start_scrape(self):
        if self.scraper_args.login_user and self.scraper_args.login_pass:
            self.scraper_instance.authenticate_with_login()
        else:
            self.scraper_instance.authenticate_as_guest()

        if self.scraper_args.followings_input:
            self.scraper_instance.usernames = list(self.scraper_instance.query_followings_gen(self.scraper_instance.login_user))
            if self.scraper_args.followings_output:
                with open(self.scraper_instance.destination + self.scraper_instance.followings_output, 'w') as file:
                    for username in self.scraper_instance.usernames:
                        file.write(username + "\n")
                # If not requesting anything else, exit
                if self.scraper_args.media_types == ['none'] and self.scraper_args.media_metadata is False:
                    self.scraper_instance.logout()
                    return

        if self.scraper_args.tag:
            self.scraper_instance.scrape_hashtag()
        elif self.scraper_args.location:
            self.scraper_instance.scrape_location()
        elif self.scraper_args.search_location:
            self.scraper_instance.search_locations()
        else:
            self.scraper_instance.scrape()

        self.scraper_instance.save_cookies()

    @staticmethod
    def get_scraper_instance():
        # Initiate scraper
        parser = argparse.ArgumentParser(
            description="instagram-scraper scrapes and downloads an instagram user's photos and videos.",
            epilog="",
            formatter_class=argparse.RawDescriptionHelpFormatter,
            fromfile_prefix_chars='@')

        parser.add_argument('username', help='Instagram user(s) to scrape', nargs='*', default=['lululala_red'])
        parser.add_argument('--destination', '-d', default='./', help='Download destination')
        parser.add_argument('--login-user', '--login_user', '-u', default=None, help='Instagram login user')
        parser.add_argument('--login-pass', '--login_pass', '-p', default=None, help='Instagram login password')
        parser.add_argument('--followings-input', '--followings_input', action='store_true', default=False,
                            help='Compile list of profiles followed by login-user to use as input')
        parser.add_argument('--followings-output', '--followings_output', help='Output followings-input to file in destination')
        parser.add_argument('--filename', '-f', help='Path to a file containing a list of users to scrape')
        parser.add_argument('--quiet', '-q', default=False, action='store_true', help='Be quiet while scraping')
        parser.add_argument('--maximum', '-m', type=int, default=0, help='Maximum number of items to scrape')
        parser.add_argument('--retain-username', '--retain_username', '-n', action='store_true', default=False,
                            help='Creates username subdirectory when destination flag is set')
        parser.add_argument('--media-metadata', '--media_metadata', action='store_true', default=False,
                            help='Save media metadata to json file')
        parser.add_argument('--profile-metadata', '--profile_metadata', action='store_true', default=False,
                            help='Save profile metadata to json file')
        parser.add_argument('--proxies', default={}, help='Enable use of proxies, add a valid JSON with http or/and https urls.')
        parser.add_argument('--include-location', '--include_location', action='store_true', default=False,
                            help='Include location data when saving media metadata')
        parser.add_argument('--media-types', '--media_types', '-t', nargs='+', default=['image', 'video', 'story'],
                            help='Specify media types to scrape')
        parser.add_argument('--latest', action='store_true', default=False, help='Scrape new media since the last scrape')
        parser.add_argument('--latest-stamps', '--latest_stamps', default=None,
                            help='Scrape new media since timestamps by user in specified file')
        parser.add_argument('--cookiejar', '--cookierjar', default=None,
                            help='File in which to store cookies so that they can be reused between runs.')
        parser.add_argument('--tag', action='store_true', default=False, help='Scrape media using a hashtag')
        parser.add_argument('--filter', default=None, help='Filter by tags in user posts', nargs='*')
        parser.add_argument('--filter-location', default=None, nargs="*", help="filter query by only accepting media with location filter as the location id")
        parser.add_argument('--filter-location-file', default=None, type=str, help="file containing list of locations to filter query by")
        parser.add_argument('--location', action='store_true', default=False, help='Scrape media using a location-id')
        parser.add_argument('--search-location', action='store_true', default=False, help='Search for locations by name')
        parser.add_argument('--comments', action='store_true', default=False, help='Save post comments to json file')
        parser.add_argument('--no-check-certificate', action='store_true', default=False, help='Do not use ssl on transaction')
        parser.add_argument('--interactive', '-i', action='store_true', default=False,
                            help='Enable interactive login challenge solving')
        parser.add_argument('--retry-forever', action='store_true', default=False,
                            help='Retry download attempts endlessly when errors are received')
        parser.add_argument('--verbose', '-v', type=int, default=0, help='Logging verbosity level')
        parser.add_argument('--template', '-T', type=str, default='{urlname}', help='Customize filename template')
        parser.add_argument('--log_destination', '-l', type=str, default='', help='destination folder for the instagram-scraper.log file')

        print("=" * 50)
        print(parser)
        print("=" * 50)
        args = parser.parse_args()

        print(args)
        print("=" * 50)

        if (args.login_user and args.login_pass is None) or (args.login_user is None and args.login_pass):
            parser.print_help()
            raise ValueError('Must provide login user AND password')

        if not args.username and args.filename is None and not args.followings_input:
            parser.print_help()
            raise ValueError('Must provide username(s) OR a file containing a list of username(s) OR pass --followings-input')
        elif (args.username and args.filename) or (args.username and args.followings_input) or (args.filename and args.followings_input):
            parser.print_help()
            raise ValueError('Must provide only one of the following: username(s) OR a filename containing username(s) OR --followings-input')

        if args.tag and args.location:
            parser.print_help()
            raise ValueError('Must provide only one of the following: hashtag OR location')

        if args.tag and args.filter:
            parser.print_help()
            raise ValueError('Filters apply to user posts')

        if (args.filter_location or args.filter_location_file) and not args.include_location:
            parser.print_help()
            raise ValueError('Location filter needs locations in metadata to filter properly')

        if args.filename:
            args.usernames = InstagramScraper.get_values_from_file(args.filename)
        else:
            args.usernames = InstagramScraper.parse_delimited_str(','.join(args.username))

        if args.filter_location_file:
            args.filter_locations = InstagramScraper.get_locations_from_file(args.filter_location_file)
        elif args.filter_location:
            locations = {}
            locations.setdefault('', [])
            locations[''] = InstagramScraper.parse_delimited_str(','.join(args.filter_location))
            args.filter_locations = locations

        if args.media_types and len(args.media_types) == 1 and re.compile(r'[,;\s]+').findall(args.media_types[0]):
            args.media_types = InstagramScraper.parse_delimited_str(args.media_types[0])

        if args.retry_forever:
            global MAX_RETRIES
            MAX_RETRIES = sys.maxsize

        scraper = InstagramScraper(**vars(args))

        return scraper, args


if __name__ == "__main__":
    scraper = FollowingCrawler()
    scraper.start_scrape()

