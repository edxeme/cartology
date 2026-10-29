# --- build stage ---------------------------------------------------------
FROM python:3.12-slim AS build
WORKDIR /build
COPY pyproject.toml README.md ./
COPY src ./src
RUN pip install --no-cache-dir --prefix=/install .

# --- runtime stage -------------------------------------------------------
FROM python:3.12-slim
LABEL org.opencontainers.image.title="cartology" \
      org.opencontainers.image.description="Static maps of a Python package" \
      org.opencontainers.image.source="https://github.com/edxeme/cartology"

COPY --from=build /install /usr/local

RUN useradd --create-home --shell /usr/sbin/nologin scanner
USER scanner

ENTRYPOINT ["cartology"]
CMD ["--help"]
