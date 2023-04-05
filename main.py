from options import Options


def main():
	#Setup parser
	options = Options()
	options.build_arg_parser()
	options.run()


if(__name__=="__main__"):
	main()