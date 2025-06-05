# shopping_cart.py

from decimal import Decimal, ROUND_HALF_UP
from item import Item # Importa a classe Item
# coupon_service.py não é modificado, então não precisa ser importado aqui se não for usado diretamente
# mas o Cart o recebe no construtor.

class Cart:
    def __init__(self, coupon_service=None):
        self._items = {}  # Agora armazena {nome_item: InstanciaDeItem}
        self._applied_coupon = None
        self.coupon_service = coupon_service

    def add_item(self, name: str, quantity: int, unit_price: float | str | Decimal):
        """Adiciona um item ao carrinho ou atualiza sua quantidade e preço."""
        # A classe Item já faz validações de nome, quantidade e preço.
        # A lógica aqui é para atualizar um item existente ou adicionar um novo.
        try:
            # Tenta converter unit_price para Decimal aqui para consistência,
            # embora o Item.__init__ e o setter também façam.
            price_decimal = Decimal(str(unit_price))
        except Exception:
            raise ValueError("Preço unitário inválido fornecido ao carrinho.")

        if price_decimal < Decimal("0"):
            raise ValueError("O preço unitário não pode ser negativo.")
        
        if not isinstance(quantity, int) or quantity <= 0:
            raise ValueError("A quantidade para adicionar deve ser um inteiro positivo.")
        
        if not isinstance(name, str) or not name.strip():
            raise ValueError("O nome do item não pode ser vazio.")


        if name in self._items:
            existing_item = self._items[name]
            existing_item.quantity += quantity
            existing_item.unit_price = price_decimal # Atualiza o preço unitário do item existente
        else:
            # A classe Item cuidará da validação detalhada ao criar a instância
            self._items[name] = Item(name=name, quantity=quantity, unit_price=price_decimal)

    def remove_item(self, name: str, quantity_to_remove: int | None = None):
        """Remove um item do carrinho ou diminui sua quantidade."""
        if name not in self._items:
            return # Nenhuma ação se o item não existir

        item_in_cart = self._items[name]

        if quantity_to_remove is None or quantity_to_remove >= item_in_cart.quantity:
            del self._items[name]
        elif quantity_to_remove > 0:
            item_in_cart.quantity -= quantity_to_remove
        elif quantity_to_remove <= 0: # Não permitir remover quantidade zero ou negativa
            raise ValueError("A quantidade a ser removida deve ser positiva.")

    def _calculate_subtotal(self) -> Decimal:
        """Calcula o subtotal dos itens no carrinho."""
        total = Decimal("0.00")
        for item_obj in self._items.values():
            total += item_obj.total_price # Usa a propriedade total_price da classe Item
        return total.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    def apply_coupon(self, coupon_code: str) -> bool:
        """
        Aplica um cupom de desconto ao carrinho.
        Requer que um coupon_service tenha sido injetado na criação do carrinho.
        """
        if not self.coupon_service:
            return False

        coupon_data = self.coupon_service.validate_coupon(coupon_code)
        if coupon_data:
            # Valida o valor do cupom antes de aplicar
            try:
                # Garante que o valor do cupom seja Decimal
                coupon_value = Decimal(str(coupon_data.get('value', 0)))
                if coupon_value < Decimal("0"):
                    # print("Valor do cupom inválido (negativo), não aplicando.")
                    self._applied_coupon = None
                    return False
                
                # Atualiza coupon_data com o valor Decimal
                coupon_data['value'] = coupon_value
                self._applied_coupon = coupon_data

            except Exception:
                # print(f"Valor do cupom '{coupon_code}' não é um número válido.")
                self._applied_coupon = None
                return False
            return True
        else:
            self._applied_coupon = None # Remove qualquer cupom anterior se o novo for inválido
            return False

    def get_total(self) -> Decimal:
        """Calcula o valor total do carrinho, aplicando descontos se houver."""
        subtotal = self._calculate_subtotal()
        total_after_discount = subtotal

        if self._applied_coupon:
            discount_type = self._applied_coupon.get('type')
            # O valor já deve ser Decimal se apply_coupon foi bem-sucedido
            discount_value = self._applied_coupon.get('value', Decimal("0"))

            if discount_type == 'percentage':
                if discount_value > Decimal("100"): # Cap de 100% para desconto percentual
                    discount_value = Decimal("100")
                elif discount_value < Decimal("0"): # Não permitir percentual negativo
                    discount_value = Decimal("0")
                
                discount_amount = (subtotal * discount_value) / Decimal("100")
                total_after_discount -= discount_amount
            elif discount_type == 'fixed':
                # discount_value já é Decimal e validado como não negativo em apply_coupon
                total_after_discount -= discount_value
        
        final_total = max(Decimal("0.00"), total_after_discount)
        return final_total.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    def list_items(self) -> list[dict]:
        """Lista os itens no carrinho usando o método to_dict() de cada Item."""
        if not self._items:
            return []
        
        return [item_obj.to_dict() for item_obj in self._items.values()]

    def clear_cart(self):
        """Limpa todos os itens e o cupom aplicado do carrinho."""
        self._items = {}
        self._applied_coupon = None