import pytest
import os
from unittest.mock import patch
from publicar_substack import processar_arquivo_markdown

@pytest.fixture
def temp_md_file(tmp_path):
    """Cria um arquivo Markdown temporário para os testes."""
    content = """---
title: "Título de Teste"
subtitle: "Subtítulo de Teste"
---
# Conteúdo Principal

Este é o corpo do post.
"""
    file_path = tmp_path / "test_post.md"
    file_path.write_text(content, encoding='utf-8')
    return str(file_path)

@pytest.fixture
def temp_md_file_no_title(tmp_path):
    """Cria um arquivo Markdown temporário sem título no front matter."""
    content = """---
subtitle: "Subtítulo de Teste"
---
# Conteúdo

Corpo do post.
"""
    file_path = tmp_path / "no_title_post.md"
    file_path.write_text(content, encoding='utf-8')
    return str(file_path)

def test_processar_arquivo_markdown_sucesso(temp_md_file):
    """
    Testa se a função processa um arquivo Markdown válido corretamente.
    """
    titulo, subtitulo, html_content = processar_arquivo_markdown(temp_md_file)

    assert titulo == "Título de Teste"
    assert subtitulo == "Subtítulo de Teste"
    assert "<h1>Conteúdo Principal</h1>" in html_content
    assert "<p>Este é o corpo do post.</p>" in html_content

def test_processar_arquivo_sem_titulo(temp_md_file_no_title):
    """
    Testa se a função falha (SystemExit) quando o título está ausente.
    """
    with pytest.raises(SystemExit) as e:
        processar_arquivo_markdown(temp_md_file_no_title)
    assert e.type == SystemExit
    assert e.value.code == 1

def test_processar_arquivo_nao_encontrado():
    """
    Testa se a função falha (SystemExit) quando o arquivo não existe.
    """
    with pytest.raises(SystemExit) as e:
        processar_arquivo_markdown("arquivo_inexistente.md")
    assert e.type == SystemExit
    assert e.value.code == 1

def test_processar_arquivo_sem_subtitulo(tmp_path):
    """
    Testa se a função lida corretamente com a ausência de subtítulo.
    """
    content = """---
title: "Apenas Título"
---
# Conteúdo
"""
    file_path = tmp_path / "no_subtitle_post.md"
    file_path.write_text(content, encoding='utf-8')

    titulo, subtitulo, _ = processar_arquivo_markdown(str(file_path))

    assert titulo == "Apenas Título"
    assert subtitulo == ""  # Deve retornar uma string vazia por padrão