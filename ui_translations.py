"""Compatibility module; editable translations are in locales/*.json."""
from language_catalog import CATALOGUES
TEXT={source:tuple(CATALOGUES.translate(source,code) for code in ('de','hu')) for source in CATALOGUES.by_source}
