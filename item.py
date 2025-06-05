# item.py
from decimal import Decimal, ROUND_HALF_UP

class Item:
    def __init__(self, name: str, quantity: int, unit_price: str | float | Decimal):
        if not isinstance(name, str) or not name.strip():
            raise ValueError("O nome do item não pode ser vazio.")
        if not isinstance(quantity, int) or quantity <= 0:
            raise ValueError("A quantidade deve ser um inteiro positivo.")
        
        try:
            self._unit_price = Decimal(str(unit_price))
            if self._unit_price < Decimal("0"):
                raise ValueError("O preço unitário não pode ser negativo.")
        except Exception as e:
            raise ValueError(f"Preço unitário inválido: {e}")

        self._name = name
        self._quantity = quantity

    @property
    def name(self) -> str:
        return self._name

    @property
    def quantity(self) -> int:
        return self._quantity

    @quantity.setter
    def quantity(self, value: int):
        if not isinstance(value, int) or value < 0: # Permitir 0 para o caso de ser removido
            raise ValueError("A quantidade deve ser um inteiro não negativo.")
        self._quantity = value

    @property
    def unit_price(self) -> Decimal:
        return self._unit_price

    @unit_price.setter
    def unit_price(self, value: str | float | Decimal):
        try:
            new_price = Decimal(str(value))
            if new_price < Decimal("0"):
                raise ValueError("O preço unitário não pode ser negativo.")
            self._unit_price = new_price
        except Exception as e:
            raise ValueError(f"Preço unitário inválido ao atualizar: {e}")
            
    @property
    def total_price(self) -> Decimal:
        return (self.quantity * self.unit_price).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    def __repr__(self) -> str:
        return f"Item(name='{self.name}', quantity={self.quantity}, unit_price='{self.unit_price}')"

    def to_dict(self) -> dict:
        """Retorna uma representação do item como dicionário, útil para listagem."""
        return {
            "name": self.name,
            "quantity": self.quantity,
            "unit_price": self.unit_price,
            "total_price": self.total_price
        }