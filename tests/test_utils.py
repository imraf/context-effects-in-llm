import pytest
import requests
from unittest.mock import patch, mock_open, MagicMock
from utils import (
    embed_fact,
    insert_secret_message,
    count_tokens,
    generate_filler_text,
    load_english_articles,
    load_hebrew_articles,
    load_text_from_file,
    OllamaClient,
)


class TestUtils:

    def test_embed_fact_start(self):
        context = "word1 word2 word3 word4"
        fact = "NEEDLE"
        result = embed_fact(context, fact, "start")
        assert "NEEDLE" in result
        # Check that it's inserted at the beginning
        # Note: implementation adds newlines
        assert result.strip().startswith("IMPORTANT FACT: NEEDLE")

    def test_embed_fact_middle(self):
        context = "word1 word2 word3 word4"
        fact = "NEEDLE"
        result = embed_fact(context, fact, "middle")
        assert "NEEDLE" in result
        words = result.split()
        # "word1" "word2" should appear before "IMPORTANT"
        assert words.index("IMPORTANT") > 0

    def test_embed_fact_end(self):
        context = "word1 word2 word3 word4"
        fact = "NEEDLE"
        result = embed_fact(context, fact, "end")
        assert "NEEDLE" in result
        assert result.strip().endswith("IMPORTANT FACT: NEEDLE")

    def test_insert_secret_message_control(self):
        text = "base text"
        result = insert_secret_message(text, "control", "secret")
        assert result == text

    def test_insert_secret_message_start(self):
        text = "base text"
        result = insert_secret_message(text, "start", "secret")
        assert result.startswith("secret")

    def test_insert_secret_message_end(self):
        text = "base text"
        result = insert_secret_message(text, "end", "secret")
        assert result.endswith("secret")

    def test_insert_secret_message_middle(self):
        text = "base text longer"
        result = insert_secret_message(text, "middle", "secret")
        assert "secret" in result
        assert not result.startswith("secret")
        assert not result.endswith("secret")

    def test_insert_secret_message_invalid(self):
        text = "base text"
        with pytest.raises(ValueError):
            insert_secret_message(text, "invalid_position", "secret")

    def test_insert_secret_message_types(self):
        with pytest.raises(TypeError):
            insert_secret_message(123, "start", "secret")

    def test_count_tokens(self):
        text = "word1 word2 word3"
        tokens = count_tokens(text)
        assert tokens > 0
        assert tokens == int(len(text.split()) * 1.3)

    def test_count_tokens_empty(self):
        assert count_tokens("") == 0

    def test_generate_filler_text(self):
        source = ["This is a test sentence.", "Another test sentence."]
        generated = generate_filler_text(50, source)
        assert len(generated.split()) > 0

    def test_generate_filler_text_empty(self):
        source = []
        generated = generate_filler_text(10, source)
        assert "Lorem ipsum" in generated

    @patch("os.path.exists")
    @patch("os.listdir")
    @patch("builtins.open", new_callable=mock_open, read_data="content")
    def test_load_english_articles(self, mock_file, mock_listdir, mock_exists):
        mock_exists.return_value = True
        mock_listdir.return_value = ["article1.txt", "article2.txt"]

        articles = load_english_articles()
        assert len(articles) == 2
        assert articles[0] == "content"

    @patch("os.path.exists")
    def test_load_english_articles_not_found(self, mock_exists):
        mock_exists.return_value = False
        articles = load_english_articles()
        assert articles == []

    @patch("os.path.exists")
    @patch("os.listdir")
    @patch("builtins.open", new_callable=mock_open, read_data="content")
    def test_load_hebrew_articles(self, mock_file, mock_listdir, mock_exists):
        mock_exists.return_value = True
        mock_listdir.return_value = ["article1.txt", "article2.txt"]

        articles = load_hebrew_articles()
        assert len(articles) == 2

    @patch("os.path.exists")
    def test_load_hebrew_articles_not_found(self, mock_exists):
        mock_exists.return_value = False
        articles = load_hebrew_articles()
        assert articles == []

    @patch("os.path.exists")
    @patch("builtins.open", new_callable=mock_open, read_data="content")
    def test_load_text_from_file(self, mock_file, mock_exists):
        mock_exists.return_value = True
        content = load_text_from_file("file.txt", 100)
        assert content == "content"

    @patch("os.path.exists")
    def test_load_text_from_file_not_found(self, mock_exists):
        mock_exists.return_value = False
        content = load_text_from_file("file.txt", 100)
        assert content == ""

    @patch("builtins.open", side_effect=Exception("Read Error"))
    @patch("os.path.exists")
    def test_load_text_from_file_error(self, mock_exists, mock_open):
        mock_exists.return_value = True
        content = load_text_from_file("file.txt", 100)
        assert content == ""


