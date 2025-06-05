# test_shopping_cart.py
import unittest
from decimal import Decimal, ROUND_HALF_UP # ROUND_HALF_UP não é usado diretamente nos testes, mas Decimal é.
from shopping_cart import Cart
from coupon_service import CouponService # Usaremos a implementação real (mock) para "integração"
# A classe Item não precisa ser importada diretamente nos testes,
# pois interagimos com ela através da interface da classe Cart.

class TestShoppingCartUnit(unittest.TestCase):
    def setUp(self):
        self.cart = Cart() # Por padrão, sem coupon_service para testes unitários puros do Cart

    def test_add_new_item(self):
        self.cart.add_item("Maçã", 2, "0.50")
        self.assertEqual(len(self.cart.list_items()), 1)
        item_data = self.cart.list_items()[0]
        self.assertEqual(item_data['name'], "Maçã")
        self.assertEqual(item_data['quantity'], 2)
        self.assertEqual(item_data['unit_price'], Decimal("0.50")) # Item.to_dict() retorna Decimal
        self.assertEqual(item_data['total_price'], Decimal("1.00"))

    def test_add_existing_item_updates_quantity_and_price(self):
        self.cart.add_item("Banana", 1, "0.30")
        self.cart.add_item("Banana", 3, "0.35") # Adicionando mais e atualizando o preço
        
        self.assertEqual(len(self.cart.list_items()), 1)
        item_data = self.cart.list_items()[0]
        self.assertEqual(item_data['name'], "Banana")
        self.assertEqual(item_data['quantity'], 4) # 1 + 3
        self.assertEqual(item_data['unit_price'], Decimal("0.35")) # Preço foi atualizado
        self.assertEqual(item_data['total_price'], (Decimal('4') * Decimal('0.35')).quantize(Decimal("0.01"))) # 4 * 0.35 = 1.40

    def test_add_item_invalid_quantity(self):
        with self.assertRaisesRegex(ValueError, "A quantidade para adicionar deve ser um inteiro positivo."):
            self.cart.add_item("Uva", 0, "1.00")
        with self.assertRaisesRegex(ValueError, "A quantidade para adicionar deve ser um inteiro positivo."):
            self.cart.add_item("Uva", -1, "1.00")

    def test_add_item_invalid_price_format(self):
        with self.assertRaisesRegex(ValueError, "Preço unitário inválido fornecido ao carrinho."):
            self.cart.add_item("Pera", 1, "abc")

    def test_add_item_negative_price(self):
        with self.assertRaisesRegex(ValueError, "O preço unitário não pode ser negativo."):
            self.cart.add_item("Pera", 1, "-1.00")
            
    def test_add_item_invalid_name(self):
        with self.assertRaisesRegex(ValueError, "O nome do item não pode ser vazio."):
            self.cart.add_item("", 1, "1.00")
        with self.assertRaisesRegex(ValueError, "O nome do item não pode ser vazio."):
            self.cart.add_item("  ", 1, "1.00")

    def test_remove_item_completely(self):
        self.cart.add_item("Laranja", 3, "0.70")
        self.cart.remove_item("Laranja") # Remove todas as 3 unidades
        self.assertEqual(len(self.cart.list_items()), 0)

    def test_remove_item_completely_by_specifying_exact_quantity(self):
        self.cart.add_item("Laranja", 3, "0.70")
        self.cart.remove_item("Laranja", 3) 
        self.assertEqual(len(self.cart.list_items()), 0)

    def test_remove_partial_quantity_of_item(self):
        self.cart.add_item("Melancia", 5, "3.00")
        self.cart.remove_item("Melancia", 2)
        
        self.assertEqual(len(self.cart.list_items()), 1)
        item_data = self.cart.list_items()[0]
        self.assertEqual(item_data['name'], "Melancia")
        self.assertEqual(item_data['quantity'], 3) # 5 - 2

    def test_remove_more_quantity_than_exists(self):
        self.cart.add_item("Morango", 3, "1.50")
        self.cart.remove_item("Morango", 5) # Tenta remover mais do que existe
        self.assertEqual(len(self.cart.list_items()), 0) # Deve remover o item completamente

    def test_remove_non_existent_item(self):
        self.cart.add_item("Kiwi", 1, "0.80")
        self.cart.remove_item("Abacaxi") # Tenta remover item que não está no carrinho
        self.assertEqual(len(self.cart.list_items()), 1) # Carrinho deve permanecer inalterado
        self.assertEqual(self.cart.list_items()[0]['name'], "Kiwi")

    def test_remove_item_invalid_quantity_to_remove(self):
        self.cart.add_item("Figo", 3, "0.90")
        with self.assertRaisesRegex(ValueError, "A quantidade a ser removida deve ser positiva."):
            self.cart.remove_item("Figo", 0)
        with self.assertRaisesRegex(ValueError, "A quantidade a ser removida deve ser positiva."):
            self.cart.remove_item("Figo", -2)
        
        self.assertEqual(len(self.cart.list_items()), 1)
        self.assertEqual(self.cart.list_items()[0]['quantity'], 3) # Quantidade não deve mudar

    def test_calculate_total_empty_cart(self):
        self.assertEqual(self.cart.get_total(), Decimal("0.00"))

    def test_calculate_total_single_item(self):
        self.cart.add_item("Pão", 2, "2.50") # Total 2 * 2.50 = 5.00
        self.assertEqual(self.cart.get_total(), Decimal("5.00"))

    def test_calculate_total_multiple_items(self):
        self.cart.add_item("Leite", 1, "4.50")    # 4.50
        self.cart.add_item("Café", 1, "10.25")   # 10.25
        # Total 4.50 + 10.25 = 14.75
        self.assertEqual(self.cart.get_total(), Decimal("14.75"))

    def test_list_items_empty_cart(self):
        self.assertEqual(self.cart.list_items(), [])

    def test_list_items_with_items(self):
        self.cart.add_item("Suco", 2, "3.00")     # Total 6.00
        self.cart.add_item("Biscoito", 3, "1.50") # Total 4.50
        items_list = self.cart.list_items()
        self.assertEqual(len(items_list), 2)
        
        expected_items_data = {
            "Suco": {"quantity": 2, "unit_price": Decimal("3.00"), "total_price": Decimal("6.00")},
            "Biscoito": {"quantity": 3, "unit_price": Decimal("1.50"), "total_price": Decimal("4.50")}
        }

        for item_dict in items_list:
            name = item_dict['name']
            self.assertTrue(name in expected_items_data)
            self.assertEqual(item_dict['quantity'], expected_items_data[name]['quantity'])
            self.assertEqual(item_dict['unit_price'], expected_items_data[name]['unit_price'])
            self.assertEqual(item_dict['total_price'], expected_items_data[name]['total_price'])

    def test_clear_cart(self):
        self.cart.add_item("Item1", 1, "10.00")
        # Simular aplicação de cupom diretamente para testar se é limpo
        # (Note: _applied_coupon é um detalhe de implementação, mas útil para este teste específico de clear_cart)
        self.cart._applied_coupon = {"type": "fixed", "value": Decimal("1.00"), "code": "TESTCLEAR"} 
        
        self.cart.clear_cart()
        
        self.assertEqual(self.cart.list_items(), [])
        self.assertEqual(self.cart.get_total(), Decimal("0.00"))
        self.assertIsNone(self.cart._applied_coupon)


