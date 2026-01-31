import os

os.environ["PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION"] = "python"
os.environ["TRANSFORMERS_NO_TF"] = "1"  # impede importar tensorflow
os.environ["TRANSFORMERS_NO_FLAX"] = "1"
os.environ["TOKENIZERS_PARALLELISM"] = "false"

os.environ["OMP_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"
os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["VECLIB_MAXIMUM_THREADS"] = "1"
os.environ["NUMEXPR_NUM_THREADS"] = "1"

import random
import re

import joblib
import pandas as pd
import torch
from datasets import load_dataset
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import classification_report
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline
from tqdm import tqdm

# Tradução EN->PT (MarianMT / OPUS-MT)
# Utiliza MarianMT para tradução do dataset de treinamento
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer

torch.set_num_threads(1)
torch.set_num_interop_threads(1)


from dotenv import load_dotenv

load_dotenv()

if not os.getenv("HF_TOKEN") and os.getenv("HUGGINGFACE_HUB_TOKEN"):
    os.environ["HF_TOKEN"] = os.environ["HUGGINGFACE_HUB_TOKEN"]


# Categorias finais (PT-BR)
CATS_PT = [
    "Renda",
    "Mercado",
    "Moradia",
    "Transporte",
    "Lazer",
    "Saúde",
    "Assinaturas",
    "Educação",
    "Viagem",
    "Outros",
]

# Mapeando dataset
BASE_MAP = {
    "Income": "Renda",
    "Transportation": "Transporte",
    "Healthcare & Medical": "Saúde",
    "Utilities & Services": "Moradia",
    "Entertainment & Recreation": "Lazer",
    "Food & Dining": "Mercado",
    "Shopping & Retail": "Outros",
    "Financial Services": "Outros",
    "Government & Legal": "Outros",
    "Charity & Donations": "Outros",
}

RESTAURANT_HINTS = [
    "mcdonald",
    "burger",
    "pizza",
    "restaurant",
    "cafe",
    "coffee",
    "bar",
    "steak",
    "sushi",
    "starbucks",
    "kfc",
    "subway",
    "taco",
    "grill",
    "bistro",
]


def normalize_pt(text: str) -> str:
    t = (text or "").lower()
    t = t.replace("apê", "apartamento").replace("condo", "condominio")
    t = re.sub(r"\s+", " ", t).strip()
    return t


def brl(amount: float) -> str:
    amount = float(amount)
    s = f"{amount:,.2f}"
    s = s.replace(",", "X").replace(".", ",").replace("X", ".")
    return f"R$ {s}"


def sample_amount_for_cat(cat_pt: str) -> float:
    ranges = {
        "Mercado": (10, 450),
        "Moradia": (50, 1200),
        "Transporte": (8, 220),
        "Lazer": (15, 500),
        "Saúde": (20, 900),
        "Assinaturas": (9, 80),
        "Educação": (30, 900),
        "Viagem": (80, 3500),
        "Renda": (800, 15000),
        "Outros": (10, 800),
    }
    lo, hi = ranges.get(cat_pt, (10, 500))
    return random.uniform(lo, hi)


def map_category_en_to_pt(cat_en: str, desc_en: str) -> str:
    base = BASE_MAP.get(cat_en, "Outros")

    if cat_en == "Food & Dining":
        d = (desc_en or "").lower()
        if any(h in d for h in RESTAURANT_HINTS):
            return "Lazer"
        return "Mercado"

    return base


def make_translator(model_name="Helsinki-NLP/opus-mt-tc-big-en-pt", device=None):
    tokenizer = AutoTokenizer.from_pretrained(model_name, token=True)
    model = AutoModelForSeq2SeqLM.from_pretrained(model_name, token=True)

    if device is None:
        if torch.backends.mps.is_available():
            device = "mps"
        elif torch.cuda.is_available():
            device = "cuda"
        else:
            device = "cpu"
    print(f"[translator] device={device}", flush=True)

    model = model.to(device)

    model.eval()

    def translate_batch(texts, batch_size=64, max_length=64):
        outs = []
        for i in tqdm(range(0, len(texts), batch_size), desc="Translating"):
            batch = texts[i : i + batch_size]
            tok = tokenizer(
                batch,
                return_tensors="pt",
                padding=True,
                truncation=True,
                max_length=max_length,
            ).to(device)

            with torch.inference_mode():
                gen = model.generate(**tok, max_length=max_length)

            outs.extend(tokenizer.batch_decode(gen, skip_special_tokens=True))
        return outs

    return translate_batch


ds = load_dataset("mitulshah/transaction-categorization", token=True)
df = ds["train"].to_pandas()
df = df.rename(columns={"transaction_description": "text_en", "category": "cat_en"})

MAX_ROWS = 20000
df = df.sample(n=min(len(df), MAX_ROWS), random_state=42).reset_index(drop=True)

df["label_pt"] = [
    map_category_en_to_pt(c, t) for c, t in zip(df["cat_en"], df["text_en"])
]

translate_batch = make_translator()
texts_pt = translate_batch(df["text_en"].tolist(), batch_size=32)
df["text_pt"] = texts_pt
df["amount_brl"] = [sample_amount_for_cat(c) for c in df["label_pt"]]
df["text_pt"] = df["text_pt"] + " " + df["amount_brl"].map(brl)


# Exemplos sintéticos para categorias ausentes
def synth_examples(n_per_cat=250):
    templates = {
        "Moradia": [
            "Paguei aluguel do apartamento",
            "Condomínio do prédio",
            "Conta de luz",
            "Conta de água",
            "Internet residencial",
            "Gás de cozinha",
            "IPTU",
        ],
        "Transporte": [
            "Uber para o trabalho",
            "Corrida 99",
            "Gasolina no posto",
            "Estacionamento",
            "Pedágio",
            "Passagem de ônibus",
            "Metrô",
        ],
        "Mercado": [
            "Compras no supermercado",
            "Carrefour",
            "Assaí atacadista",
            "Pão e leite na padaria",
            "Feira de legumes",
            "Açougue",
            "Delivery de mercado",
        ],
        "Lazer": [
            "Restaurante",
            "iFood jantar",
            "Cinema",
            "Bar com amigos",
            "Show",
            "Sorvete",
            "Viagem de fim de semana",
        ],
        "Saúde": [
            "Farmácia",
            "Consulta médica",
            "Exame de sangue",
            "Dentista",
            "Plano de saúde",
            "Compra de remédio",
        ],
        "Assinaturas": [
            "Renovação Netflix",
            "Spotify mensal",
            "Amazon Prime renovação",
            "YouTube Premium",
            "iCloud mensal",
        ],
        "Educação": [
            "Mensalidade faculdade",
            "Curso de Python",
            "Udemy curso ML",
            "Compra de livro",
            "Alura assinatura anual",
        ],
        "Viagem": [
            "Passagem aérea",
            "Hotel reservado",
            "Airbnb",
            "Aluguel de carro viagem",
            "Seguro viagem",
        ],
        "Renda": [
            "Salário recebido",
            "Recebimento de freelas",
            "Pagamento do cliente",
            "Pix recebido",
            "Comissão",
        ],
        "Outros": [
            "Presente",
            "Doação",
            "Taxa bancária",
            "Serviço",
            "Manutenção",
            "Compra diversa",
        ],
    }

    rows = []
    for cat, temps in templates.items():
        for _ in range(n_per_cat):
            t = random.choice(temps)
            a = brl(sample_amount_for_cat(cat))
            rows.append({"text_pt": f"{t} {a}", "label_pt": cat})
    return pd.DataFrame(rows)


df_synth = synth_examples(n_per_cat=250)

df_train_all = (
    pd.concat(
        [df[["text_pt", "label_pt"]], df_synth[["text_pt", "label_pt"]]],
        ignore_index=True,
    )
    .sample(frac=1, random_state=42)
    .reset_index(drop=True)
)

df_train_all["text_pt"] = df_train_all["text_pt"].map(normalize_pt)

X_train, X_test, y_train, y_test = train_test_split(
    df_train_all["text_pt"],
    df_train_all["label_pt"],
    test_size=0.2,
    random_state=42,
    stratify=df_train_all["label_pt"],
)

model = Pipeline(
    [
        (
            "tfidf",
            TfidfVectorizer(
                ngram_range=(1, 2), min_df=1, sublinear_tf=True, strip_accents="unicode"
            ),
        ),
        ("nb", MultinomialNB(alpha=0.2)),
    ]
)

model.fit(X_train, y_train)

pred = model.predict(X_test)
print(classification_report(y_test, pred))

joblib.dump(model, "expense_clf_tfidf_nb_ptbr.joblib")
print("Salvo em: expense_clf_tfidf_nb_ptbr.joblib")
