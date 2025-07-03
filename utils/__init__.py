"""Pacote de utilidades do sistema."""

# Importação opcional das funções de OCR.
try:
    from .ocr_utils import extract_text_from_image, extract_text_from_pdf
except Exception:  # pylint: disable=broad-except
    # Caso as dependências de OCR não estejam instaladas, definimos stubs
    def extract_text_from_image(*_args, **_kwargs):  # type: ignore
        raise ImportError("Dependências de OCR não instaladas")

    def extract_text_from_pdf(*_args, **_kwargs):  # type: ignore
        raise ImportError("Dependências de OCR não instaladas")

__all__ = ["extract_text_from_image", "extract_text_from_pdf"]