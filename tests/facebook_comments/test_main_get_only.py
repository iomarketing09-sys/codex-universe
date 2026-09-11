import json
import os
from unittest.mock import patch
import pytest

from src.facebook_comments.main import CommentProcessor


class MockResponse:
    def __init__(self, data, status=200):
        self.data = data
        self.status = status

    def read(self):
        return json.dumps(self.data).encode()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass


def test_dry_run_get_only_real_success(monkeypatch, capsys):
    # Set up environment variables for the test
    monkeypatch.setenv('META_ACCESS_TOKEN', 'fake_token')
    monkeypatch.setenv('FB_PAGE_ID', '12345')
    monkeypatch.setenv('META_GRAPH_VERSION', 'v26.0')
    # Ensure we are not in pytest mode to trigger the real GET branch
    monkeypatch.delenv('PYTEST_CURRENT_TEST', raising=False)

    # Mock responses
    post_response = {"data": [{"id": "12345_111", "created_time": "2026-09-10T10:00:00+0000"}]}
    comments_response = {
        "data": [
            {
                "id": "12345_111_1",
                "from": {"id": "111", "name": "User1"},
                "message": "Test comment 1",
                "created_time": "2026-09-10T11:00:00+0000"
            }
        ]
    }

    mock_responses = [post_response, comments_response]
    call_count = 0

    def mock_urlopen(url, data=None, timeout=None):
        nonlocal call_count
        # We don't expect any POST (data should be None)
        if data is not None:
            raise Exception(f"POST not allowed: {data}")
        response = mock_responses[call_count]
        call_count += 1
        return MockResponse(response)

    with patch('urllib.request.urlopen', side_effect=mock_urlopen):
        processor = CommentProcessor(dry_run=True, max_comments=5)
        # Mock _load_environment to do nothing because we have set the env vars with monkeypatch
        with patch.object(processor, '_load_environment'):
            result = processor.run()

    # Check that we got two calls
    assert call_count == 2

    # Check that the processor ran successfully (return code 0)
    assert result == 0

    # Check that the output does not contain the token
    captured = capsys.readouterr()
    assert 'fake_token' not in captured.out
    assert 'fake_token' not in captured.err

    # Check that we processed the comment we mocked
    assert 'Test comment 1' in captured.out


def test_dry_run_get_only_missing_token(monkeypatch, capsys):
    # Unset the token, ensure we are not in pytest mode
    monkeypatch.delenv('META_ACCESS_TOKEN', raising=False)
    monkeypatch.setenv('FB_PAGE_ID', '12345')
    monkeypatch.setenv('META_GRAPH_VERSION', 'v26.0')
    monkeypatch.delenv('PYTEST_CURRENT_TEST', raising=False)

    processor = CommentProcessor(dry_run=True, max_comments=5)
    # Mock _load_environment to do nothing because we have unset the token with monkeypatch
    with patch.object(processor, '_load_environment'):
        result = processor.run()

    # Should return error code
    assert result == 1
    captured = capsys.readouterr()
    # Check that we got an error about missing token or failed to fetch posts
    assert ('Error: META_ACCESS_TOKEN environment variable not set.' in captured.out or
            'Error: FB_PAGE_ID environment variable not set.' in captured.out or
            'Error: Failed to fetch posts.' in captured.out)


