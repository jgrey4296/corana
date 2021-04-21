##
# Code Analysis
#
# @file
# @version 0.1

# Reminder: make TARGET args="-r 5" etc

abl:
	python code_analysis/specific/abl/abl_extractor.py ${args} ${args}

config:
	python code_analysis/specific/config_files/config_extractor.py ${args}

csharp:
	python code_analysis/specific/csharp/csharp_extractor.py ${args}

csv:
	python code_analysis/specific/csv/csv_extractor.py ${args}

tsv:
	python code_analysis/specific/csv/tsv_extractor.py ${args}

dev:
	python code_analysis/specific/dev_logs/dev_log_extractor.py ${args}

dialogue:
	python code_analysis/specific/dialogue/dialogue_extractor.py ${args}

eula:
	python code_analysis/specific/eulas/eula_extractor.py ${args}

dramatis:
	python code_analysis/specific/fiction/dramatis_extractor.py ${args}

narrative:
	python code_analysis/specific/fiction/narrative_extractor.py ${args}

game:
	python code_analysis/specific/game_config_text/game_script_extractor.py ${args}

index:
	python code_analysis/specific/indexes/index_extractor.py ${args}

json:
	python code_analysis/specific/json/json_extractor.py ${args}

lua:
	python code_analysis/specific/lua/lua_extractor.py ${args}

names:
	python code_analysis/specific/names/name_extractor.py ${args}

deontic:
	python code_analysis/specific/natural_language_deontics/deontic_extractor.py ${args}

patch:
	python code_analysis/specific/patch_notes/patch_notes_extractor.py ${args}

sql:
	python code_analysis/specific/sql/sql_extractor.py ${args}

versu:
	python code_analysis/specific/versu/versu_extractor.py ${args}

xmlrule:
	python code_analysis/specific/xml/xml_rule_extractor.py ${args}

xmltext:
	python code_analysis/specific/xml/xml_text_extractor.py ${args}

nyt:
	python code_analysis/specific/nyt/nyt_extractor.py ${args}

# end
