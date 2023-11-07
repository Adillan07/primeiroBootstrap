CREATE TABLE IF NOT EXISTS produtos (
    id_prod INTEGER PRIMARY KEY,
    nome_prod TEXT NOT NULL,
    descricao_prod TEXT NOT NULL,
    preco_prod DECIMAL(5,2) NOT NULL,
    imagem_prod TEXT NOT NULL 
);