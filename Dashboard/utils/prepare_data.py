import json
from pathlib import Path

current_path = Path(__file__)
data_path = current_path.parent.parent / 'data'

with open(str(data_path / 'res.json')) as file:
    res = json.load(file)

all_languages = list(res.keys())
most_common = {k: res.get(k).pop('most_common') for k in all_languages}

desc_stat_columns = [{"name": i, "id": i} for i in res.get(all_languages[0]).keys()]
desc_stat_data = list(res.values())

most_common_columns = [{'name': 'language', 'id': 'language'}] + [{'name': i, 'id': i} for i in all_languages]
all_commons = list()
for language in all_languages:
    this_common = most_common.get(language)
    this_common = [f'{k} ({v})' for k, v in this_common.items()]
    this_common = [{language: v} for v in this_common]
    all_commons.append(this_common)

most_common_data = [{'language': idx + 1} for idx in range(len(all_commons[0]))]
for this_common in all_commons:
    for idx, value in enumerate(this_common):
        most_common_data[idx].update(value)


