import os
import re

from setuptools import setup, find_packages

PKG_NAME = "pyrail"
MODULE_NAME = PKG_NAME

# Get metadata from init file of the module
pkg_path = os.path.dirname(__file__)
init_file = open(os.path.join(pkg_path, MODULE_NAME, "__init__.py")).read()
module_metadata = dict(re.findall(r"__(.+)__\s*=\s*['\"](.*?)['\"]", init_file))

setup(
	name=PKG_NAME,
	version=module_metadata["version"],
	packages=find_packages(),
	install_requires=[
		"pyserial>=3.4",
	],
	entry_points={
		"console_scripts": [
			"dccpp = pyrail.tools.dccpp:main",
			"dcchttpd = pyrail.tools.dcchttpd:main"
		]
}
)