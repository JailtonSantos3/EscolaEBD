import json
import os
import streamlit as st
import pandas as pd

# Configuração da página
st.set_page_config(
    page_title="Sistema de Escola Dominical",
    page_icon="⛪",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Arquivo de dados
DATA_FILE = os.path.join(os.path.dirname(__file__), 'students.json')


def load_students():
    """Carrega alunos do arquivo JSON"""
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []


def save_students(students):
    """Salva alunos no arquivo JSON"""
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(students, f, ensure_ascii=False, indent=2)


def add_student(nome, idade, congregacao, turma):
    """Adiciona um novo aluno"""
    students = load_students()
    next_id = 1 if not students else max(aluno['matricula'] for aluno in students) + 1
    aluno = {'matricula': next_id, 'nome': nome.strip(), 'idade': idade, 'congregacao': congregacao.strip(), 'turma': turma.strip()}
    students.append(aluno)
    save_students(students)
    return True


def update_student(student_id, nome, idade, congregacao, turma):
    """Atualiza dados de um aluno"""
    students = load_students()
    for aluno in students:
        if aluno['matricula'] == student_id:
            aluno['nome'] = nome.strip()
            aluno['idade'] = idade
            aluno['congregacao'] = congregacao.strip()
            aluno['turma'] = turma.strip()
            save_students(students)
            return True
    return False


def delete_student(student_id):
    """Deleta um aluno"""
    students = load_students()
    updated = [aluno for aluno in students if aluno['matricula'] != student_id]
    if len(updated) == len(students):
        return False
    save_students(updated)
    return True


def get_student_by_id(student_id):
    """Retorna um aluno pelo ID"""
    students = load_students()
    for aluno in students:
        if aluno['matricula'] == student_id:
            return aluno
    return None


# Estilos CSS
st.markdown("""
<style>
    .main-title {
        text-align: center;
        color: #1f77b4;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        text-align: center;
    }
    .success-message {
        background-color: #d4edda;
        color: #155724;
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# Título principal
st.markdown("<h1 class='main-title'>⛪Sistema de Escola Dominical</h1>", unsafe_allow_html=True)

# Inicializar session state para controlar modal de edição
if 'show_edit_form' not in st.session_state:
    st.session_state.show_edit_form = False
if 'edit_student_id' not in st.session_state:
    st.session_state.edit_student_id = None

# Sidebar com navegação
st.sidebar.title("Menu")
page = st.sidebar.radio("Selecione uma opção:", 
                         ["📊 Dashboard", "➕ Novo Aluno", "👥 Lista de Alunos"])

students = load_students()

# ==================== DASHBOARD ====================
if page == "📊 Dashboard":
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(label="Total de Alunos", value=len(students))
    
    with col2:
        idade_media = round(sum(a['idade'] for a in students) / len(students)) if students else 0
        st.metric(label="Idade Média", value=f"{idade_media} anos")
    
    with col3:
        congregacoes = len(set(a['congregacao'] for a in students))
        st.metric(label="Congregações", value=congregacoes)
    
    st.divider()
    
    if students:
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Distribuição por Congregação")
            congregacao_count = pd.Series([a['congregacao'] for a in students]).value_counts()
            st.bar_chart(congregacao_count)
        
        with col2:
            st.subheader("Distribuição por Turma")
            turma_count = pd.Series([a['turma'] for a in students]).value_counts()
            st.bar_chart(turma_count)

# ==================== NOVO ALUNO ====================
elif page == "➕ Novo Aluno":
    st.header("Cadastrar Novo Aluno")
    
    with st.form("novo_aluno_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            nome = st.text_input("Nome Completo", placeholder="Ex: João Silva Santos")
            idade = st.number_input("Idade", min_value=1, max_value=120, step=1)
        
        with col2:
            congregacao = st.text_input("Congregação", placeholder="Ex: Centro")
            turma = st.text_input("Turma", placeholder="Ex: Infantil")
            submitted = st.form_submit_button("✅ Cadastrar Aluno", use_container_width=True)
        
        if submitted:
            if nome.strip() and idade > 0 and congregacao.strip() and turma.strip():
                if add_student(nome, idade, congregacao, turma):
                    st.success(f"✅ Aluno '{nome}' cadastrado com sucesso!")
                    st.rerun()
            else:
                st.error("❌ Preencha todos os campos corretamente.")

# ==================== LISTA DE ALUNOS ====================
elif page == "👥 Lista de Alunos":
    st.header("Lista de Alunos")
    
    if not students:
        st.info("📭 Nenhum aluno cadastrado. Adicione um novo aluno para começar!")
    else:
        # Filtros
        col1, col2, col3 = st.columns(3)
        
        with col1:
            search_term = st.text_input("🔍 Buscar por nome:", placeholder="Digite o nome do aluno")
        
        with col2:
            filter_congregacao = st.selectbox("Filtrar por congregação:", ["Todos"] + sorted(list(set(a['congregacao'] for a in students))))
        
        with col3:
            sort_by = st.selectbox("Ordenar por:", ["Matrícula", "Nome", "Idade"])
        
        # Aplicar filtros
        filtered_students = students
        
        if search_term:
            filtered_students = [a for a in filtered_students if search_term.lower() in a['nome'].lower()]
        
        if filter_congregacao != "Todos":
            filtered_students = [a for a in filtered_students if a['congregacao'] == filter_congregacao]
        
        # Ordenar
        if sort_by == "Nome":
            filtered_students = sorted(filtered_students, key=lambda x: x['nome'])
        elif sort_by == "Idade":
            filtered_students = sorted(filtered_students, key=lambda x: x['idade'])
        else:
            filtered_students = sorted(filtered_students, key=lambda x: x['matricula'])
        
        st.divider()
        
        if not filtered_students:
            st.warning("⚠️ Nenhum aluno encontrado com os filtros aplicados.")
        else:
            # Mostrar alunos em formato de tabela com ações
            col1, col2, col3, col4, col5, col6, col7 = st.columns([1, 3, 1, 2, 2, 1, 1])
            with col1:
                st.write("**Matrícula**")
            with col2:
                st.write("**Nome**")
            with col3:
                st.write("**Idade**")
            with col4:
                st.write("**Congregação**")
            with col5:
                st.write("**Turma**")
            with col6:
                st.write("**Ações**")
            with col7:
                st.write("")
            
            st.divider()
            
            for aluno in filtered_students:
                col1, col2, col3, col4, col5, col6, col7 = st.columns([1, 3, 1, 2, 2, 1, 1])
                
                with col1:
                    st.write(f"#{aluno['matricula']}")
                with col2:
                    st.write(aluno['nome'])
                with col3:
                    st.write(f"{aluno['idade']} anos")
                with col4:
                    st.write(aluno['congregacao'])
                with col5:
                    st.write(aluno['turma'])
                with col6:
                    if st.button("✏️ Editar", key=f"edit_{aluno['matricula']}"):
                        st.session_state.show_edit_form = True
                        st.session_state.edit_student_id = aluno['matricula']
                with col7:
                    if st.button("🗑️ Deletar", key=f"delete_{aluno['matricula']}"):
                        if delete_student(aluno['matricula']):
                            st.success(f"Aluno deletado com sucesso!")
                            st.rerun()
            
            st.divider()
            
            # DataFrame para exportação
            df = pd.DataFrame(filtered_students)
            st.subheader("📥 Exportar Dados")
            csv = df.to_csv(index=False, encoding='utf-8-sig')
            st.download_button(
                label="⬇️ Baixar como CSV",
                data=csv,
                file_name="alunos.csv",
                mime="text/csv"
            )
    
    # Modal de edição
    if st.session_state.show_edit_form and st.session_state.edit_student_id:
        st.divider()
        st.subheader("✏️ Editar Aluno")
        
        student = get_student_by_id(st.session_state.edit_student_id)
        
        if student:
            with st.form("edit_aluno_form"):
                nome = st.text_input("Nome Completo", value=student['nome'])
                idade = st.number_input("Idade", min_value=1, max_value=120, step=1, value=student['idade'])
                congregacao = st.text_input("Congregação", value=student['congregacao'])
                turma = st.text_input("Turma", value=student['turma'])
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.form_submit_button("💾 Salvar Alterações"):
                        if update_student(st.session_state.edit_student_id, nome, idade, congregacao, turma):
                            st.success("Aluno atualizado com sucesso!")
                            st.session_state.show_edit_form = False
                            st.rerun()
                
                with col2:
                    if st.form_submit_button("❌ Cancelar"):
                        st.session_state.show_edit_form = False
                        st.rerun()