def test_dry_run_get_only_http_error(monkeypatch, capsys):
    # Set up environment
    monkeypatch.setenv('META_ACCESS_TOKEN', 'fake_token')
    monkeypatch.setenv('FB_PAGE_ID', '12345')
    monkeypatch.setenv('META_GRAPH_VERSION', 'v26.0')
    monkeypatch.delenv('PYTEST_CURRENT_TEST', raising=False)

    # We'll simulate an HTTP error on the first call (posts)
    call_count = 0

    def mock_urlopen(url, data=None, timeout=None):
        nonlocal call_count
        if data is not None:
            raise Exception(f"POST not allowed: {data}")
        if call_count == 0:
            # Simulate an HTTP error by raising an exception
            raise Exception("HTTP Error 404: Not Found")
        call_count += 1
        # For the second call, we never reach here because we return early on error, but just in case
        return MockResponse({})

    with patch('urllib.request.urlopen', side_effect=mock_urlopen):
        processor = CommentProcessor(dry_run=True, max_comments=5)
        # Mock _load_environment to do nothing because we have set the env vars with monkeypatch
        with patch.object(processor, '_load_environment'):
            result = processor.run()

    # Should return error code because the posts request failed
    assert result == 1
    captured = capsys.readouterr()
    # We expect an error message about failed GET request
    assert ('Warning: GET request to' in captured.out or
            'Error: Failed to fetch posts.' in captured.out)


def test_dry_run_get_only_uses_get_method_and_endpoint(monkeypatch):
    # We want to verify that the method is GET and the endpoint is v26.0
    monkeypatch.setenv('META_ACCESS_TOKEN', 'fake_token')
    monkeypatch.setenv('FB_PAGE_ID', '12345')
    monkeypatch.setenv('META_GRAPH_VERSION', 'v26.0')
    monkeypatch.delenv('PYTEST_CURRENT_TEST', raising=False)

    captured_urls = []
    captured_data = []
    call_count = 0

    def mock_urlopen(url, data=None, timeout=None):
        nonlocal call_count
        call_count += 1
        captured_urls.append(url)
        captured_data.append(data)
        # Return a minimal valid response to avoid errors in the processor
        if '/posts' in url:
            return MockResponse({"data": [{"id": "12345_111", "created_time": "2026-09-10T10:00:00+0000"}]})
        elif '/comments' in url:
            return MockResponse({
                "data": [
                    {
                        "id": "12345_111_1",
                        "from": {"id": "111", "name": "User1"},
                        "message": "Test comment 1",
                        "created_time": "2026-09-10T11:00:00+0000"
                    }
                ]
            })
        else:
            return MockResponse({})

    with patch('urllib.request.urlopen', side_effect=mock_urlopen):
        processor = CommentProcessor(dry_run=True, max_comments=5)
        # Mock _load_environment to do nothing because we have set the env vars with monkeypatch
        with patch.object(processor, '_load_environment'):
            processor.run()

    # Check that we have two URLs
    assert len(captured_urls) == 2
    # Check that the first URL is for posts and the second for comments
    assert any('/posts' in url for url in captured_urls)
    assert any('/comments' in url for url in captured_urls)
    # Check that the data is None (meaning GET)
    assert all(d is None for d in captured_data)
    # Check that the token is in the URL (as a query parameter) - this is expected for the API call
    assert any('access_token=fake_token' in url for url in captured_urls)


def test_under_pytest_uses_mock_data(monkeypatch, capsys):
    # When PYTEST_CURRENT_TEST is set, we should use mock data regardless of dry_run
    monkeypatch.setenv('PYTEST_CURRENT_TEST', 'true')
    monkeypatch.setenv('META_ACCESS_TOKEN', 'fake_token')  # should not be used
    monkeypatch.setenv('FB_PAGE_ID', '12345')
    monkeypatch.setenv('META_GRAPH_VERSION', 'v26.0')

    processor = CommentProcessor(dry_run=True, max_comments=5)
    # We do not mock _load_environment here because we are in pytest mode and we want to use mock data.
    # However, to avoid loading the .env file and potentially overriding our monkeypatch, we can mock it to do nothing as well.
    # But note: in pytest mode, we don't use the environment variables for the API call, so it's safe to load the .env file.
    # However, to be consistent and avoid any side effects, we'll mock _load_environment to do nothing.
    with patch.object(processor, '_load_environment'):
        result = processor.run()

    # Should succeed and use mock data
    assert result == 0
    captured = capsys.readouterr()
    # Check that we got the mock comments
    assert '¡Esto es genial! Me encanta el meme.' in captured.out
    assert '¿De qué trata este meme?' in captured.out
