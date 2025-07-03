"""Pacote de utilidades do sistema."""

# Importação opcional das funções de OCR.
try:
    from .ocr_utils import (
        extract_text_from_image,
        extract_text_from_pdf,
        extract_text_from_image_bytes,
        extract_text_from_pdf_bytes,
        preprocess_image,
        set_tesseract_cmd,
        detect_orientation,
    )
except Exception:  # pylint: disable=broad-except
    # Caso as dependências de OCR não estejam instaladas, definimos stubs
    def extract_text_from_image(*_args, **_kwargs):  # type: ignore
        raise ImportError("Dependências de OCR não instaladas")

    def extract_text_from_pdf(*_args, **_kwargs):  # type: ignore
        raise ImportError("Dependências de OCR não instaladas")

    def extract_text_from_image_bytes(*_args, **_kwargs):  # type: ignore
        raise ImportError("Dependências de OCR não instaladas")

    def extract_text_from_pdf_bytes(*_args, **_kwargs):  # type: ignore
        raise ImportError("Dependências de OCR não instaladas")

    def preprocess_image(*_args, **_kwargs):  # type: ignore
        raise ImportError("Dependências de OCR não instaladas")

    def set_tesseract_cmd(*_args, **_kwargs):  # type: ignore
        raise ImportError("Dependências de OCR não instaladas")

    def detect_orientation(*_args, **_kwargs):  # type: ignore
        raise ImportError("Dependências de OCR não instaladas")

try:
    from .gui_utils import (
        carregar_combobox_por_cidade,
        carregar_combobox_cidades_por_parceiro,
        carregar_combobox_parceiros_por_loja,
    )
    from .pasta_utils import criar_estrutura_comprovantes, renomear_comprovantes_auto
except Exception:  # pylint: disable=broad-except

    def carregar_combobox_por_cidade(*_args, **_kwargs):  # type: ignore
        return {}

    def carregar_combobox_cidades_por_parceiro(*_args, **_kwargs):  # type: ignore
        return []

    def carregar_combobox_parceiros_por_loja(*_args, **_kwargs):  # type: ignore
        return {}

    def criar_estrutura_comprovantes(*_args, **_kwargs):  # type: ignore
        return ""

    def renomear_comprovantes_auto(*_args, **_kwargs):  # type: ignore
        return ""

__all__ = [
    "extract_text_from_image",
    "extract_text_from_pdf",
    "extract_text_from_image_bytes",
    "extract_text_from_pdf_bytes",
    "preprocess_image",
    "set_tesseract_cmd",
    "detect_orientation",
    "carregar_combobox_por_cidade",
    "carregar_combobox_cidades_por_parceiro",
    "carregar_combobox_parceiros_por_loja",
    "criar_estrutura_comprovantes",
    "renomear_comprovantes_auto",
]