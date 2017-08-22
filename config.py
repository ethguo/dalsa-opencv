from yaml import safe_load

def YAMLObject(obj):
	if type(obj) is dict:
		return YAMLDict(obj)
	elif type(obj) is list:
		return YAMLList(obj)
	else:
		return obj

class YAMLDict (dict):
	def __init__(self, obj):
		obj = {key: YAMLObject(value) for key, value in obj.items()}
		dict.__init__(self, obj)

	def __getattr__(self, name):
		return dict.__getitem__(self, name)

class YAMLList (list):
	def __init__(self, obj):
		obj = [YAMLObject(item) for item in obj]
		list.__init__(self, obj)

def loadYAML(path):
	f = open(path)
	obj = safe_load(f)
	return YAMLObject(obj)