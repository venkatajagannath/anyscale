Tool to autogenerate documentation for the Anyscale SDK/CLI that can be embedded in a [Docusarus](https://docusaurus.io/) site.

This is used by: https://github.com/anyscale/endpoint-docs.

Usage:
```bash
Usage: python -m anyscale._private.docgen [OPTIONS] OUTPUT_DIR

  Generate markdown docs for the Anyscale CLI & SDK.

Options:
  -r, --remove-existing  If set, all files in the 'output_dir' that were not
                         generated will be removed.
  --help                 Show this message and exit.
```
