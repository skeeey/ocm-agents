SHELL:=/bin/bash

.PHONY: generate-requirements
generate-requirements:
	pip install pigar
	pigar generate

.PHONY: deps
deps:
	pip install -r requirements.txt
