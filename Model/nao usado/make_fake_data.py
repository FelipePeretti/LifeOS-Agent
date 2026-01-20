import random
import pandas as pd

CATS = ["Renda","Mercado","Moradia","Transporte","Lazer","Saúde","Assinaturas","Educação","Viagem","Outros"]

templates = {
  "Renda": [
    "Recebi salário", "Pix recebido do {pessoa}", "Pagamento {empresa}", "Bônus do trabalho",
    "Recebimento freelance {tipo}", "Depósito de salário {empresa}"
  ],
  "Mercado": [
    "Compra no {mercado}", "Fui no {mercado} comprar comida", "Açougue {loja}", "Padaria {loja}",
    "Hortifruti {loja}", "Compra de supermercado {mercado}"
  ],
  "Moradia": [
    "Paguei aluguel", "Conta de luz {empresa}", "Conta de água {empresa}", "Internet {empresa}",
    "Gás de cozinha", "Condomínio do apartamento"
  ],
  "Transporte": [
    "Uber para {lugar}", "99 para {lugar}", "Gasolina no {posto}", "Estacionamento {lugar}",
    "Passagem de ônibus", "Pedágio {lugar}"
  ],
  "Lazer": [
    "Cinema com amigos", "Restaurante {rest}", "Bar {rest}", "Ifood {rest}",
    "Show/ingresso", "Sorvete {rest}"
  ],
  "Saúde": [
    "Farmácia {farm}", "Consulta médica", "Exame de sangue", "Plano de saúde {empresa}",
    "Dentista", "Remédio {med}"
  ],
  "Assinaturas": [
    "Netflix", "Spotify", "Amazon Prime", "YouTube Premium",
    "Assinatura {serv}", "Renovação {serv}"
  ],
  "Educação": [
    "Mensalidade faculdade", "Curso {curso}", "Compra de livro {livro}",
    "Udemy {curso}", "Alura", "Material escolar"
  ],
  "Viagem": [
    "Passagem aérea {cia}", "Hotel em {lugar}", "Airbnb {lugar}",
    "Aluguel de carro", "Passeio turístico {lugar}", "Seguro viagem"
  ],
  "Outros": [
    "Presente para {pessoa}", "Compra na {loja}", "Serviço {serv}", "Manutenção {item}",
    "Doação", "Pagamento diverso"
  ]
}

fills = {
  "pessoa": ["mãe","pai","cliente","João","Maria"],
  "empresa": ["Claro","Vivo","Tim","Enel","Copasa","Unimed","Nubank","Itaú"],
  "mercado": ["Assaí","Carrefour","Atacadão","Pão de Açúcar","Supermercado local"],
  "loja": ["da esquina","Central","Bom Preço","Popular"],
  "lugar": ["trabalho","casa","aeroporto","academia","centro"],
  "posto": ["Shell","Ipiranga","BR","Ale"],
  "rest": ["Outback","McDonald's","Burger King","Restaurante japonês","Pizzaria"],
  "farm": ["Drogasil","Droga Raia","Pague Menos","Panvel"],
  "med": ["dipirona","ibuprofeno","vitamina C","antialérgico"],
  "serv": ["iCloud","Google One","Office 365","ChatGPT Plus"],
  "curso": ["Python","Machine Learning","Inglês","Power BI"],
  "livro": ["estatística","machine learning","finanças pessoais"],
  "cia": ["Latam","Gol","Azul"],
  "item": ["celular","carro","moto","computador"]
}

def render(t):
  for k, vals in fills.items():
    t = t.replace("{"+k+"}", random.choice(vals))
  return t

def add_noise(s):
  noises = ["", "", "", " ✅", " 😅", " (pix)", " urgente", " hoje"]
  s2 = s + random.choice(noises)
  if random.random() < 0.25:
    s2 += f" R$ {random.randint(10,600)},{random.randint(0,99):02d}"
  if random.random() < 0.15:
    s2 = s2.upper()
  return s2

rows = []
n_per_cat = 250  # ajuste (250*10 = 2500 linhas)
for cat in CATS:
  for _ in range(n_per_cat):
    t = random.choice(templates[cat])
    text = add_noise(render(t))
    rows.append({"text": text, "label": cat})

df = pd.DataFrame(rows).sample(frac=1, random_state=42).reset_index(drop=True)
df.to_csv("expenses_pt_synth.csv", index=False)
print(df.head(), "=>", df["label"].value_counts().to_dict())
