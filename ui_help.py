"""Help message mappings come from the English catalogue; UI translation is applied later."""
from collections import defaultdict
from language_catalog import CATALOGUES
FIELDS=defaultdict(str,CATALOGUES.help_text('fields'))
TIPS=defaultdict(str,CATALOGUES.help_text('tips'))
BUTTONS={label:(text,) for label,text in CATALOGUES.help_text('buttons').items()}
