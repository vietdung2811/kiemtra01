import numpy as np
import logging
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import ProductMetadata, UserViewLog
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

# Configure logging
logger = logging.getLogger(__name__)

# ─────────────────────────────────────────────
# Shared Embedding Model (lazy-loaded)
# ─────────────────────────────────────────────
MODEL_NAME = 'all-MiniLM-L6-v2'
_model = None

def get_model():
    global _model
    if _model is None:
        logger.info("Loading SentenceTransformer model...")
        _model = SentenceTransformer(MODEL_NAME)
    return _model

def generate_embedding(text: str) -> np.ndarray:
    return get_model().encode(text)


# ─────────────────────────────────────────────
# Helper: Retrieve top-K relevant products by semantic similarity
# ─────────────────────────────────────────────
def retrieve_similar_products(query_embedding: np.ndarray, top_k: int = 5, exclude_ids: list = None):
    """
    RAG Retrieval step:
    Compare query_embedding against all stored product embeddings in DB.
    Returns top_k ProductMetadata objects sorted by similarity score.
    """
    if exclude_ids is None:
        exclude_ids = []

    all_products = ProductMetadata.objects.exclude(product_id__in=exclude_ids).exclude(embedding=None)
    if not all_products.exists():
        return []

    product_list = list(all_products)
    embeddings = []
    valid_products = []

    for p in product_list:
        try:
            vec = np.frombuffer(bytes(p.embedding), dtype=np.float32)
            embeddings.append(vec)
            valid_products.append(p)
        except Exception:
            continue

    if not embeddings:
        return []

    embedding_matrix = np.vstack(embeddings)
    query_vec = query_embedding.reshape(1, -1).astype(np.float32)
    scores = cosine_similarity(query_vec, embedding_matrix)[0]

    top_indices = scores.argsort()[::-1][:top_k]
    results = []
    for idx in top_indices:
        p = valid_products[idx]
        results.append({
            'id': p.product_id,
            'type': p.product_type,
            'brand': p.brand,
            'name': p.name,
            'price': float(p.price),
            'description': p.description,
            'score': float(scores[idx]),
        })
    return results


# ─────────────────────────────────────────────
# Helper: Build a natural language response from context
# ─────────────────────────────────────────────
def generate_rag_response(message: str, products: list, history_lines: list) -> str:
    """
    RAG Generation step:
    Build a context-aware response from retrieved products and user history.
    """
    response_parts = []

    # History context
    if history_lines:
        response_parts.append("📋 **Lịch sử xem gần đây của bạn:**")
        for line in history_lines:
            response_parts.append(f"  - {line}")
        response_parts.append("")

    # Retrieved product context
    if products:
        response_parts.append("🔍 **Sản phẩm phù hợp với yêu cầu của bạn:**")
        for i, p in enumerate(products, 1):
            response_parts.append(
                f"  {i}. **{p['brand']} {p['name']}** ({p['type']}) — "
                f"{p['price']:,.0f}₫\n"
                f"     {p.get('description', '')[:120]}..."
            )
        response_parts.append("")
        response_parts.append(
            "💡 Những sản phẩm trên được gợi ý dựa trên nội dung câu hỏi của bạn. "
            "Bạn có muốn biết thêm chi tiết về sản phẩm nào không?"
        )
    else:
        response_parts.append(
            "Xin lỗi, hiện tôi chưa tìm thấy sản phẩm phù hợp. "
            "Hãy thử hỏi với từ khóa khác như tên thương hiệu, loại sản phẩm, hoặc tính năng cụ thể."
        )

    return "\n".join(response_parts)


# ─────────────────────────────────────────────
# View 1: TrackView — Log user behavior & store embedding
# ─────────────────────────────────────────────
class TrackView(APIView):
    def post(self, request):
        user_id = request.data.get('user_id')
        product_id = request.data.get('product_id')
        product_type = request.data.get('product_type')
        brand = request.data.get('brand', '')
        name = request.data.get('name', '')
        price = request.data.get('price', 0.0)
        description = request.data.get('description', '')

        if not all([user_id, product_id, product_type]):
            return Response({'error': 'Missing required fields: user_id, product_id, product_type'},
                            status=status.HTTP_400_BAD_REQUEST)

        # Generate semantic embedding for product
        text_for_embedding = f"{brand} {name} {description}"
        embedding_vec = generate_embedding(text_for_embedding).astype(np.float32)
        embedding_bytes = embedding_vec.tobytes()

        # Upsert product metadata + embedding
        ProductMetadata.objects.update_or_create(
            product_id=product_id,
            product_type=product_type,
            defaults={
                'brand': brand,
                'name': name,
                'price': price,
                'description': description,
                'embedding': embedding_bytes,
            }
        )

        # Log user view behavior
        UserViewLog.objects.create(
            user_id=user_id,
            product_id=product_id,
            product_type=product_type
        )

        logger.info(f"Tracked: user={user_id} viewed {product_type} id={product_id}")
        return Response({'status': 'success'}, status=status.HTTP_201_CREATED)


