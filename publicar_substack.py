import os
import sys
import argparse
import frontmatter
from markdown import markdown
from substack import Api
from substack.post import Post
from dotenv import load_dotenv

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

# 1. Configuração de Variáveis de Ambiente
EMAIL = os.getenv("SUBSTACK_EMAIL")
SENHA = os.getenv("SUBSTACK_SENHA")
URL_PUBLICACAO = os.getenv("SUBSTACK_URL")

# --- Funções Auxiliares ---

def processar_arquivo_markdown(caminho_arquivo: str) -> tuple[str, str, str]:
    """
    Lê um arquivo .md, extrai metadados (título, subtítulo) do front matter
    e converte o conteúdo para HTML.
    """
    try:
        post = frontmatter.load(caminho_arquivo)
    except FileNotFoundError:
        print(f"Erro: Arquivo Markdown não encontrado em '{caminho_arquivo}'")
        sys.exit(1)
    except Exception as e:
        print(f"Erro ao processar o arquivo Markdown: {e}")
        sys.exit(1)

    titulo = post.metadata.get('title')
    subtitulo = post.metadata.get('subtitle', '')

    if not titulo:
        print(f"Erro: O 'title' não foi encontrado no front matter do arquivo '{caminho_arquivo}'.")
        sys.exit(1)

    html_content = markdown(post.content)
    return titulo, subtitulo, html_content

def publicar_post_substack(titulo: str, subtitulo: str, html_content: str):
    """
    Autentica no Substack e publica um novo post.
    """
    if not EMAIL or not SENHA or not URL_PUBLICACAO:
        print("Erro: Variáveis de ambiente SUBSTACK_EMAIL, SUBSTACK_SENHA e SUBSTACK_URL devem ser configuradas.")
        print("Verifique se você criou um arquivo .env a partir do .env.sample e preencheu suas credenciais.")
        sys.exit(1)

    try:
        print("1. Tentando autenticar no Substack...")
        api = Api(email=EMAIL, password=SENHA)

        api.change_publication_url(URL_PUBLICACAO)
        user_id = api.get_user_id()

        post_obj = Post(
            title=titulo,
            subtitle=subtitulo,
            user_id=user_id
        )
        post_obj.add_html(html_content)

        print("2. Enviando rascunho...")
        draft_response = api.post_draft(post_obj.get_draft())
        draft_id = draft_response.get("id")

        print("3. Publicando o rascunho...")
        publicacao_response = api.publish_post(draft_id)

        print("\n--- SUCESSO ---")
        print(f"Post publicado! ID: {draft_id}")
        print(f"URL de visualização: {publicacao_response.get('canonical_url')}")

    except Exception as e:
        print(f"\n--- ERRO NA PUBLICAÇÃO ---")
        print(f"Ocorreu um erro (a API não-oficial pode ter mudado ou a autenticação falhou): {e}")
        sys.exit(1)

def main():
    """Função principal para executar o script."""
    parser = argparse.ArgumentParser(
        description="Publica um arquivo Markdown com front matter no Substack.",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument(
        "caminho_md",
        help="O caminho para o arquivo .md a ser publicado."
    )

    args = parser.parse_args()

    print(f"Processando arquivo: {args.caminho_md}")

    titulo, subtitulo, conteudo_html = processar_arquivo_markdown(args.caminho_md)

    print(f"Título encontrado: '{titulo}'")
    print(f"Subtítulo encontrado: '{subtitulo}'")

    publicar_post_substack(titulo, subtitulo, conteudo_html)

if __name__ == "__main__":
    main()