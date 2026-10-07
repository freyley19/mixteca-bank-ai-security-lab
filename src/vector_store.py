# Author: @freyley.leyva

import json
import os

import chromadb
import requests


OLLAMA_HOST = os.getenv(
    "OLLAMA_HOST",
    "http://localhost:11434",
)

EMBED_MODEL = os.getenv(
    "EMBED_MODEL",
    "nomic-embed-text",
)


def get_embedding(text):
    r = requests.post(
        f"{OLLAMA_HOST}/api/embeddings",
        json={
            "model": EMBED_MODEL,
            "prompt": text,
        },
        timeout=30,
    )

    r.raise_for_status()

    return r.json()["embedding"]


class VectorManager:
    def __init__(self):
        self.client = chromadb.Client()

        try:
            self.client.delete_collection("mixteca_docs")
        except Exception:
            pass

        self.collection = self.client.create_collection(
            "mixteca_docs"
        )

        self._seed_data()

    def _seed_data(self):
        data_path = os.path.join(
            os.path.dirname(__file__),
            "..",
            "data",
            "bank_data.json",
        )

        with open(data_path, encoding="utf-8") as f:
            docs = json.load(f)

        self.collection.add(
            ids=[
                d["id"]
                for d in docs
            ],
            documents=[
                d["content"]
                for d in docs
            ],
            metadatas=[
                {
                    "owner_id": d["owner_id"],
                    "category": d["category"],
                    "trust_level": d.get(
                        "trust_level",
                        "untrusted",
                    ),
                }
                for d in docs
            ],
            embeddings=[
                get_embedding(d["content"])
                for d in docs
            ],
        )

    def query(
        self,
        text,
        user_id,
        mode,
        n_results=2,
    ):
        args = {
            "query_embeddings": [
                get_embedding(text)
            ],
            "n_results": n_results,
        }

        # ---------------------------------------------------------
        # HARDENED MODE
        #
        # Un documento debe superar DOS controles:
        #
        # 1. AUTORIZACIÓN
        #    - pertenece al usuario
        #    - o es público
        #
        # 2. CONFIANZA
        #    - trust_level == trusted
        #
        # Public no significa trusted.
        # Authorized no significa safe.
        # ---------------------------------------------------------
        if mode == "hardened":
            args["where"] = {
                "$and": [
                    {
                        "$or": [
                            {
                                "owner_id": {
                                    "$eq": user_id
                                }
                            },
                            {
                                "owner_id": {
                                    "$eq": "public"
                                }
                            },
                        ]
                    },
                    {
                        "trust_level": {
                            "$eq": "trusted"
                        }
                    },
                ]
            }

        r = self.collection.query(**args)

        # ---------------------------------------------------------
        # OBSERVABILIDAD DEL RETRIEVAL
        #
        # Esto nos permite comprobar qué documentos llegaron
        # realmente desde Chroma antes de construir el contexto.
        # ---------------------------------------------------------
        print(
            "\n[DEBUG RETRIEVAL]"
            f"\n  ids: {r.get('ids', [[]])[0]}"
            f"\n  distances: {r.get('distances', [[]])[0]}",
            flush=True,
        )

        return (
            r.get("documents", [[]])[0],
            r.get("ids", [[]])[0],
        )