class TestOllamaClient:

    @patch("requests.post")
    @patch("utils.OllamaClient._get_from_cache")
    def test_generate_cache_hit(self, mock_get_cache, mock_post):
        mock_get_cache.return_value = {"response": "cached response"}

        client = OllamaClient("test-model")
        resp = client.generate("prompt")

        assert resp == "cached response"
        mock_post.assert_not_called()

    @patch("requests.post")
    @patch("utils.OllamaClient._get_from_cache")
    @patch("utils.OllamaClient._save_to_cache")
    def test_generate_cache_miss_and_save(self, mock_save_cache, mock_get_cache, mock_post):
        mock_get_cache.return_value = None
        mock_resp = MagicMock()
        mock_resp.json.return_value = {"response": "api response"}
        mock_post.return_value = mock_resp

        client = OllamaClient("test-model")
        resp = client.generate("prompt")

        assert resp == "api response"
        mock_post.assert_called()
        mock_save_cache.assert_called()

    @patch("requests.post")
    @patch("utils.OllamaClient._get_from_cache")
    @patch("utils.OllamaClient._save_to_cache")
    def test_generate_success(self, mock_save_cache, mock_get_cache, mock_post):
        mock_get_cache.return_value = None
        mock_resp = MagicMock()
        mock_resp.json.return_value = {"response": "test response"}
        mock_post.return_value = mock_resp

        client = OllamaClient("test-model")
        resp = client.generate("prompt")

        assert resp == "test response"

    @patch("requests.post", side_effect=requests.exceptions.RequestException)
    @patch("utils.OllamaClient._get_from_cache")
    def test_generate_failure(self, mock_get_cache, mock_post):
        mock_get_cache.return_value = None
        client = OllamaClient("test-model")
        resp = client.generate("prompt")
        assert resp == ""

    @patch("requests.post")
    @patch("utils.OllamaClient._get_from_cache")
    @patch("utils.OllamaClient._save_to_cache")
    def test_generate_with_stats_success(self, mock_save_cache, mock_get_cache, mock_post):
        mock_get_cache.return_value = None
        mock_resp = MagicMock()
        mock_resp.json.return_value = {"response": "test", "eval_count": 10}
        mock_post.return_value = mock_resp

        client = OllamaClient("test-model")
        resp = client.generate_with_stats("prompt")

        assert resp["eval_count"] == 10

    @patch("requests.post", side_effect=requests.exceptions.RequestException)
    @patch("utils.OllamaClient._get_from_cache")
    def test_generate_with_stats_failure(self, mock_get_cache, mock_post):
        mock_get_cache.return_value = None
        client = OllamaClient("test-model")
        resp = client.generate_with_stats("prompt")
        assert resp == {}

    @patch("requests.post")
    def test_embed_success(self, mock_post):
        mock_resp = MagicMock()
        mock_resp.json.return_value = {"embedding": [0.1, 0.2]}
        mock_post.return_value = mock_resp

        client = OllamaClient("test-model")
        emb = client.embed("text")

        assert len(emb) == 2

    @patch("requests.post", side_effect=requests.exceptions.RequestException)
    def test_embed_failure(self, mock_post):
        client = OllamaClient("test-model")
        emb = client.embed("text")
        assert emb == []
