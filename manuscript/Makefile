# Builds through makedoc (https://github.com/BWBrook/makedoc). uv supplies a python3 with PyYAML,
# leaving system Python untouched. Run from the repository root as `make -C manuscript [target]`.
MAKEDOC ?= $(HOME)/work/makedoc
CONFIG := $(CURDIR)/settings/build.yaml
PROFILES := main supplement brief
RUN := uv run --no-project --with pyyaml
TEXT := text/main.md text/figures.md text/supplement.md text/supplement_figures.md text/brief.md text/brief_figures.md

.PHONY: all check check-makedoc check-render $(PROFILES)

all: $(PROFILES) check-render

$(PROFILES): check-makedoc
	$(RUN) $(MAKE) -C "$(MAKEDOC)" CONFIG="$(CONFIG)" PROFILE=$@ all

check-makedoc:
	@test "$$(git -C "$(MAKEDOC)" rev-parse HEAD)" = "$$(python3 -c 'import json; print(json.load(open("makedoc.lock.json"))["commit"])')" || { echo "makedoc revision differs from makedoc.lock.json; update the lock deliberately"; exit 1; }
	@git -C "$(MAKEDOC)" diff --quiet HEAD -- || { echo "makedoc has tracked modifications"; exit 1; }

check: check-makedoc
	python3 ../tools/claims.py check claims.csv text/main.md text/supplement.md text/brief.md text/for-agents.md
	python3 ../tools/check_render.py $(TEXT)
	$(foreach p,$(PROFILES),$(RUN) $(MAKE) -C "$(MAKEDOC)" CONFIG="$(CONFIG)" PROFILE=$(p) lint-manuscript refs-audit &&) true

check-render:
	python3 ../tools/check_render.py $(TEXT) --brief build/brief.pdf
