import os
import sys
import argparse
from markdown import markdown
from substack import Api
from substack.post import Post

# 1. Configuração de Variáveis de Ambiente
# DICA: Guarde credenciais como variáveis de ambiente, Docker Secrets ou Azure Key Vault,
# em vez de codificá-las diretamente.
EMAIL = os.getenv("SUBSTACK_EMAIL")
SENHA = os.getenv("SUBSTACK_SENHA")
URL_PUBLICACAO = os.getenv("SUBSTACK_URL")

# --- Não Edite Abaixo Desta Linha ---

def converter_markdown_para_html(caminho_arquivo: str) -> str:
    """Lê um arquivo .md e retorna o conteúdo em HTML."""
    try:
        with open(caminho_arquivo, 'r', encoding='utf-8') as f:
            markdown_content = f.read()
        return markdown(markdown_content)
    except FileNotFoundError:
        print(f"Erro: Arquivo Markdown não encontrado em '{caminho_arquivo}'")
        sys.exit(1)

def publicar_post_substack(titulo: str, subtitulo: str, html_content: str):
    """
    Autentica no Substack e publica um novo post.
    Nota: Esta biblioteca utiliza a API interna/não-oficial do Substack.
    """
    if not EMAIL or not SENHA or not URL_PUBLICACAO:
        print("Erro: Variáveis de ambiente SUBSTACK_EMAIL, SUBSTACK_SENHA e SUBSTACK_URL devem ser configuradas.")
        sys.exit(1)

    try:
        print("1. Tentando autenticar no Substack...")
        api = Api(email=EMAIL, password=SENHA)

        # 2. Configura a publicação
        api.change_publication_url(URL_PUBLICACAO)
        user_id = api.get_user_id()

        # 3. Cria o Objeto Post e Adiciona o HTML
        # O Substack usa um formato JSON estruturado, então a forma mais simples
        # de inserir conteúdo externo é através de HTML.
        post = Post(
            title=titulo,
            subtitle=subtitulo,
            user_id=user_id
        )

        # Adiciona o conteúdo HTML ao corpo do post
        post.add_html(html_content)

        # 4. Envia o rascunho para o Substack
        print("2. Enviando rascunho...")
        draft_response = api.post_draft(post.get_draft())
        draft_id = draft_response.get("id")

        # 5. Publica o rascunho
        print("3. Publicando o rascunho...")
        publicacao_response = api.publish_post(draft_id)

        print("\n--- SUCESSO ---")
        print(f"Post publicado! ID: {draft_id}")
        print(f"URL de visualização (pode ser o link do rascunho, dependendo da biblioteca): {publicacao_response.get('canonical_url')}")

    except Exception as e:
        print(f"\n--- ERRO NA PUBLICAÇÃO ---")
        print(f"Ocorreu um erro (a API não-oficial pode ter mudado ou a autenticação falhou): {e}")

def main():
    """Função principal para executar o script."""
    parser = argparse.ArgumentParser(description="Publica um arquivo Markdown no Substack.")
    parser.add_argument(
        "caminho_md",
        help="O caminho para o arquivo .md a ser publicado."
    )
    parser.add_argument(
        "--titulo",
        required=True,
        help="O título do post."
    )
    parser.add_argument(
        "--subtitulo",
        default="",
        help="O subtítulo do post (opcional)."
    )

    args = parser.parse_args()

    print(f"Processando arquivo: {args.caminho_md}")

    # 1. Converte .md para HTML
    conteudo_html = converter_markdown_para_html(args.caminho_md)

    # 2. Publica no Substack
    publicar_post_substack(args.titulo, args.subtitulo, conteudo_html)

if __name__ == "__main__":
    main()