import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-key-change-in-production')
    DEBUG = os.environ.get('DEBUG', 'false').lower() == 'true'
    DATABASE_PATH = os.environ.get('DATABASE_PATH', 'loja.db')

CATEGORIAS_VALIDAS = ['informatica', 'moveis', 'vestuario', 'geral', 'eletronicos', 'livros']
STATUS_VALIDOS = ['pendente', 'aprovado', 'enviado', 'entregue', 'cancelado']