class TestShoppingCartIntegration(unittest.TestCase):
    def setUp(self):
        self.coupon_service = CouponService() # Usamos a implementação "real" (mock) do serviço
        self.cart = Cart(coupon_service=self.coupon_service)

    def test_apply_valid_percentage_coupon(self):
        self.cart.add_item("Produto A", 1, "100.00") # Subtotal = 100.00
        applied = self.cart.apply_coupon("SAVE10") # 10% de desconto
        
        self.assertTrue(applied)
        self.assertIsNotNone(self.cart._applied_coupon)
        self.assertEqual(self.cart._applied_coupon['type'], 'percentage')
        self.assertEqual(self.cart._applied_coupon['value'], Decimal("10")) # apply_coupon converte para Decimal
        # Total = 100.00 - 10% (10.00) = 90.00
        self.assertEqual(self.cart.get_total(), Decimal("90.00"))

    def test_apply_valid_fixed_coupon(self):
        self.cart.add_item("Produto B", 2, "20.00") # Subtotal = 40.00
        applied = self.cart.apply_coupon("5OFF") # R$5 de desconto
        
        self.assertTrue(applied)
        self.assertIsNotNone(self.cart._applied_coupon)
        self.assertEqual(self.cart._applied_coupon['type'], 'fixed')
        self.assertEqual(self.cart._applied_coupon['value'], Decimal("5.0")) # apply_coupon converte para Decimal
        # Total = 40.00 - 5.00 = 35.00
        self.assertEqual(self.cart.get_total(), Decimal("35.00"))

    def test_apply_invalid_coupon_code(self):
        self.cart.add_item("Produto C", 1, "50.00") # Subtotal = 50.00
        applied = self.cart.apply_coupon("CUPOMINVALIDO123") # Código não existe no CouponService
        
        self.assertFalse(applied)
        self.assertIsNone(self.cart._applied_coupon) # Cupom inválido não deve ser aplicado
        self.assertEqual(self.cart.get_total(), Decimal("50.00")) # Total não deve mudar

    def test_apply_coupon_when_service_returns_none_for_coupon_details(self):
        self.cart.add_item("Produto D", 1, "30.00")
        # O cupom "INVALIDO" está configurado no mock CouponService para retornar None nos detalhes
        applied = self.cart.apply_coupon("INVALIDO")
        
        self.assertFalse(applied)
        self.assertIsNone(self.cart._applied_coupon)
        self.assertEqual(self.cart.get_total(), Decimal("30.00"))

    def test_coupon_discount_makes_total_negative_should_be_zero(self):
        self.cart.add_item("Produto E", 1, "3.00") # Subtotal = 3.00
        self.cart.apply_coupon("5OFF") # R$5 de desconto
        # Total = 3.00 - 5.00 = -2.00, mas deve ser 0.00
        self.assertEqual(self.cart.get_total(), Decimal("0.00"))

    def test_reapply_coupon_overwrites_previous(self):
        self.cart.add_item("Produto F", 1, "200.00") # Subtotal = 200.00
        
        self.cart.apply_coupon("SAVE10") # 10% -> Total = 180.00
        self.assertEqual(self.cart.get_total(), Decimal("180.00"))
        self.assertEqual(self.cart._applied_coupon['type'], 'percentage')

        self.cart.apply_coupon("5OFF") # R$5 de desconto sobre 200.00 -> Total = 195.00
        self.assertEqual(self.cart.get_total(), Decimal("195.00"))
        self.assertEqual(self.cart._applied_coupon['type'], 'fixed') # Verifica se o último cupom foi aplicado

    def test_apply_invalid_coupon_after_valid_one_removes_discount(self):
        self.cart.add_item("Produto G", 1, "100.00")
        self.cart.apply_coupon("SAVE10") # Total 90.00
        self.assertEqual(self.cart.get_total(), Decimal("90.00"))

        applied_invalid = self.cart.apply_coupon("CUPOMQUENAOEXISTE") # Cupom inválido
        self.assertFalse(applied_invalid)
        self.assertIsNone(self.cart._applied_coupon) # Cupom deve ser removido/resetado
        self.assertEqual(self.cart.get_total(), Decimal("100.00")) # Total volta ao subtotal

    def test_full_scenario_valid_coupon_and_item_removal(self):
        # 1. Adicionar itens
        self.cart.add_item("Laptop", 1, "2500.00")
        self.cart.add_item("Mouse", 2, "75.00") # 2 * 75 = 150
        # Subtotal = 2500 + 150 = 2650.00

        # 2. Listar itens (verificação opcional aqui, mais para depuração)
        items = self.cart.list_items()
        self.assertEqual(len(items), 2)

        # 3. Verificar subtotal (através de método interno para granularidade do teste)
        self.assertEqual(self.cart._calculate_subtotal(), Decimal("2650.00"))

        # 4. Aplicar cupom válido
        self.assertTrue(self.cart.apply_coupon("SAVE10")) # 10% de 2650 = 265.00
        # Total = 2650.00 - 265.00 = 2385.00
        self.assertEqual(self.cart.get_total(), Decimal("2385.00"))

        # 5. Remover uma unidade de um item
        self.cart.remove_item("Mouse", 1) # Remove 1 mouse, resta 1
        # Novo subtotal: Laptop (2500) + Mouse (1 * 75) = 2575.00
        self.assertEqual(self.cart._calculate_subtotal(), Decimal("2575.00"))

        # 6. Calcular total final novamente (cupom ainda aplicado ao novo subtotal)
        # Desconto de 10% em 2575.00 = 257.50
        # Total = 2575.00 - 257.50 = 2317.50
        self.assertEqual(self.cart.get_total(), Decimal("2317.50"))

        # 7. Listar itens novamente para verificar o estado
        items_after_removal = self.cart.list_items()
        self.assertEqual(len(items_after_removal), 2)
        mouse_item_data = next(item_d for item_d in items_after_removal if item_d['name'] == "Mouse")
        self.assertEqual(mouse_item_data['quantity'], 1)

    def test_cart_without_coupon_service_apply_coupon_fails_gracefully(self):
        cart_no_service = Cart() # Sem injetar coupon_service
        cart_no_service.add_item("Produto X", 1, "10.00")
        
        applied = cart_no_service.apply_coupon("SAVE10")
        
        self.assertFalse(applied) # Não deve aplicar se não há serviço
        self.assertIsNone(cart_no_service._applied_coupon)
        self.assertEqual(cart_no_service.get_total(), Decimal("10.00")) # Total não muda

if __name__ == '__main__':
    unittest.main(argv=['first-arg-is-ignored'], exit=False) # exit=False é útil para rodar em alguns ambientes como Jupyter