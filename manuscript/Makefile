MAKEDOC ?= $(HOME)/work/makedoc
CONFIG := $(CURDIR)/settings/build.yaml
PROFILES := main supplement brief
RUN := uv run --project "$(CURDIR)" --frozen
MODEL_RUN := uv run --project "$(abspath ..)" --frozen --extra analysis --extra plot
CACHE := $(CURDIR)/.cache
export UV_CACHE_DIR ?= $(CACHE)/uv
MAKEDOC_ARGS := CONFIG="$(CONFIG)" PROFILE_CACHE_DIR="$(CACHE)/makedoc" PDF_ENGINE_OUTPUT_DIR="$(CACHE)/latex"
TEXT := text/main.md text/figures.md text/supplement.md text/brief.md text/brief_figures.md

.PHONY: all figures check check-figures check-makedoc check-render $(PROFILES)

all: check-render

# The pinned makedoc revision does not track figure images as make prerequisites.
$(PROFILES): check
	$(RUN) $(MAKE) --always-make -C "$(MAKEDOC)" $(MAKEDOC_ARGS) PROFILE=$@ all

figures:
	$(MODEL_RUN) python "$(CURDIR)/figures.py" --generate

check-figures:
	python3 figures.py --check
	python3 tables.py --check

check-makedoc:
	@test "$$(git -C "$(MAKEDOC)" rev-parse HEAD)" = "$$(python3 -c 'import json; print(json.load(open("makedoc.lock.json"))["commit"])')" || { echo "makedoc revision differs from makedoc.lock.json; update the lock deliberately"; exit 1; }
	@git -C "$(MAKEDOC)" diff --quiet HEAD -- || { echo "makedoc has tracked modifications"; exit 1; }

check: check-makedoc check-figures
	python3 ../tools/claims.py check claims.csv $(TEXT) text/for-agents.md
	python3 ../tools/check_render.py $(TEXT)
	$(foreach p,$(PROFILES),$(RUN) $(MAKE) -C "$(MAKEDOC)" $(MAKEDOC_ARGS) PROFILE=$(p) lint-manuscript refs-audit &&) true

check-render: $(PROFILES)
	python3 ../tools/check_render.py $(TEXT) --brief build/brief.pdf
