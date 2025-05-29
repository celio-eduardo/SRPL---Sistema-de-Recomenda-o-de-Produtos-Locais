import pandas as pd
import folium
from datetime import datetime
from flask import Blueprint, render_template, request, jsonify, redirect, url_for
from src.models.produto import Produto
from src.models.associacao import Associacao
from src.models.usuario import Usuario
from surprise import Dataset, Reader, KNNBasic

# Criar o blueprint para as rotas principais
main_bp = Blueprint('main', __name__)

# Dados simulados para teste
associacoes = []
produtos = []
usuarios = []

# Função para carregar dados iniciais
def carregar_dados_iniciais():
    # Carregar regiões e associações do CSV
    try:
        df_regioes = pd.read_csv("data/regioes_com_coordenadas.csv")
        df_assoc = pd.read_csv("data/associacoes_formatadas.csv")
        
        # Criar associações
        for i, row in df_assoc.drop_duplicates(subset=["Associação"]).iterrows():
            assoc = Associacao(
                id=i+1,
                nome=row["Associação"],
                regiao=row["Região"],
                lat=row["Lat"],
                lon=row["Lon"]
            )
            associacoes.append(assoc)
            
        # Criar produtos de exemplo para cada associação
        produtos_lista = [
            "Alface", "Mandioca", "Tomate", "Repolho", "Batata", "Cebola", "Couve", 
            "Chuchu", "Morango", "Pimentão", "Brócolis", "Abóbora", "Berinjela", 
            "Beterraba", "Pepino", "Cenoura", "Quiabo", "Agrião", "Jiló", "Gengibre",
            "Abacate", "Goiaba", "Banana", "Limão", "Tangerina", "Maracujá", "Manga", 
            "Lichia", "Uva", "Atemóia", "Cajamanga", "Graviola", "Coco", "Pitaia", "Mamão"
        ]
        
        # Definir sazonalidade para os produtos
        sazonalidade = {
            "Morango": [4, 5, 6, 7, 8, 9],  # Abril a Setembro
            "Manga": [10, 11, 12, 1, 2],    # Outubro a Fevereiro
            "Abacate": [2, 3, 4, 5],        # Fevereiro a Maio
            "Lichia": [12, 1],              # Dezembro e Janeiro
            "Uva": [1, 2, 3],               # Janeiro a Março
            "Tomate": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],  # Ano todo
            "Alface": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],  # Ano todo
            "Cenoura": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], # Ano todo
            "Batata": [3, 4, 5, 6, 7, 8],   # Março a Agosto
            "Cebola": [7, 8, 9, 10, 11],    # Julho a Novembro
        }
        
        # Criar produtos para cada associação
        produto_id = 1
        for assoc in associacoes:
            # Selecionar alguns produtos aleatórios para cada associação
            import random
            produtos_assoc = random.sample(produtos_lista, 10)
            
            for nome_produto in produtos_assoc:
                preco = round(random.uniform(2.0, 15.0), 2)
                categoria = "Fruta" if nome_produto in ["Abacate", "Goiaba", "Banana", "Limão", 
                                                      "Tangerina", "Maracujá", "Manga", "Lichia", 
                                                      "Uva", "Atemóia", "Cajamanga", "Graviola", 
                                                      "Coco", "Pitaia", "Mamão"] else "Hortaliça"
                organico = random.choice([True, False])
                
                produto = Produto(
                    id=produto_id,
                    nome=nome_produto,
                    categoria=categoria,
                    preco=preco,
                    associacao_id=assoc.id,
                    disponivel=True,
                    organico=organico
                )
                
                # Definir sazonalidade se existir para este produto
                if nome_produto in sazonalidade:
                    produto.definir_sazonalidade(sazonalidade[nome_produto])
                
                produtos.append(produto)
                assoc.adicionar_produto(produto)
                produto_id += 1
                
        # Criar usuário de exemplo
        usuario = Usuario(
            id=1,
            nome="Usuário Teste",
            email="usuario@teste.com",
            lat=-15.7939,
            lon=-47.8828  # Coordenadas de Brasília
        )
        usuarios.append(usuario)
        
    except Exception as e:
        print(f"Erro ao carregar dados iniciais: {e}")
        # Criar dados mínimos para teste se não conseguir carregar os CSVs
        if not associacoes:
            assoc = Associacao(
                id=1,
                nome="Associação Teste",
                regiao="Brasília, DF",
                lat=-15.7939,
                lon=-47.8828
            )
            associacoes.append(assoc)
            
            # Criar alguns produtos
            for i, nome in enumerate(["Alface", "Tomate", "Cenoura", "Banana", "Maçã"]):
                produto = Produto(
                    id=i+1,
                    nome=nome,
                    categoria="Fruta" if nome in ["Banana", "Maçã"] else "Hortaliça",
                    preco=round(float(i+5), 2),
                    associacao_id=1,
                    disponivel=True,
                    organico=False
                )
                
                # Definir sazonalidade para alguns produtos
                if nome == "Banana":
                    produto.definir_sazonalidade([1, 2, 3, 4, 5, 6])
                elif nome == "Maçã":
                    produto.definir_sazonalidade([7, 8, 9, 10, 11, 12])
                
                produtos.append(produto)
                assoc.adicionar_produto(produto)
            
            # Criar usuário de exemplo
            usuario = Usuario(
                id=1,
                nome="Usuário Teste",
                email="usuario@teste.com",
                lat=-15.7939,
                lon=-47.8828
            )
            usuarios.append(usuario)

