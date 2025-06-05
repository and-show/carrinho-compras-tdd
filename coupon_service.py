# coupon_service.py

class CouponService:
    """
    Serviço fictício para validar cupons de desconto.
    """
    def __init__(self):
        # Cupons válidos 'hardcoded' para simulação
        self.valid_coupons = {
            "SAVE10": {"type": "percentage", "value": 10}, # 10% de desconto
            "5OFF": {"type": "fixed", "value": 5.0},      # R$5 de desconto fixo
            "INVALIDO": None # Para testar cupons inválidos
        }

    def validate_coupon(self, coupon_code: str) -> dict | None:
        """
        Valida um código de cupom.

        Args:
            coupon_code: O código do cupom a ser validado.

        Returns:
            Um dicionário com os detalhes do cupom se válido (ex: {'type': 'percentage', 'value': 10}),
            ou None se o cupom for inválido.
        """
        if coupon_code in self.valid_coupons:
            return self.valid_coupons[coupon_code]
        # Em um cenário real, isso poderia ser uma chamada de API, consulta a banco de dados, etc.
        # Para este exemplo, apenas retornamos None para códigos não encontrados explicitamente.
        if coupon_code not in self.valid_coupons and coupon_code != "INVALIDO":
             # Simula um cupom que o serviço desconhece
            return None
        return self.valid_coupons.get(coupon_code)