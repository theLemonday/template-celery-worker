# ==========================================
# Stage 1: The Builder (Two-Stage Install)
# ==========================================
FROM ghcr.io/astral-sh/uv:python3.11-bookworm-slim AS builder

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY pyproject.toml uv.lock ./
RUN uv export --frozen --no-dev --no-emit-project --format=requirements-txt >requirements.txt

# 3. Install dependencies
# We install these into /app/site-packages.
# Docker will CACHE this layer as long as uv.lock doesn't change.
RUN uv pip install \
    --target /app/site-packages \
    -r requirements.txt

# --- STATION B: Custom Finish (Frequent Changes) ---
# 4. Copy the actual source code
# This layer invalidates frequently, but that's okay because the heavy lift is done.
COPY . .

RUN uv build

# 5. Install the project itself
# --no-deps: Critical! We tell pip "Trust us, dependencies are already there."
# This prevents it from re-checking the internet or the previous layer.
# This takes the code from 'src/', packages it, and installs it to site-packages
RUN uv pip install \
    --system \
    --no-deps \
    --target /app/site-packages \
    dist/*.whl

# ==========================================
# Stage 2: The Runner (Distroless)
# ==========================================
FROM gcr.io/distroless/python3-debian12 AS prod

WORKDIR /app

# 1. Copy the combined "site-packages" (Dependencies + Your App)
COPY --from=builder /app/site-packages /app/site-packages

# 2. Configure PYTHONPATH
ENV PYTHONPATH="/app/site-packages"

USER nonroot:nonroot

# 3. Entrypoint
CMD ["-m", "celery", "-A", "celery_worker.main.app", "worker", "--loglevel=info"]