# ─────────────────────────────────────────────
# View 2: RecommendView — Content-based RAG Recommendation
# ─────────────────────────────────────────────
class RecommendView(APIView):
    """
    Content-based product recommendation using semantic embeddings.

    Query params:
      - query (str): Free-text description of desired product
      - user_id (int, optional): If provided, use user's history for personalization
      - top_k (int, optional): Number of results (default 5)
    """
    def get(self, request):
        query = request.query_params.get('query', '').strip()
        user_id = request.query_params.get('user_id')
        top_k = int(request.query_params.get('top_k', 5))

        # 1. If we have a query, use semantic search on that query
        if query:
            query_embedding = generate_embedding(query)
            results = retrieve_similar_products(query_embedding, top_k=top_k)
            return Response({'query': query, 'recommendations': results}, status=status.HTTP_200_OK)

        # 2. If no query but we have a user_id, use their history
        if user_id:
            last_views = UserViewLog.objects.filter(user_id=user_id).order_by('-viewed_at')[:3]
            if last_views.exists():
                # Combine metadata of last viewed items to build a profile embedding
                profile_texts = []
                for view in last_views:
                    p = ProductMetadata.objects.filter(product_id=view.product_id, product_type=view.product_type).first()
                    if p:
                        profile_texts.append(f"{p.brand} {p.name} {p.description}")
                
                if profile_texts:
                    profile_query = " ".join(profile_texts)
                    profile_embedding = generate_embedding(profile_query)
                    # Exclude what they already saw
                    viewed_ids = UserViewLog.objects.filter(user_id=user_id).values_list('product_id', flat=True)
                    results = retrieve_similar_products(profile_embedding, top_k=top_k, exclude_ids=list(viewed_ids))
                    return Response({'type': 'personalized', 'recommendations': results}, status=status.HTTP_200_OK)

        # 3. Fallback: Just return the latest products or some default
        latest_products = ProductMetadata.objects.order_by('-id')[:top_k]
        results = []
        for p in latest_products:
            results.append({
                'id': p.product_id,
                'type': p.product_type,
                'brand': p.brand,
                'name': p.name,
                'price': float(p.price),
                'description': p.description,
            })
        
        return Response({'type': 'default', 'recommendations': results}, status=status.HTTP_200_OK)


# ─────────────────────────────────────────────
# View 3: GraphRecommendView — Collaborative Filtering via Neo4j
# ─────────────────────────────────────────────
from neo4j import GraphDatabase

class GraphRecommendView(APIView):
    """
    Collaborative filtering recommendation using Neo4j knowledge graph.
    Finds products viewed by similar users (that current user hasn't seen).
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.driver = GraphDatabase.driver("bolt://neo4j:7687", auth=("neo4j", "password123"))

    def get(self, request):
        user_id = request.query_params.get('user_id')
        if not user_id:
            return Response({'error': 'Missing user_id'}, status=status.HTTP_400_BAD_REQUEST)

        user_id = int(user_id)

        with self.driver.session() as session:
            query = """
            MATCH (u1:User {id: $user_id})-[:ACTED]->(p:Product)<-[:ACTED]-(u2:User)
            MATCH (u2)-[:ACTED]->(rec:Product)
            WHERE u1 <> u2 AND NOT (u1)-[:ACTED]->(rec)
            RETURN rec.id AS product_id, count(*) AS strength
            ORDER BY strength DESC
            LIMIT 5
            """
            result = session.run(query, user_id=user_id)
            rec_ids = [record["product_id"] for record in result]

        recommendations = []
        metas = ProductMetadata.objects.filter(product_id__in=rec_ids)
        for meta in metas:
            recommendations.append({
                'id': meta.product_id,
                'type': meta.product_type,
                'brand': meta.brand,
                'name': meta.name,
                'price': float(meta.price),
                'description': meta.description,
            })

        return Response({'recommendations': recommendations}, status=status.HTTP_200_OK)


# ─────────────────────────────────────────────
# View 4: ChatView — Full RAG Chatbot
# ─────────────────────────────────────────────
class ChatView(APIView):
    """
    RAG-powered chatbot:
      1. Encode user message → semantic embedding
      2. Retrieve top-K relevant products (semantic similarity on DB embeddings)
      3. Augment with user's view history from Neo4j
      4. Generate natural language response from context
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        try:
            self.driver = GraphDatabase.driver("bolt://neo4j:7687", auth=("neo4j", "password123"))
        except Exception as e:
            logger.warning(f"Neo4j not available: {e}")
            self.driver = None

    def _get_user_history(self, user_id: int) -> list:
        """Fetch last 3 user actions from Neo4j graph."""
        if not self.driver or not user_id:
            return []
        try:
            with self.driver.session() as session:
                query = """
                MATCH (u:User {id: $user_id})-[r:ACTED]->(p:Product)
                RETURN p.id AS pid, r.action AS action, r.timestamp AS ts
                ORDER BY r.timestamp DESC
                LIMIT 3
                """
                result = session.run(query, user_id=user_id)
                return [
                    f"{record['action']} sản phẩm #{record['pid']} lúc {record['ts']}"
                    for record in result
                ]
        except Exception as e:
            logger.warning(f"Neo4j query failed: {e}")
            return []

    def post(self, request):
        user_id = request.data.get('user_id')
        message = request.data.get('message', '').strip()

        if not message:
            return Response({'error': 'Empty message'}, status=status.HTTP_400_BAD_REQUEST)

        logger.info(f"ChatView RAG: user={user_id}, message='{message}'")

        # ── Step 1: Encode user message (query representation)
        query_embedding = generate_embedding(message)

        # ── Step 2: Retrieve relevant products from DB (semantic search)
        retrieved_products = retrieve_similar_products(query_embedding, top_k=3)

        # ── Step 3: Augment with user history from Neo4j
        history_lines = []
        if user_id:
            history_lines = self._get_user_history(int(user_id))

        # ── Step 4: Generate natural language response
        reply = generate_rag_response(message, retrieved_products, history_lines)

        return Response({
            'reply': reply,
            'retrieved_products': retrieved_products,  # expose for frontend
        }, status=status.HTTP_200_OK)
