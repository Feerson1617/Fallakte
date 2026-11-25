"""Ordnet einem Text eine konkrete Browserbeobachtung im passenden Lernweg zu."""
import gzip
import json
import re
from collections import defaultdict


def normal(text):
    return ' '.join(text.split())


def niveau(label):
    return label.replace('Foerder', 'Förder')


class Lernwege:
    def __init__(self, qa):
        self.by_module = defaultdict(list)
        self.pairs = {}
        for name in ('PREP', 'UB02', 'UB08', 'Zusatz'):
            file = 'Paarvergleich-' + name
            with gzip.open(qa / (file + '.ndjson.gz'), 'rt') as stream:
                raw = stream.read()
            count = json.loads((qa / (file + '.json')).read_text())['zustaende']
            assert len(raw.splitlines()) == count
            self.pairs[name] = (raw, count)
            for n, line in enumerate(raw.splitlines(), 1):
                row = json.loads(line)
                content = row['neutext']
                first = content.strip().split('\n', 1)[0]
                route = row['weg']
                module = row['modul']
                if module == 'PREP':
                    match = re.match(r'^([1-4][AB])\b', first)
                    stage = match[1] if match else ''
                else:
                    stage = route.split(' · ')[0]
                label = f'{name}.jsonl Zeile {n}'
                elements = {normal(x) for x in [*content.splitlines(), *row['bedienung']] if x}
                self.by_module[module].append((niveau(row['niveau']), stage, route, normal(content), elements, label))
        self.cache = {}

    def find(self, module, tier, path, text):
        if not isinstance(text, str) or not text.strip():
            return ''
        value = normal(text)
        parts = path.split('/')
        stage = method = ''
        if module == 'PREP' and 'chapters' in parts:
            i = int(parts[parts.index('chapters') + 1])
            stage = str(i // 2 + 1) + 'AB'[i % 2]
        if module == 'UB02' and parts[0] == 'stages':
            stage = parts[1]
            if 'strategies' in parts:
                method = parts[parts.index('strategies') + 1]
        if module in ('Tom', 'Celina') and parts[0] == 'stages':
            stage = module + ' ' + str(1 + int(parts[1]))
            if 'checks' in parts:
                method = parts[parts.index('checks') + 1]
        if module == 'UB08' and parts[0] == 'cases':
            stage = parts[1]
        level = niveau(tier)
        if level not in ('Förder', 'ESA', 'MSA', 'AHR'):
            level = ''
        key = module, level, stage, method, value
        if key not in self.cache:
            result = ''
            for actual_level, place, route, content, elements, label in self.by_module[module]:
                if (level and level != actual_level) or (stage and stage != place) or (method and route.split(' · ')[-1] != method):
                    continue
                if value in elements or (' ' in value and value in content):
                    result = label
                    break
            self.cache[key] = result
        return self.cache[key]
