from odoo import _, api, fields, models
from odoo.exceptions import AccessError
from odoo.tools import float_round


class SaleOrder(models.Model):
    _inherit = "sale.order"

    x_sohome_markup = fields.Float(
        string="Markup",
        default=1.0,
        help="Multiplicador aplicado ao preco unitario de cada linha do pedido.",
    )
    x_sohome_over_percent = fields.Float(
        string="Over (%)",
        default=5.26,
        help="Percentual aplicado depois do markup em cada linha do pedido.",
    )

    def _sohome_price_factor(self):
        self.ensure_one()
        markup = self.x_sohome_markup or 0.0
        over_percent = self.x_sohome_over_percent or 0.0
        return markup * (1.0 + over_percent / 100.0)

    def _sohome_check_restricted_fields_access(self, vals):
        if self.env.is_superuser():
            return
        if "x_sohome_markup" in vals and not self.env.user.has_group(
            "sohome_pricelist_markup.group_sohome_sale_markup"
        ):
            raise AccessError(_("Voce nao tem permissao para alterar o Markup do pedido."))
        if "x_sohome_over_percent" in vals and not self.env.user.has_group(
            "sohome_pricelist_markup.group_sohome_sale_over"
        ):
            raise AccessError(_("Voce nao tem permissao para alterar o Over do pedido."))

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            self._sohome_check_restricted_fields_access(vals)
        orders = super().create(vals_list)
        orders._sohome_apply_adjustments_to_lines()
        return orders

    def write(self, vals):
        self._sohome_check_restricted_fields_access(vals)
        result = super().write(vals)
        if not self.env.context.get("skip_sohome_price_adjustment"):
            self._sohome_apply_adjustments_to_lines()
        return result

    def _sohome_apply_adjustments_to_lines(self):
        for order in self:
            factor = order._sohome_price_factor()
            for line in order.order_line.filtered(lambda item: not item.display_type):
                base_price = line.x_sohome_base_price or line.price_unit
                if not line.x_sohome_base_price:
                    line.with_context(skip_sohome_price_adjustment=True).write({
                        "x_sohome_base_price": base_price,
                    })
                adjusted_price = float_round(
                    base_price * factor,
                    precision_rounding=order.currency_id.rounding,
                )
                if line.price_unit != adjusted_price:
                    line.with_context(skip_sohome_price_adjustment=True).write({
                        "price_unit": adjusted_price,
                    })


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    x_sohome_base_price = fields.Float(
        string="Preco Base Sohome",
        digits="Product Price",
        copy=False,
        help="Preco unitario antes da aplicacao de Markup e Over do pedido.",
    )

    @api.model_create_multi
    def create(self, vals_list):
        lines = super().create(vals_list)
        lines.order_id._sohome_apply_adjustments_to_lines()
        return lines

    def write(self, vals):
        if (
            "price_unit" in vals
            and not self.env.context.get("skip_sohome_price_adjustment")
        ):
            vals = dict(vals, x_sohome_base_price=vals["price_unit"])
        result = super().write(vals)
        if not self.env.context.get("skip_sohome_price_adjustment"):
            self.order_id._sohome_apply_adjustments_to_lines()
        return result
