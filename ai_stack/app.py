import json
import os

import streamlit as st
from agent_pipeline import gerar_material_educacional
from dotenv import load_dotenv

# Importa as funções dos módulos que criamos nas etapas anteriores
from rag_pipeline import buscar_contexto, criar_base_vetorial
from streamlit_google_auth import Authenticate

# Carrega variáveis de ambiente (.env)
load_dotenv()

# Configuração da página do Streamlit
st.set_page_config(
    page_title="Gerador Inteligente de Conteúdo Técnico", page_icon="🎓", layout="wide"
)

# ==========================================
# CONFIGURAÇÃO DE AUTENTICAÇÃO GOOGLE
# ==========================================
authenticator = Authenticate(
    secret_credentials_path={
        "client_id": os.getenv("GOOGLE_CLIENT_ID"),
        "client_secret": os.getenv("GOOGLE_CLIENT_SECRET"),
        "redirect_uri": "http://localhost:8501",
    },
    cookie_name="rag_app_google_cookie",
    cookie_key="chave_secreta_super_segura_para_cookies",
    redirect_uri="http://localhost:8501",
    scope=["openid", "email", "profile"],
)

# Verifica se o usuário está logado
authenticator.check_authentication()

# Se não estiver autenticado, exibe o botão de login
if not st.session_state.get("connected", False):
    st.title("🎓 Login - Gerador Inteligente de Conteúdo")
    st.markdown("Faça login com sua conta Google para acessar a plataforma RAG.")

    # Exibe o botão de login do Google
    authenticator.login()
    st.stop()  # Interrompe a execução do restante da página até que o login seja feito

# ==========================================
# APLICAÇÃO PRINCIPAL (PROTEGIDA POR LOGIN)
# ==========================================
user_info = st.session_state.get("user_info", {})
user_email = user_info.get("email", "Usuário")
user_name = user_info.get("name", "Convidado")

# Barra lateral com dados do usuário logado
with st.sidebar:
    st.write(f"👤 Logado como: **{user_name}**")
    st.write(f"📧 `{user_email}`")

    # Botão de Logout nativo do componente
    authenticator.logout("Sair", "sidebar")
    st.divider()

    st.header("⚙️ Configurações & Parâmetros")

    # 1. Upload do Documento
    st.subheader("1. Documento de Entrada")
    arquivo_upload = st.file_uploader(
        "Envie o material técnico",
        type=["pdf", "md", "txt"],
        help="Suporta arquivos PDF, Markdown ou texto bruto.",
    )

    st.divider()

    # 2. Parâmetros de Personalização
    st.subheader("2. Critérios Pedagógicos")

    perfil = st.selectbox(
        "Perfil do Destinatário",
        [
            "Iniciante / Transição de Carreira",
            "Desenvolvedor Júnior / Pleno",
            "Líder Técnico / Arquiteto",
            "Gestor / Executivo (Não Técnico)",
        ],
    )

    formato = st.selectbox(
        "Formato Pedagógico de Saída",
        [
            "Guia Prático Passo a Passo (Tutorial)",
            "Quiz Interativo com Justificativas",
            "Flashcards de Memorização",
            "Resumo Executivo (TL;DR)",
            "Roteiro de Aula / Vídeo",
        ],
    )

    nicho = st.selectbox(
        "Nicho / Contexto de Aplicação", ["Geral", "Fintech", "Saúde", "E-commerce"]
    )

    st.divider()
    botao_gerar = st.button(
        "🚀 Gerar Conteúdo Educacional", type="primary", use_container_width=True
    )

# Título principal da aplicação
st.title("🎓 Gerador Inteligente de Conteúdo Educacional (RAG + Agentes)")
st.markdown("""
Transforme documentações técnicas densas, manuais ou artigos em **tutoriais, quizzes, flashcards ou resumos** 
personalizados para diferentes perfis e indústrias, com validação anti-alucinação.
""")

if botao_gerar:
    if not arquivo_upload:
        st.warning(
            "⚠️ Por favor, faça o upload de um documento técnico na barra lateral antes de gerar."
        )
    else:
        temp_dir = "./temp_data"
        os.makedirs(temp_dir, exist_ok=True)
        caminho_temp = os.path.join(temp_dir, arquivo_upload.name)

        with open(caminho_temp, "wb") as f:
            f.write(arquivo_upload.getbuffer())

        try:
            with st.status(
                "🔄 Processando pipeline inteligente...", expanded=True
            ) as status:
                st.write("📄 Lendo documento e criando chunks...")
                db_vetorial = criar_base_vetorial(
                    caminho_temp, persist_directory="./chroma_temp_db"
                )

                st.write("🔍 Realizando busca semântica (Retrieval)...")
                query_busca = f"Conceitos principais, regras, códigos e instruções sobre {arquivo_upload.name}"
                docs_encontrados = buscar_contexto(db_vetorial, query_busca, k=4)

                contexto_consolidado = "\n\n".join(
                    [doc.page_content for doc in docs_encontrados]
                )

                st.write(
                    "🤖 Executando Agente Redator e Agente Revisor (Anti-Alucinação)..."
                )
                resultado_json = gerar_material_educacional(
                    contexto_rag=contexto_consolidado,
                    perfil=perfil,
                    formato=formato,
                    nicho=nicho,
                )

                status.update(
                    label="✅ Conteúdo gerado e validado com sucesso!",
                    state="complete",
                    expanded=False,
                )

            if os.path.exists(caminho_temp):
                os.remove(caminho_temp)

            st.success("✨ Material Pedagógico Pronto!")

            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric(
                    "Tempo Estimado",
                    f"{resultado_json.get('tempo_estimado_minutos', 10)} min",
                )
            with col2:
                st.metric(
                    "Score de Fidelidade",
                    f"{resultado_json.get('score_fidelidade', 10)} / 10",
                )
            with col3:
                st.metric("Formato", formato.split("(")[0].strip())
            with col4:
                st.metric("Perfil", perfil.split("/")[0].strip())

            st.divider()

            st.subheader(f"📌 {resultado_json.get('titulo')}")

            with st.expander("🔍 Ver Conceitos-Chave e Pré-requisitos"):
                st.markdown("**Pré-requisitos:**")
                for pre in resultado_json.get("pre_requisitos", []):
                    st.markdown(f"- {pre}")

                st.markdown("**Conceitos-Chave:**")
                st.write(", ".join(resultado_json.get("conceitos_chave", [])))

                st.markdown(
                    f"**Notas de Revisão:** _{resultado_json.get('observacoes_revisao')}_"
                )

            st.markdown("### 📖 Conteúdo Adaptado")
            st.markdown(resultado_json.get("conteudo_estruturado"))

            st.divider()

            json_string = json.dumps(resultado_json, indent=2, ensure_ascii=False)
            st.download_button(
                label="📥 Baixar Pacote de Conteúdo (JSON)",
                data=json_string,
                file_name=f"conteudo_{formato.lower().replace(' ', '_')}.json",
                mime="application/json",
            )

        except Exception as e:
            st.error(f"❌ Ocorreu um erro durante o processamento: {str(e)}")
else:
    st.info(
        "👈 Envie um documento técnico na barra lateral esquerda e selecione os critérios pedagógicos para iniciar a geração."
    )
