# Author: @freyley.leyva
import chromadb, requests, json, os
OLLAMA_HOST=os.getenv("OLLAMA_HOST","http://localhost:11434"); EMBED_MODEL=os.getenv("EMBED_MODEL","nomic-embed-text")
def get_embedding(text):
    r=requests.post(f"{OLLAMA_HOST}/api/embeddings",json={"model":EMBED_MODEL,"prompt":text},timeout=30); r.raise_for_status(); return r.json()["embedding"]
class VectorManager:
    def __init__(self):
        self.client=chromadb.Client();
        try:self.client.delete_collection("mixteca_docs")
        except Exception:pass
        self.collection=self.client.create_collection("mixteca_docs"); self._seed_data()
    def _seed_data(self):
        with open(os.path.join(os.path.dirname(__file__),"..","data","bank_data.json"),encoding="utf-8") as f: docs=json.load(f)
        self.collection.add(ids=[d["id"] for d in docs],documents=[d["content"] for d in docs],metadatas=[{"owner_id":d["owner_id"],"category":d["category"]} for d in docs],embeddings=[get_embedding(d["content"]) for d in docs])
    def query(self,text,user_id,mode,n_results=2):
        args={"query_embeddings":[get_embedding(text)],"n_results":n_results}
        if mode=="hardened": args["where"]={"$or":[{"owner_id":{"$eq":user_id}},{"owner_id":{"$eq":"public"}}]}
        r=self.collection.query(**args); return r.get("documents",[[]])[0],r.get("ids",[[]])[0]
