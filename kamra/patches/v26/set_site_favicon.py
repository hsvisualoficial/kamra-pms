from kamra.install import set_site_favicon


def execute():
	# existing sites (demo, nightly, self-hosts) pick the Kamra favicon up
	# on migrate; new sites get it from after_install
	set_site_favicon()
