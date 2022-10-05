from typing import List

import yaml

from utils.site import Site

def get_site_from_settings_file(filename: str) -> List['Site']:
        objs = []
        with open(filename) as f:
            data = yaml.load(f, Loader=yaml.SafeLoader)
            for sito in data:
                name, link, token, chat_id, dev_chat_ids = sito.values()
                objs.append(Site(name, link, token, chat_id, dev_chat_ids))
        return objs