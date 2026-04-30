# Sohome Pricelist Markup

Modulo Odoo 16 para aplicar `Markup` e `Over (%)` no pedido de venda.

## Como funciona

A lista de precos continua definindo o preco base de cada variante completa do produto.

No pedido de venda aparecem os campos:

- `Markup`
- `Over (%)`

Ao salvar o pedido, o modulo aplica esses fatores em cada linha:

```text
preco unitario base da linha * markup * (1 + over / 100)
```

Exemplo:

```text
preco base da linha = 1000.00
markup = 1.5
over = 5.26

preco unitario final = 1000.00 * 1.5 * 1.0526 = 1578.90
```

O modulo guarda internamente o preco base original da linha em `x_sohome_base_price`, para evitar multiplicar o preco repetidas vezes quando o pedido for salvo novamente.

## Permissoes

Existem permissoes separadas:

- `Sohome - Editar Markup no pedido`
- `Sohome - Editar Over no pedido`

Quem nao tiver o grupo de `Markup` nao ve nem altera o campo `Markup`.

Quem nao tiver o grupo de `Over` nao ve nem altera o campo `Over (%)`.

As permissoes tambem bloqueiam alteracao por importacao/API.

## Localizacao brasileira

O modulo foi pensado para uso com localizacao brasileira, mas nao substitui os addons fiscais. A localizacao BR continua vindo dos addons OCA instalados em `extra-addons`, como `l10n-brazil`.
