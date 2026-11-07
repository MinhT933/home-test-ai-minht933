from app.markdown_converter import convert_html_to_markdown


def test_preserves_content_and_converts_relative_urls():
    html = """
    <h1>Guide</h1><h2>Setup</h2><p>Héllo <a href="../help">help</a>.</p>
    <ul><li>First</li></ul><img src="/images/example.png" alt="Example">
    <pre><code>print("ok")</code></pre><script>bad()</script><nav>Menu</nav>
    """
    result = convert_html_to_markdown(
        html, article_url="https://example.com/articles/guide", title="Guide"
    )

    assert result.count("# Guide") == 0
    assert "## Setup" in result
    assert "Héllo [help](https://example.com/help)" in result
    assert "* First" in result
    assert "![Example](https://example.com/images/example.png)" in result
    assert 'print("ok")' in result
    assert "bad()" not in result
    assert "Menu" not in result


def test_does_not_remove_a_legitimate_nonmatching_heading():
    result = convert_html_to_markdown("<h1>Details</h1><p>Text</p>", title="Guide")
    assert "# Details" in result


def test_removes_duplicate_title_inside_wrappers_and_keeps_footer_content():
    html = """
    <article><div class="article-body"><header><h1>Guide</h1></header>
    <p>Body</p><footer><p>Important article note</p></footer></div></article>
    """
    result = convert_html_to_markdown(html, title="Guide")

    assert "# Guide" not in result
    assert "Body" in result
    assert "Important article note" in result
