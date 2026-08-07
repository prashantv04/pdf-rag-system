from sentence_transformers import SentenceTransformer


MODEL_NAME = "all-MiniLM-L6-v2"


class EmbeddingModel:
    def __init__(self):
        self.model = SentenceTransformer(MODEL_NAME)

    def encode(self, texts: list[str]) -> list[list[float]]:
        embeddings = self.model.encode(
            texts,
            batch_size=32,
            show_progress_bar=True,
            normalize_embeddings=True,
        )

        return embeddings.tolist()


# from sentence_transformers import SentenceTransformer
#
#
# MODEL_NAME = "all-MiniLM-L6-v2"
#
#
# class EmbeddingModel:
#     def __init__(self):
#         self.model = SentenceTransformer(MODEL_NAME)
#
#     def encode(self, texts: list[str]) -> list[list[float]]:
#         embeddings = self.model.encode(
#             texts,
#             normalize_embeddings=True,
#         )
#
#         return embeddings.tolist()
