#!/bin/bash
##
##	Format files in this project.  It saves on arguments.
##

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)"

# shellcheck source=init.sh
source "${HERE}/init.sh"
pip -q install beautysh yapf ruamel.yaml

function lsfiles()
{
	cd "${HERE}" && git ls-files -- '[^converage/]*'
}

## Format JSON
lsfiles | grep -iE '.json$' | while read -r; do
	echo -n "Formatting JSON: ${REPLY}..."
	# shellcheck disable=SC2005
	echo "$(python -m json.tool "${REPLY}")" >"${REPLY}" || echo -ne '\tFailed!'
	echo
done

## Format YAML
lsfiles | grep -iE '.ya?ml$' | while read -r; do
	echo -n "Formatting YAML: ${REPLY}..."
	python <<-EOF
		from ruamel.yaml import YAML
		yaml = YAML(typ='rt')
		yaml.top_level_colon_align = True
		yaml.preserve_quotes = True
		doc = yaml.load(open("${REPLY}", 'r').read())
		yaml.dump(doc, open("${REPLY}", 'w'))
	EOF
	# shellcheck disable=SC2181
	[ $? == 0 ] || echo -ne '\tFailed!'
	echo
done

## Format Python
## See: https://github.com/google/yapf
## Disable formatting for sections with:
## # yapf: disable
## FOO = {
##     # ... some very large, complex data literal.
## }
## # yapf: enable
## You can also disable formatting for a single literal like this:
## BAZ = {
##     # ... some very large, complex data literal.
## }  # yapf: disable
lsfiles | grep -iE '.py$' | while read -r; do
	echo -n "Formatting Python: ${REPLY}..."
	yapf --in-place --style="${HERE}/.style.yapf" "${REPLY}" || echo -ne '\tFailed!'
	echo
done

## Format Shell
## See:  https://github.com/bemeurer/beautysh
## Disable formatting for sections with:
## # @formatter:off
## command \
##     --option1 \
##         --option2 \
##             --option3 \
## # @formatter:on
	lsfiles | grep -iE '.(ba)?sh$' | while read -r; do
	echo -n "Formatting Shell: ${REPLY}..."
	beautysh --indent-size=4 --tab --files "${REPLY}" || echo -ne '\tFailed!'
	echo
done

echo
echo "Done"
