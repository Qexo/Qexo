# Target section and Global definitions
# -----------------------------------------------------------------------------
.PHONY: deploy

all: deploy


deploy: generate_dot_env
	bash ./update_tag.sh
	docker-compose build
	docker-compose up -d

down: 
	docker-compose down

generate_dot_env:
	@if [[ ! -e .env ]]; then \
		cp .env.example .env; \
	fi