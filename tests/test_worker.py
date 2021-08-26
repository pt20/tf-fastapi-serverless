from unittest.mock import patch

from src.worker import create_task


@patch("src.worker.create_task.run")
def test_mock_task(mock_run):
    assert create_task.run(1)
    create_task.run.assert_called_once_with(1)

    assert create_task.run(10)
    assert create_task.run.call_count == 2

    assert create_task.run(100)
    assert create_task.run.call_count == 3
