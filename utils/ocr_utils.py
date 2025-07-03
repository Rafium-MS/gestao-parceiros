import logging
import io
import re


from PIL import Image, ImageOps
from pdf2image import convert_from_path, convert_from_bytes
import pytesseract

pages = convert_from_path(pdf_path, dpi=300, poppler_path=r'C:\Users\rafael\Documents\projetos\poppler-24.08.0\Library\bin')

# Caminho padrão do executável do Tesseract no Windows.
# Pode ser alterado em tempo de execução com ``set_tesseract_cmd``.
pytesseract.pytesseract.tesseract_cmd = r'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'

def set_tesseract_cmd(cmd_path: str) -> None:
    """Define o caminho do executável do Tesseract."""
    pytesseract.pytesseract.tesseract_cmd = cmd_path


def preprocess_image(image: Image.Image, *, grayscale: bool = True, threshold: int | None = None) -> Image.Image:
    """Realiza pré-processamento simples de uma imagem para melhorar o OCR."""
    if grayscale:
        image = ImageOps.grayscale(image)
    if threshold is not None:
        image = image.point(lambda p: 255 if p > threshold else 0)
    return image


def detect_orientation(image: Image.Image) -> int:
    """Detecta a orientação de uma imagem em graus."""
    try:
        osd = pytesseract.image_to_osd(image)
        match = re.search(r'Rotate: (\d+)', osd)
        if match:
            return int(match.group(1))
    except Exception as e:  # pylint: disable=broad-except
        logging.getLogger(__name__).error(f"Erro ao detectar orientação: {e}")
    return 0


def extract_text_from_image_bytes(image_bytes: bytes, lang: str = 'por') -> str:
    """Extrai texto de uma imagem fornecida em bytes."""
    try:
        with Image.open(io.BytesIO(image_bytes)) as img:
            img = preprocess_image(img)
            texto = pytesseract.image_to_string(img, lang=lang)
            return texto.strip()
    except Exception as e:  # pylint: disable=broad-except
        logging.getLogger(__name__).error(f"Erro de OCR em imagem via bytes: {e}")
        return ""



def extract_text_from_pdf_bytes(pdf_bytes: bytes, lang: str = 'por') -> str:
    """Extrai texto de um PDF fornecido em bytes."""
    try:
        pages = convert_from_bytes(pdf_bytes)
        textos = []
        for page in pages:
            page = preprocess_image(page)
            textos.append(pytesseract.image_to_string(page, lang=lang))
        return "\n".join(textos).strip()
    except Exception as e:  # pylint: disable=broad-except
        logging.getLogger(__name__).error(f"Erro de OCR em PDF via bytes: {e}")
        return ""


def extract_text_from_image(image_path: str, lang: str = 'por') -> str:
    """Extrai texto de um arquivo de imagem usando OCR."""
    try:
        image = Image.open(image_path)
        image = preprocess_image(image)
        texto = pytesseract.image_to_string(image, lang=lang)
        return texto.strip()
    except Exception as e:  # pylint: disable=broad-except
        logging.getLogger(__name__).error(f"Erro de OCR em imagem: {e}")
        return ""


def extract_text_from_pdf(pdf_path: str, lang: str = 'por') -> str:
    """Extrai texto de um arquivo PDF convertendo páginas em imagens."""
    try:
        pages = convert_from_path(pdf_path)
        textos = []
        for page in pages:
            page = preprocess_image(page)
            textos.append(pytesseract.image_to_string(page, lang=lang))
        return "\n".join(textos).strip()
    except Exception as e:  # pylint: disable=broad-except
        logging.getLogger(__name__).error(f"Erro de OCR em PDF: {e}")
        return ""