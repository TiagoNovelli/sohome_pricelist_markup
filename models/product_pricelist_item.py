from odoo import _, api, fields, models
from odoo.exceptions import AccessError


class ProductPricelistItem(models.Model):
    _inherit = "product.pricelist.item"

    _SOHOME_RESTRICTED_FIELDS = {
        "x_sohome_markup",
        "x_sohome_over_percent",
    }

    x_sohome_markup = fields.Float(
        string="Markup",
        default=1.0,
        help="Multiplicador aplicado ao preco da regra. Exemplo: 1,5 aumenta a linha em 50%.",
    )
    x_sohome_over_percent = fields.Float(
        string="Over (%)",
        default=5.26,
        help="Percentual aplicado depois do markup. Padrao: 5,26%.",
    )
    x_sohome_adjusted_fixed_price = fields.Float(
        string="Preco Final Calculado",
        compute="_compute_sohome_adjusted_fixed_price",
        digits="Product Price",
        help="Previa do preco fixo multiplicado pelo Markup e pelo Over.",
    )

    @api.depends("fixed_price", "x_sohome_markup", "x_sohome_over_percent")
    def _compute_sohome_adjusted_fixed_price(self):
        for item in self:
            item.x_sohome_adjusted_fixed_price = item.fixed_price * item._sohome_price_factor()

    def _sohome_price_factor(self):
        self.ensure_one()
        markup = self.x_sohome_markup or 0.0
        over_percent = self.x_sohome_over_percent or 0.0
        return markup * (1.0 + over_percent / 100.0)

    def _sohome_check_restricted_fields_access(self, vals_list):
        if self.env.is_superuser():
            return
        vals_list = vals_list if isinstance(vals_list, list) else [vals_list]
        restricted_fields = set().union(*(vals.keys() for vals in vals_list)) & self._SOHOME_RESTRICTED_FIELDS
        if restricted_fields and not self.env.user.has_group(
            "sohome_pricelist_markup.group_sohome_pricelist_markup_manager"
        ):
            raise AccessError(
                _(
                    "Somente usuarios do grupo 'Sohome - Markup e Over de listas de precos' "
                    "podem criar ou alterar Markup e Over."
                )
            )

    @api.model_create_multi
    def create(self, vals_list):
        self._sohome_check_restricted_fields_access(vals_list)
        return super().create(vals_list)

    def write(self, vals):
        self._sohome_check_restricted_fields_access(vals)
        return super().write(vals)

    def _compute_price(self, product, quantity, uom, date, currency=None):
        price = super()._compute_price(product, quantity, uom, date, currency=currency)
        self.ensure_one()
        price *= self._sohome_price_factor()
        return currency.round(price) if currency else price
