import imp

"""
Returns true if the given package exists
"""
def TryModule(module_name, print_name, pip_name):
    try:
        imp.find_module(module_name)
        return True
    except ImportError:
        print("Error: Package \"" + print_name +"\" not found.")
        return False

""" Check for required packages"""
all_found = True
all_found &= TryModule("requests", "Requests", "requests")
all_found &= TryModule("bs4", "BeautifulSoup4", "BeautifulSoup4")#BeautifulSoup4

if not all_found:
	print("Install missing packages with \"pip install -r requirements.txt\"")
