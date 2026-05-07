import json

route_dirs: dict = {}
route_incidents: dict = {}
route_encodings: dict = {}
route_info: dict = {}

def load_data():
    global route_dirs, route_incidents, route_encodings, route_info
    with open("./backend-data/route_dirs.json") as f_dirs:
        route_dirs = json.load(f_dirs, object_hook=lambda d: {int(k):v for k,v in d.items()})
    with open("./backend-data/route_top_incidents.json") as f_incs:
        route_incidents = json.load(f_incs, object_hook=lambda d: {int(k):v for k,v in d.items()})
    with open("./backend-data/route_encodings.json") as f_encs:
        route_encodings = json.load(f_encs, object_hook=lambda d: {int(k):v for k,v in d.items()})
    with open("./backend-data/route_info.json") as f_info:
        route_info_load = json.load(f_info)
        route_info = {int(k):v for k,v in route_info_load.items()}
