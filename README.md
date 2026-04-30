# Sohome Pricelist Markup

Adiciona dois campos em cada regra de lista de precos do Odoo:

- `Markup`: multiplier applied to the rule price.
- `Over (%)`: percentage applied after markup. Default: `5.26`.

The final computed price is:

```text
rule price * markup * (1 + over_percent / 100)
```

Example:

```text
fixed price = 1000.00
markup = 1.5
over % = 5.26

final price = 1000.00 * 1.5 * 1.0526 = 1578.90
```

## Variant combinations

Use one pricelist rule per complete product variant (`product.product`), not only per product template.

Example:

```text
Sofa 3m + Fabric A
Sofa 4m + Fabric A
Sofa 3m + Fabric B
Sofa 4m + Fabric B
```

Each combination can have its own fixed price, markup, and additional percentage.

## Security

Only users in the group `Sohome - Markup e Over de listas de precos` can see or change `Markup` and `Over (%)`.

Other users keep using the final computed prices, but the fields are hidden and protected against manual edits/imports.

## Import

Use the fields:

```text
Pricelist
Applied On
Product Variant
Fixed Price
Markup
Over (%)
```

See `demo/pricelist_import_example.csv` for a model import file.
