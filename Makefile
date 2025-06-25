# Universal File Converter System
# Usage: make [library] [from_format] [to_format] [input_file] [output_file]
# Example: make imagemagick jpg png input.jpg output.png

SHELL := /bin/bash
CONVERTER_DIR := ./converters
HELP_DIR := ./help
CONFIG_DIR := ./config

# Default output file generation
define generate_output
$(if $(5),$(5),$(basename $(4)).$(3))
endef

# Color definitions for output
RED := \033[0;31m
GREEN := \033[0;32m
YELLOW := \033[0;33m
BLUE := \033[0;34m
NC := \033[0m # No Color

# Help system
.PHONY: help list-libraries list-formats search benchmark validate
help:
	@echo -e "$(BLUE)Universal File Converter System$(NC)"
	@echo "Usage: make [library] [from_format] [to_format] [input_file] [output_file]"
	@echo ""
	@echo "Available commands:"
	@echo "  help              - Show this help"
	@echo "  list-libraries    - List all available libraries"
	@echo "  list-formats      - List supported formats by library"
	@echo "  search            - Search libraries for specific conversion (make search [from] [to])"
	@echo "  benchmark         - Benchmark conversion speed and quality"
	@echo "  validate          - Validate file format and integrity"
	@echo "  batch             - Batch convert multiple files"
	@echo "  preview           - Preview conversion without executing"
	@echo "  check-conflicts   - Check format conversion conflicts"
	@echo ""
	@echo "Interactive conflict resolution:"
	@echo "  ./help.sh [from_format] [to_format]"

list-libraries:
	@echo -e "$(GREEN)Available Conversion Libraries:$(NC)"
	@if [ -d "$(CONVERTER_DIR)" ]; then \
		for lib in $(CONVERTER_DIR)/*.sh; do \
			if [ -f "$$lib" ] && [ "$$(basename "$$lib")" != "_template.sh" ]; then \
				echo "  $$(basename "$$lib" .sh)"; \
			fi; \
		done; \
	else \
		echo -e "$(YELLOW)  No converters found. Run: make install-deps$(NC)"; \
	fi


list-formats:
	@echo -e "$(GREEN)Supported Formats by Library:$(NC)"
	@for lib in $(CONVERTER_DIR)/*.sh; do \
		echo -e "$(YELLOW)$$(basename $$lib .sh):$(NC)"; \
		bash $$lib --list-formats 2>/dev/null || echo "  Format list not available"; \
		echo ""; \
	done

# Format conflict checker
check-conflicts:
	@echo -e "$(YELLOW)Checking for format conversion conflicts...$(NC)"
	@bash $(HELP_DIR)/conflict_checker.sh

# Search for libraries supporting specific conversion
search:
	@echo -e "$(BLUE)Searching for converters that support: $(word 1,$(filter-out $@,$(MAKECMDGOALS))) → $(word 2,$(filter-out $@,$(MAKECMDGOALS)))$(NC)"
	@echo -e "$(YELLOW)Note: This is a basic search. Some converters might support this conversion even if not listed.$(NC)"
	@echo ""
	@if [ -z "$(word 1,$(filter-out $@,$(MAKECMDGOALS)))" ] || [ -z "$(word 2,$(filter-out $@,$(MAKECMDGOALS)))" ]; then \
		echo -e "$(RED)Error: Missing arguments$(NC)"; \
		echo "Usage: make search [from_format] [to_format]"; \
		echo "Example: make search md pdf"; \
		exit 1; \
	fi
	@FOUND=0; \
	for converter in $(CONVERTER_DIR)/*.sh; do \
		if [ -f "$$converter" ]; then \
			converter_name=$$(basename "$$converter" .sh); \
			if bash "$$converter" --list-formats 2>/dev/null | grep -q -i "Input:.*$(word 1,$(filter-out $@,$(MAKECMDGOALS)))" && \
			   bash "$$converter" --list-formats 2>/dev/null | grep -q -i "Output:.*$(word 2,$(filter-out $@,$(MAKECMDGOALS)))"; then \
				FOUND=1; \
				echo -e "$(GREEN)✓ $$converter_name$(NC)"; \
				echo "  Command: make $$converter_name $(word 1,$(filter-out $@,$(MAKECMDGOALS))) $(word 2,$(filter-out $@,$(MAKECMDGOALS))) [input] [output]"; \
				echo ""; \
			fi; \
		fi; \
	done; \
	if [ $$FOUND -eq 0 ]; then \
		echo -e "$(YELLOW)No direct converters found for $(word 1,$(filter-out $@,$(MAKECMDGOALS))) → $(word 2,$(filter-out $@,$(MAKECMDGOALS)))$(NC)"; \
		echo ""; \
		echo -e "$(BLUE)Available converters:$(NC)"; \
		make list-libraries; \
		echo ""; \
		echo -e "$(YELLOW)Try:$(NC)"; \
		echo "• Check formats: make list-formats"; \
		echo "• Try conversion chains: ./help.sh $(word 1,$(filter-out $@,$(MAKECMDGOALS))) $(word 2,$(filter-out $@,$(MAKECMDGOALS)))"; \
	fi

# Benchmark conversion performance
benchmark:
	@if [ -z "$(word 1,$(filter-out $@,$(MAKECMDGOALS)))" ]; then \
		echo -e "$(RED)Usage: make benchmark [test_file] [from_format] [to_format]$(NC)"; \
		echo "Example: make benchmark test.jpg jpg png"; \
		exit 1; \
	fi; \
	TEST_FILE="$(word 1,$(filter-out $@,$(MAKECMDGOALS)))"; \
	FROM_FMT="$(word 2,$(filter-out $@,$(MAKECMDGOALS)))"; \
	TO_FMT="$(word 3,$(filter-out $@,$(MAKECMDGOALS)))"; \
	echo -e "$(BLUE)Benchmarking conversion: $FROM_FMT → $TO_FMT$(NC)"; \
	bash $(HELP_DIR)/benchmark.sh "$TEST_FILE" "$FROM_FMT" "$TO_FMT"

# Validate file format and integrity
validate:
	@if [ -z "$(word 1,$(filter-out $@,$(MAKECMDGOALS)))" ]; then \
		echo -e "$(RED)Usage: make validate [file]$(NC)"; \
		exit 1; \
	fi; \
	FILE="$(word 1,$(filter-out $@,$(MAKECMDGOALS)))"; \
	echo -e "$(BLUE)Validating file: $FILE$(NC)"; \
	bash $(HELP_DIR)/validator.sh "$FILE"

# Batch convert multiple files
batch:
	@if [ -z "$(word 1,$(filter-out $@,$(MAKECMDGOALS)))" ]; then \
		echo -e "$(RED)Usage: make batch [library] [from_format] [to_format] [pattern]$(NC)"; \
		echo "Example: make batch imagemagick jpg png '*.jpg'"; \
		exit 1; \
	fi; \
	LIBRARY="$(word 1,$(filter-out $@,$(MAKECMDGOALS)))"; \
	FROM_FMT="$(word 2,$(filter-out $@,$(MAKECMDGOALS)))"; \
	TO_FMT="$(word 3,$(filter-out $@,$(MAKECMDGOALS)))"; \
	PATTERN="$(word 4,$(filter-out $@,$(MAKECMDGOALS)))"; \
	echo -e "$(BLUE)Batch converting: $PATTERN ($FROM_FMT → $TO_FMT) using $LIBRARY$(NC)"; \
	bash $(HELP_DIR)/batch_processor.sh "$LIBRARY" "$FROM_FMT" "$TO_FMT" "$PATTERN"

# Preview conversion command without executing
preview:
	@if [ -z "$(word 1,$(filter-out $@,$(MAKECMDGOALS)))" ]; then \
		echo -e "$(RED)Usage: make preview [library] [from_format] [to_format] [input] [output]$(NC)"; \
		exit 1; \
	fi; \
	LIBRARY="$(word 1,$(filter-out $@,$(MAKECMDGOALS)))"; \
	FROM_FMT="$(word 2,$(filter-out $@,$(MAKECMDGOALS)))"; \
	TO_FMT="$(word 3,$(filter-out $@,$(MAKECMDGOALS)))"; \
	INPUT="$(word 4,$(filter-out $@,$(MAKECMDGOALS)))"; \
	OUTPUT="$(word 5,$(filter-out $@,$(MAKECMDGOALS)))"; \
	echo -e "$(BLUE)Preview mode - Command that would be executed:$(NC)"; \
	PREVIEW_MODE=1 bash $(CONVERTER_DIR)/$LIBRARY.sh "$FROM_FMT" "$TO_FMT" "$INPUT" "$OUTPUT"

# Image conversion libraries
imagemagick:
	@$(call convert_file,imagemagick,$(filter-out $@,$(MAKECMDGOALS)))

graphicsmagick:
	@$(call convert_file,graphicsmagick,$(filter-out $@,$(MAKECMDGOALS)))

ffmpeg:
	@$(call convert_file,ffmpeg,$(filter-out $@,$(MAKECMDGOALS)))

pillow:
	@$(call convert_file,pillow,$(filter-out $@,$(MAKECMDGOALS)))

opencv:
	@$(call convert_file,opencv,$(filter-out $@,$(MAKECMDGOALS)))

# Document conversion libraries
pandoc:
	@$(call convert_file,pandoc,$(filter-out $@,$(MAKECMDGOALS)))

libreoffice:
	@$(call convert_file,libreoffice,$(filter-out $@,$(MAKECMDGOALS)))

ghostscript:
	@$(call convert_file,ghostscript,$(filter-out $@,$(MAKECMDGOALS)))

poppler:
	@$(call convert_file,poppler,$(filter-out $@,$(MAKECMDGOALS)))

wkhtmltopdf:
	@$(call convert_file,wkhtmltopdf,$(filter-out $@,$(MAKECMDGOALS)))

# Audio/Video conversion
sox:
	@$(call convert_file,sox,$(filter-out $@,$(MAKECMDGOALS)))

# Specialized converters
inkscape:
	@$(call convert_file,inkscape,$(filter-out $@,$(MAKECMDGOALS)))

rsvg:
	@$(call convert_file,rsvg,$(filter-out $@,$(MAKECMDGOALS)))

# Conversion function
define convert_file
	@if [ ! -f "$(CONVERTER_DIR)/$(1).sh" ]; then \
		echo -e "$(RED)Error: Library $(1) not found$(NC)"; \
		exit 1; \
	fi; \
	if [ -z "$(word 1,$(2))" ] || [ -z "$(word 2,$(2))" ] || [ -z "$(word 3,$(2))" ]; then \
		echo -e "$(RED)Error: Missing arguments$(NC)"; \
		echo "Usage: make $(1) [from_format] [to_format] [input_file] [output_file]"; \
		exit 1; \
	fi; \
	FROM_FORMAT="$(word 1,$(2))"; \
	TO_FORMAT="$(word 2,$(2))"; \
	INPUT_FILE="$(word 3,$(2))"; \
	OUTPUT_FILE="$(call generate_output,$(1),$$FROM_FORMAT,$$TO_FORMAT,$$INPUT_FILE,$(word 4,$(2)))"; \
	echo -e "$(GREEN)Converting with $(1):$(NC) $$INPUT_FILE ($$FROM_FORMAT) -> $$OUTPUT_FILE ($$TO_FORMAT)"; \
	bash $(CONVERTER_DIR)/$(1).sh "$$FROM_FORMAT" "$$TO_FORMAT" "$$INPUT_FILE" "$$OUTPUT_FILE"
endef

# Install dependencies
install-deps:
	@echo -e "$(BLUE)Installing converter dependencies...$(NC)"
	@bash $(CONFIG_DIR)/install_dependencies.sh

# Prevent make from interpreting arguments as targets
%:
	@:
