ARG PYTHON_VERSION=3.12
FROM python:${PYTHON_VERSION}-slim

WORKDIR /workspace
COPY . /workspace

RUN python -m pip install --upgrade pip build
RUN python -m build --wheel
RUN python -m pip install --no-cache-dir -r requirements.lock.txt
RUN python -m pip install --no-cache-dir dist/*.whl

CMD ["bash", "-lc", "python -m ruff check src tests examples scripts && python -m mypy src && python -m pytest -q"]
