# OpenStock Makefile

IMAGE_PREFIX ?= zhongcheng0519/openstock
PLATFORM     ?= linux/amd64

BACKEND_VERSION  := $(shell awk -F'"' '/^version/ {print $$2}' backend/pyproject.toml)
FRONTEND_VERSION := $(shell node -p "require('./frontend/package.json').version")

.PHONY: help build build-backend build-frontend

help:
	@echo "OpenStock - Build Commands"
	@echo ""
	@echo "  make build-backend   Build & push backend  ($(IMAGE_PREFIX)-backend:$(BACKEND_VERSION))"
	@echo "  make build-frontend  Build & push frontend ($(IMAGE_PREFIX)-frontend:$(FRONTEND_VERSION))"
	@echo "  make build           Build & push all images"
	@echo ""
	@echo "Usage:"
	@echo "  IMAGE_PREFIX=yourname/openstock  make build"

build: build-backend build-frontend

build-backend:
	docker buildx build --platform $(PLATFORM) \
		-t $(IMAGE_PREFIX)-backend:$(BACKEND_VERSION) \
		-t $(IMAGE_PREFIX)-backend:latest \
		--push \
		backend/

build-frontend:
	docker buildx build --platform $(PLATFORM) \
		-t $(IMAGE_PREFIX)-frontend:$(FRONTEND_VERSION) \
		-t $(IMAGE_PREFIX)-frontend:latest \
		--push \
		frontend/