# Rota principal
@main_bp.route('/')
def index():
    return render_template('index.html')  # Agora usando a pasta templates

# Rota para obter dados do mapa
@main_bp.route('/api/mapa')
def get_mapa_data():
    # Obter localização do usuário (padrão: Brasília)
    user_lat = float(request.args.get('lat', -15.7939))
    user_lon = float(request.args.get('lon', -47.8828))
    
    # Criar dados para o mapa
    mapa_data = []
    for assoc in associacoes:
        distancia = assoc.calcular_distancia(user_lat, user_lon)
        mapa_data.append({
            'id': assoc.id,
            'nome': assoc.nome,
            'regiao': assoc.regiao,
            'lat': assoc.lat,
            'lon': assoc.lon,
            'distancia': round(distancia, 2),
            'num_produtos': len(assoc.produtos)
        })
    
    return jsonify(mapa_data)

# Rota para obter produtos
@main_bp.route('/api/produtos')
def get_produtos():
    # Parâmetros de filtro
    associacao_id = request.args.get('associacao_id')
    apenas_organicos = request.args.get('organicos') == 'true'
    mes_atual = request.args.get('mes')
    if mes_atual:
        mes_atual = int(mes_atual)
    else:
        mes_atual = datetime.now().month
    
    # Filtrar produtos
    produtos_filtrados = []
    for produto in produtos:
        # Filtrar por associação se especificado
        if associacao_id and str(produto.associacao_id) != associacao_id:
            continue
            
        # Filtrar por orgânicos se solicitado
        if apenas_organicos and not produto.organico:
            continue
            
        # Filtrar por sazonalidade
        if not produto.esta_disponivel_no_mes(mes_atual):
            continue
            
        # Adicionar à lista de produtos filtrados
        produtos_filtrados.append({
            'id': produto.id,
            'nome': produto.nome,
            'categoria': produto.categoria,
            'preco': produto.preco,
            'associacao_id': produto.associacao_id,
            'disponivel': produto.disponivel,
            'organico': produto.organico,
            'meses_disponibilidade': produto.meses_disponibilidade,
            'media_avaliacoes': produto.media_avaliacoes()
        })
    
    return jsonify(produtos_filtrados)

# Rota para adicionar avaliação
@main_bp.route('/api/avaliar', methods=['POST'])
def avaliar_produto():
    data = request.json
    produto_id = data.get('produto_id')
    pontuacao = data.get('pontuacao')
    comentario = data.get('comentario', '')
    
    # Validar dados
    if not produto_id or not pontuacao:
        return jsonify({'error': 'Produto ID e pontuação são obrigatórios'}), 400
    
    # Encontrar o produto
    produto = next((p for p in produtos if p.id == int(produto_id)), None)
    if not produto:
        return jsonify({'error': 'Produto não encontrado'}), 404
    
    # Adicionar avaliação (usando ID do primeiro usuário para simplificar)
    usuario_id = 1
    produto.adicionar_avaliacao(usuario_id, int(pontuacao), comentario)
    
    # Adicionar avaliação ao usuário também
    usuario = usuarios[0]
    usuario.adicionar_avaliacao(produto_id, int(pontuacao), comentario)
    
    return jsonify({'success': True, 'media': produto.media_avaliacoes()})

# Rota para obter recomendações personalizadas
@main_bp.route('/api/recomendacoes')
def get_recomendacoes():
    # Monta dataframe de avaliações a partir dos objetos em memória
    avaliacoes = []
    for usuario in usuarios:
        for av in usuario.avaliacoes:
            avaliacoes.append([str(usuario.id), str(av["produto_id"]), av["pontuacao"]])
    if not avaliacoes:
        return []

    df = pd.DataFrame(avaliacoes, columns=["usuario_id", "produto_id", "pontuacao"])
    reader = Reader(rating_scale=(1, 5))
    data = Dataset.load_from_df(df, reader)
    trainset = data.build_full_trainset()

    sim_options = {"name": "cosine", "user_based": True}
    algo = KNNBasic(sim_options=sim_options, verbose=False)
    algo.fit(trainset)

    # Produtos já avaliados pelo usuário
    usuario_id_str = str(user_id)
    produtos_avaliados = set(df[df["usuario_id"] == usuario_id_str]["produto_id"])
    todos_produtos = {str(produto.id) for produto in produtos}
    produtos_para_recomendar = list(todos_produtos - produtos_avaliados)

    # Gera previsões para produtos não avaliados
    previsoes = []
    for produto_id in produtos_para_recomendar:
        pred = algo.predict(usuario_id_str, produto_id)
        previsoes.append((produto_id, pred.est))
    # Ordena pelas maiores notas previstas
    previsoes.sort(key=lambda x: -x[1])
    produtos_recomendados_ids = [int(p[0]) for p in previsoes[:n_recommendations]]

  # Monta a resposta detalhada (pode adicionar mais campos conforme já faz)
    produtos_dict = {produto.id: produto for produto in produtos}
    recomendados = []
    for pid in produtos_recomendados_ids:
        produto = produtos_dict[pid]
        recomendados.append({
            "id": produto.id,
            "nome": produto.nome,
            "categoria": produto.categoria,
            "preco": produto.preco,
            "associacao_id": produto.associacao_id,
            "organico": produto.organico,
            "media_avaliacoes": produto.media_avaliacoes(),
        })
    
    # Retorne no máximo 10 recomendações
    #return recomendados[:10]
    
    return jsonify(recomendados[:10])  # Retornar os 10 melhores
