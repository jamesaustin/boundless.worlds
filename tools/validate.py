#!/usr/bin/env python3
# -*- coding: latin-1 -*-
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
from json import dumps as json_dumps, load as json_load

from pathlib import Path
from collections import Counter, defaultdict

import logging
LOG = logging.getLogger(__name__)

def _iterate_references(node):
    if isinstance(node, list):
        for v in node:
            yield from _iterate_references(v)
    elif isinstance(node, dict):
        node_type = node.get('type', None)
        node_reference = node.get('reference', None)
        if node_type and node_type == 'reference' and node_reference:
            yield node_reference
        for v in node.values():
            yield from _iterate_references(v)

def parse_args():
    parser = ArgumentParser(formatter_class=ArgumentDefaultsHelpFormatter)
    parser.add_argument('--config', default='.')
    group = parser.add_argument_group('debugging options')
    group.add_argument('--verbose', '-v', action='store_true')
    group.add_argument('--debug', action='store_true')
    args = parser.parse_args()

    if args.debug:
        level = logging.DEBUG
    elif args.verbose:
        level = logging.INFO
    else:
        level = logging.WARNING
    logging.basicConfig(format='%(message)s', level=level)
    LOG.debug('# %s', args)

    return args

def main():
    args = parse_args()

    # TODO handle the nodes in: biomeparts, decorations, images, substrate
    config_type_to_location = {
        'BIOME': 'biomes',
        'INSTANCE': 'instances',
        'NOISE2D': 'noise2d',
        'NOISE3D': 'noise3d',
        'STRATA': 'strata',
        'WORLD': 'worlds',
    }
    bad_config_location = {}
    num_config_types = Counter()

    nodes_by_name = {}
    nodes_by_path = {}
    nodes_by_type = defaultdict(dict)

    for path in Path(args.config).rglob('*.json'):
        LOG.info('# Considering: %s', path)
        with path.open() as f:
            config = json_load(f)

            # Extract the toplevel type of the node.
            config_type = config.get('@configType', None)
            if not config_type:
                LOG.error('# Missing "@configType" from: %s', path)
            else:
                num_config_types[config_type] += 1

                # Confirm the node is in the expected folder.
                expected_path = config_type_to_location.get(config_type, None)
                if not expected_path:
                    LOG.error('# Unknown location for type "%s": %s', config_type, path)
                elif expected_path != path.relative_to(args.config).parts[0]:
                    LOG.error('# Move %s "%s" to "%s"', config_type, path, expected_path)
                    bad_config_location[str(path)] = expected_path

                nodes_by_path[path] = config
                nodes_by_name[config['@name']] = config
                nodes_by_type[config_type][path] = config

    # Collect the referenced nodes.
    referenced_nodes = {str(p): list(_iterate_references(c)) for p, c in nodes_by_path.items()}

    print(json_dumps({
        'numConfigTypes': num_config_types,
        'badConfigLocation': bad_config_location,
        #'referencedNodes': referenced_nodes
    }, sort_keys=True, indent=2, separators=(',', ': ')))

if __name__ == '__main__':
    main()
