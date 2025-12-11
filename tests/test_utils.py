import pytest
import os
from unittest.mock import patch, mock_open
from utils import (
    embed_fact,
    insert_secret_message,
    count_tokens,
    generate_filler_text,
    load_english_articles,
    load_hebrew_articles,
)
import config


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

    def test_insert_secret_message_invalid(self):
        text = "base text"
        with pytest.raises(ValueError):
            insert_secret_message(text, "invalid_position", "secret")

    def test_count_tokens(self):
        text = "word1 word2 word3"
        tokens = count_tokens(text)
        assert tokens > 0
        assert tokens == int(len(text.split()) * 1.3)

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
