import argparse
import os
import pickle
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from utils import extract_text_from_image, extract_text_from_pdf


def extrair_texto(path: str) -> str:
    ext = os.path.splitext(path)[1].lower()
    if ext in {'.png', '.jpg', '.jpeg'}:
        return extract_text_from_image(path)
    if ext == '.pdf':
        return extract_text_from_pdf(path)
    return ''


def main():
    parser = argparse.ArgumentParser(description='Treina um modelo de classificação de comprovantes.')
    parser.add_argument('planilha', help='Arquivo Excel contendo colunas "arquivo" e "loja"')
    parser.add_argument('--saida', default='modelo_recebimento.pkl', help='Arquivo para salvar o modelo treinado')
    args = parser.parse_args()

    df = pd.read_excel(args.planilha)

    if 'texto' not in df.columns:
        df['texto'] = df['arquivo'].apply(extrair_texto)

    X_train, X_test, y_train, y_test = train_test_split(df['texto'], df['loja'], test_size=0.2, random_state=42)

    pipeline = Pipeline([
        ('tfidf', TfidfVectorizer()),
        ('clf', LogisticRegression(max_iter=1000))
    ])

    pipeline.fit(X_train, y_train)
    score = pipeline.score(X_test, y_test)
    print(f'Acurácia: {score:.2%}')

    with open(args.saida, 'wb') as f:
        pickle.dump(pipeline, f)
    print(f'Modelo salvo em {args.saida}')

if __name__ == '__main__':
    main()