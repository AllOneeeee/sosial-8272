import pickle
import requests
import pandas as pd

from sklearn.metrics.pairwise import cosine_similarity


# =====================
# KBLI
# =====================

df_kbli = pd.read_csv(
    "ai/kbli.csv"
)

with open(
    "ai/kbli_embeddings.pkl",
    "rb"
) as f:
    embeddings_kbli = pickle.load(f)


# =====================
# KBJI
# =====================

df_kbji = pd.read_csv(
    "ai/kbji.csv"
)

with open(
    "ai/kbji_embeddings.pkl",
    "rb"
) as f:
    embeddings_kbji = pickle.load(f)


# =====================
# HF SPACE
# =====================

HF_SPACE_URL = (
    "https://alwan775-alwan7755.hf.space/embed"
)


def get_embedding(text):

    response = requests.post(
        HF_SPACE_URL,
        json={
            "text": f"query: {text}"
        },
        timeout=60
    )

    response.raise_for_status()

    data = response.json()

    return [data["embedding"]]


# =====================
# PREDIKSI KBLI
# =====================

def cari_kbli(text, top_k=5):

    query_embedding = get_embedding(text)

    scores = cosine_similarity(
        query_embedding,
        embeddings_kbli
    )[0]

    top_idx = scores.argsort()[-top_k:][::-1]

    hasil = []

    for i in top_idx:

        hasil.append({
            "kode": str(
                df_kbli.iloc[i]["kode_kbli"]
            ).zfill(5),
            "uraian": str(
                df_kbli.iloc[i]["uraian"]
            ),
            "score": round(
                float(scores[i]) * 100,
                2
            )
        })

    return hasil


# =====================
# PREDIKSI KBJI
# =====================

def cari_kbji(text, top_k=5):

    query_embedding = get_embedding(text)

    scores = cosine_similarity(
        query_embedding,
        embeddings_kbji
    )[0]

    top_idx = scores.argsort()[-top_k:][::-1]

    hasil = []

    for i in top_idx:

        hasil.append({
            "kode": str(
                df_kbji.iloc[i]["kode_kbji"]
            ),
            "uraian": str(
                df_kbji.iloc[i]["uraian"]
            ),
            "score": round(
                float(scores[i]) * 100,
                2
            )
        })

    return hasil