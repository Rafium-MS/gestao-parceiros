import logging

from PIL import Image
import pytesseract
from pdf2image import convert_from_path


def extract_text_from_image(image_path: str, lang: str = 'por') -> str:
    """Extrai texto de um arquivo de imagem usando OCR.

    Args:
        image_path: Caminho para a imagem.
        lang: Idioma para o reconhecimento (padrão: português).

    Returns:
        Texto extraído ou string vazia em caso de erro.
    """
    try:
        image = Image.open(image_path)
        texto = pytesseract.image_to_string(image, lang=lang)
        return texto.strip()
    except Exception as e:
        logging.getLogger(__name__).error(f"Erro de OCR em imagem: {e}")
        return ""


def extract_text_from_pdf(pdf_path: str, lang: str = 'por') -> str:
    """Extrai texto de um arquivo PDF convertendo páginas em imagens.

    Args:
        pdf_path: Caminho para o arquivo PDF.
        lang: Idioma para o reconhecimento (padrão: português).

    Returns:
        Texto extraído ou string vazia em caso de erro.
    """
    try:
        pages = convert_from_path(pdf_path)
        textos = []
        for page in pages:
            textos.append(pytesseract.image_to_string(page, lang=lang))
        return "\n".join(textos).strip()
    except Exception as e:
        logging.getLogger(__name__).error(f"Erro de OCR em PDF: {e}")
        return ""