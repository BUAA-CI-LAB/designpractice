#!/usr/bin/env python3
"""Check local TeX structure and build warnings; --baseline also checks migration fidelity.

This optional audit uses only the Python standard library. PDF builds do not use it.
"""
import argparse
import collections
import hashlib
import json
from pathlib import Path
import re
import sys


def digest(data):
    return hashlib.sha256(data).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--baseline', action='store_true', help='Check original code and asset hashes from the migration manifest.')
    parser.add_argument('--require-build', action='store_true', help='Require a compiled PDF and log.')
    parser.add_argument('--output', type=Path, help='Write the JSON result to this path.')
    args = parser.parse_args()
    root = Path(__file__).resolve().parent.parent
    errors = []
    manifest = json.loads((root / 'migration/content-manifest.json').read_text(encoding='utf-8'))
    main_tex = (root / 'main.tex').read_text(encoding='utf-8')
    chapter_paths = re.findall(r'\\input\{(chapters/[^}]+)\}', main_tex)
    stats = collections.Counter()
    labels = []
    refs = []
    graphics = []
    code_hashes_verified = 0
    for stem in chapter_paths:
        path = root / (stem + '.tex')
        if not path.is_file():
            errors.append(f'Missing chapter: {path.relative_to(root)}')
            continue
        text = path.read_text(encoding='utf-8')
        code = re.findall(r'\\begin\{CodeBlock\}\n(.*?)\n\\end\{CodeBlock\}', text, re.S)
        prose = re.sub(r'\\begin\{CodeBlock\}\n.*?\n\\end\{CodeBlock\}', '', text, flags=re.S)
        headings = len(re.findall(r'^\\(?:chapter\*?|section\*?|subsection\*?|subsubsection\*?|paragraph\*?|subparagraph\*?)\{', prose, re.M))
        figures = len(re.findall(r'\\begin\{figure\}', prose))
        tables = len(re.findall(r'\\begin\{longtable\}', prose))
        stats.update({'chapters': 1, 'headings': headings, 'code_blocks': len(code), 'figures': figures, 'tables': tables})
        labels.extend(re.findall(r'\\label\{([^}]+)\}', prose))
        refs.extend(re.findall(r'\\(?:ref|eqref|pageref)\{([^}]+)\}', prose))
        graphics.extend(re.findall(r'\\includegraphics(?:\[[^\]]*\])?\{([^}]+)\}', prose))
        if re.search(r'\\@ref|@\\ref|@ref\\?\{|<br\s*/?>|\\(?:NormalTok|KeywordTok|Highlighting)|knitr::', prose):
            errors.append(f'Unconverted markup: {path.name}')
        if re.search(r'^(?:\d+\. |[-*] )', prose, re.M):
            errors.append(f'Unconverted list: {path.name}')
        if args.baseline:
            baseline = next((c for c in manifest['chapters'] if c['target'] == stem + '.tex'), None)
            if baseline is None:
                errors.append(f'Chapter outside migration baseline: {path.name}')
                continue
            for extra in manifest['additional_code_blocks']:
                if extra['file'] == stem + '.tex':
                    if extra['code'] not in code:
                        errors.append(f'Missing repaired command: {extra["code"]}')
                    else:
                        code.remove(extra['code'])
            expected = [c['sha256'] for c in baseline['source_code_blocks']]
            actual = [digest(c.encode('utf-8')) for c in code]
            if actual != expected:
                errors.append(f'Original code changed or reordered: {path.name}')
            else:
                code_hashes_verified += len(actual)
            for key, value in [('headings', headings), ('figures', figures), ('tables', tables)]:
                if value != baseline[key]:
                    errors.append(f'{path.name}: {key} count changed ({value} != {baseline[key]})')

    duplicates = [label for label, count in collections.Counter(labels).items() if count > 1]
    if duplicates:
        errors.append('Duplicate labels: ' + ', '.join(duplicates))
    missing_refs = sorted(set(refs) - set(labels))
    if missing_refs:
        errors.append('Unresolved references: ' + ', '.join(missing_refs))
    for graphic in graphics:
        path = (root / graphic).resolve()
        if root not in path.parents or not path.is_file():
            errors.append('Missing or external graphic: ' + graphic)
    symlinks = [str(p.relative_to(root)) for p in root.rglob('*') if p.is_symlink()]
    if symlinks:
        errors.append('Project contains symlinks: ' + ', '.join(symlinks))
    if args.baseline:
        if chapter_paths != [c['target'][:-4] for c in manifest['chapters']]:
            errors.append('Chapter order differs from the migration baseline.')
        for name, expected in manifest['assets'].items():
            path = root / name
            if not path.is_file() or digest(path.read_bytes()) != expected:
                errors.append('Original asset changed or missing: ' + name)
        summary = manifest['summary']
        for key, expected in [('chapters', 22), ('headings', 346), ('code_blocks', summary['migrated_code_blocks']), ('tables', 21), ('figures', 38)]:
            if stats[key] != expected:
                errors.append(f'{key}: {stats[key]} != {expected}')
        reference_text = (root / 'chapters/30-references.tex').read_text(encoding='utf-8')
        if len(re.findall(r'^\{\[\}\d+\{\]\}', reference_text, re.M)) != 20:
            errors.append('Expected 20 manual bibliography entries.')

    log_path = root / 'build/main.log'
    log_stats = {}
    if log_path.exists():
        log = log_path.read_text(encoding='utf-8', errors='replace')
        log_stats = {
            'missing_characters': log.count('Missing character:'),
            'overfull_boxes': len(re.findall(r'Overfull \\[hv]box', log)),
            'undefined_references': len(re.findall(r'LaTeX Warning: Reference .*?undefined', log)),
            'latex_errors': len(re.findall(r'^!|LaTeX Error:|Package .*? Error:', log, re.M)),
            'font_warnings': log.count('LaTeX Font Warning:'),
        }
        for key, count in log_stats.items():
            if count:
                errors.append(f'Build log: {key} = {count}')
        if not (root / 'build/main.pdf').is_file():
            errors.append('Build log exists without build/main.pdf.')
    elif args.require_build:
        errors.append('Build the book before running --require-build.')
    recorder = root / 'build/main.fls'
    project_inputs = set()
    if recorder.is_file():
        old_root = Path(manifest['source_directory'])
        for line in recorder.read_text(encoding='utf-8', errors='replace').splitlines():
            if not line.startswith('INPUT '):
                continue
            path = Path(line[6:].strip('"'))
            path = (root / path).resolve() if not path.is_absolute() else path.resolve()
            if old_root in path.parents:
                errors.append('Build still reads the original project: ' + str(path))
            if root in path.parents:
                project_inputs.add(str(path.relative_to(root)))
    report = {
        'project': str(root), 'baseline_checked': args.baseline,
        'counts': dict(stats), 'labels': len(labels), 'references': len(refs),
        'original_code_blocks_hash_verified': code_hashes_verified,
        'original_assets_hash_verified': len(manifest['assets']) if args.baseline else None,
        'recorded_local_inputs': sorted(project_inputs),
        'log': log_stats, 'errors': errors, 'passed': not errors,
    }
    output = json.dumps(report, ensure_ascii=False, indent=2)
    print(output)
    if args.output:
        args.output.write_text(output + '\n', encoding='utf-8')
    return int(bool(errors))


if __name__ == '__main__':
    sys.exit(main())
