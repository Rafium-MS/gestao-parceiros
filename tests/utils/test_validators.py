import pytest
from utils import validators


@pytest.mark.parametrize(
    "cpf,is_valid",
    [
        ("123.456.789-01", False),
        ("11144477735", True),
        ("00000000000", False),
    ],
)
def test_validar_cpf(cpf, is_valid):
    assert validators.validar_cpf(cpf) is is_valid


def test_formatar_cpf():
    assert validators.formatar_cpf("11144477735") == "111.444.777-35"


@pytest.mark.parametrize(
    "cnpj,is_valid",
    [
        ("12.345.678/9012-34", False),
        ("11222333000181", True),
        ("00000000000000", False),
    ],
)
def test_validar_cnpj(cnpj, is_valid):
    assert validators.validar_cnpj(cnpj) is is_valid


def test_formatar_cnpj():
    assert (
        validators.formatar_cnpj("11222333000181")
        == "11.222.333/0001-81"
    )


def test_validar_email():
    assert validators.validar_email("usuario@example.com")
    assert not validators.validar_email("invalido@")


@pytest.mark.parametrize(
    "telefone,formated",
    [
        ("1122334455", "(11) 2233-4455"),
        ("11987654321", "(11) 98765-4321"),
    ],
)
def test_formatar_telefone(telefone, formated):
    assert validators.formatar_telefone(telefone) == formated


def test_validar_data():
    ok, dt = validators.validar_data("01/12/2023")
    assert ok and dt.year == 2023
    ok, dt = validators.validar_data("32/01/2023")
    assert not ok and dt is None