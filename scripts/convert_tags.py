#!/usr/bin/env python3
import json
import sys

with open(sys.argv[1], 'r') as tags:
    old_tags = json.load(tags)
    new_tags = {}
    for tag in old_tags['tags']:
        name = tag['name']
        content = tag['content']
        owner = tag['owner']

        new_tags[name] = {'content': content, 'owner': owner}

    with open("new_{}.json".format(sys.argv[1]), 'w') as tag_file:
        json.dump(new_tags, tag_file, sort_keys=True, indent=2)
