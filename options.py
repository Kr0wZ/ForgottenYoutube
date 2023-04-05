import argparse
import forgotten

import sys

class Options:
	def __init__(self):
		self.parser = None
		self.args = None
		self.executor = forgotten.ForgottenYoutube()

	def build_arg_parser(self):
		epilog = "python3 main.py -u 'PLl9ZdhTSovhwFfkrRD3sL52sN67j8FBwu' -a 'AfsE41Cxfoze641FojkfbFIKlk5218S8-jp852DSs' -u -r -f 'RU'"
		self.parser = argparse.ArgumentParser(description="Made by KrowZ", epilog=epilog, argument_default=argparse.SUPPRESS)

		#If -f then must also have -r

		self.parser.add_argument("-i", "--id", metavar="ID", type=str, required=True, help="Playlist ID")
		self.parser.add_argument("-a", "--api", metavar="API_KEY", type=str, required=True, help="Google API key to interact with Youtube")
		self.parser.add_argument("-u", "--unavailable", action="store_true", help="List deleted and private videos from playlist")
		self.parser.add_argument("-r", "--restricted", action="store_true", help="List videos by regions from playlist")
		self.parser.add_argument("-f", "--filter", metavar="COUNTRY", type=str, help="Filter by country for restricted videos by region")

		self.parser.add_argument("-o", "--output", metavar="FILE", type=str, help="File where results are stored")

		self.args = self.parser.parse_args()


		#Check if user just runs the script without any argument
		if(len(sys.argv) == 1):
			self.parser.print_help()

		#If output option is used alone
		if("output" in self.args and len(vars(self.args)) == 1):
			self.parser.error("Error --output option cannot be alone")

		#Find how to setup the proxy option -> https://stackoverflow.com/questions/30499648/python-mutually-exclusive-arguments-complains-about-action-index
		if("id" in self.args and len(vars(self.args)) == 1):
			self.parser.error("Error --id option cannot be alone")

		if("api-key" in self.args and len(vars(self.args)) == 1):
			self.parser.error("Error --api-key option cannot be alone")

		if("filter" in self.args and not "restricted" in self.args):
			self.parser.error("Error cannot use filter without --restricted")

		if(not "unavailable" in self.args and not "restricted" in self.args):
			self.parser.error("Error you must choose at least --unavailable or --restricted")


	def get_args(self):
		return self.args

	def run(self):

		if("api" in self.args):
			self.executor.set_api_key(self.args.api)

		if("id" in self.args):
			self.executor.set_playlist_id(self.args.id)
		
		if("unavailable" in self.args):
			self.executor.set_unavailable_videos()

		if("restricted" in self.args):
			self.executor.set_restricted_videos()

		if("output" in self.args):
			self.executor.set_output_file(self.args.output)

		if("filter" in self.args):
			self.executor.set_region_filter(self.args.filter)

		self.executor.run()
		


if (__name__ == "__main__"):
	options = Options()
	options.build_arg_parser()