import yaml

def read_config(path):
    with open(path) as f:
        data = yaml.load(f, Loader=yaml.FullLoader)
    return data