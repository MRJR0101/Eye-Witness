from pathlib import Path


def test_framework_example_files_exist():
    assert Path("examples/fastapi_app/main.py").exists()
    assert Path("examples/flask_app/app.py").exists()
    assert Path("examples/django_app/settings_snippet.py").exists()
    assert Path("examples/celery_worker/worker.py").exists()
