import re
from collections import Counter

import networkx as nx
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.feature_extraction.text import TfidfVectorizer
from sqlmodel import Session, delete, select

from app.models import NetworkMetric, NewsArticle, TopicCluster
from app.schemas import (
    KMeansPoint,
    KMeansVisualization,
    NetworkEdge,
    NetworkNode,
    NetworkVisualization,
)

WORD_RE = re.compile(r"[A-Za-z][A-Za-z0-9]{2,}")


def _build_feature_matrix(articles: list[NewsArticle]):
    texts = [f"{a.title} {a.summary or ''}" for a in articles]
    vectorizer = TfidfVectorizer(stop_words="english", max_features=1000)
    matrix = vectorizer.fit_transform(texts)
    return matrix, vectorizer


def build_topic_clusters(session: Session, k: int = 4) -> list[TopicCluster]:
    articles = session.exec(select(NewsArticle)).all()
    if len(articles) < 2:
        return []

    matrix, vectorizer = _build_feature_matrix(articles)
    k = max(1, min(k, len(articles)))
    model = KMeans(n_clusters=k, n_init="auto", random_state=42)
    labels = model.fit_predict(matrix)

    session.exec(delete(TopicCluster))
    feature_names = vectorizer.get_feature_names_out()
    clusters: list[TopicCluster] = []

    for cluster_idx in range(k):
        article_indexes = [i for i, label in enumerate(labels) if label == cluster_idx]
        center = model.cluster_centers_[cluster_idx]
        top_word_indexes = center.argsort()[-3:][::-1]
        top_words = [feature_names[idx] for idx in top_word_indexes if center[idx] > 0]
        label = " ".join(top_words) if top_words else f"topic-{cluster_idx + 1}"
        hashtag = "#" + "".join(word.title() for word in label.split())

        topic = TopicCluster(
            hashtag=hashtag,
            label=label,
            article_count=len(article_indexes),
            score=float(center[top_word_indexes[0]]) if len(top_word_indexes) else 0.0,
        )
        session.add(topic)
        clusters.append(topic)

    session.commit()
    for c in clusters:
        session.refresh(c)
    return clusters


def get_kmeans_visualization(session: Session, k: int = 4) -> KMeansVisualization:
    articles = session.exec(select(NewsArticle).order_by(NewsArticle.published_at.desc())).all()
    if len(articles) < 2:
        return KMeansVisualization(points=[])

    matrix, vectorizer = _build_feature_matrix(articles)
    k = max(1, min(k, len(articles)))
    model = KMeans(n_clusters=k, n_init="auto", random_state=42)
    labels = model.fit_predict(matrix)

    dense = matrix.toarray()
    reduced = PCA(n_components=2, random_state=42).fit_transform(dense)

    feature_names = vectorizer.get_feature_names_out()
    cluster_hashtags: dict[int, str] = {}
    for cluster_idx in range(k):
        center = model.cluster_centers_[cluster_idx]
        top_word_indexes = center.argsort()[-3:][::-1]
        top_words = [feature_names[idx] for idx in top_word_indexes if center[idx] > 0]
        label = " ".join(top_words) if top_words else f"topic-{cluster_idx + 1}"
        cluster_hashtags[cluster_idx] = "#" + "".join(word.title() for word in label.split())

    points: list[KMeansPoint] = []
    for idx, article in enumerate(articles):
        points.append(
            KMeansPoint(
                article_id=article.id or 0,
                title=article.title,
                category=article.category,
                cluster_id=int(labels[idx]),
                cluster_hashtag=cluster_hashtags[int(labels[idx])],
                x=float(reduced[idx][0]),
                y=float(reduced[idx][1]),
            )
        )

    return KMeansVisualization(points=points)


def build_keyword_network(session: Session, top_n: int = 25) -> list[NetworkMetric]:
    articles = session.exec(select(NewsArticle)).all()
    if not articles:
        return []

    graph = nx.Graph()
    for article in articles:
        words = WORD_RE.findall(f"{article.title} {article.summary or ''}".lower())
        frequent_words = [w for w, _ in Counter(words).most_common(8)]
        for i, word_a in enumerate(frequent_words):
            graph.add_node(word_a)
            for word_b in frequent_words[i + 1 :]:
                if word_a == word_b:
                    continue
                if graph.has_edge(word_a, word_b):
                    graph[word_a][word_b]["weight"] += 1
                else:
                    graph.add_edge(word_a, word_b, weight=1)

    session.exec(delete(NetworkMetric))
    degree = nx.degree_centrality(graph)
    between = nx.betweenness_centrality(graph)

    ranked = sorted(degree.items(), key=lambda item: item[1], reverse=True)[:top_n]
    metrics: list[NetworkMetric] = []

    for keyword, degree_score in ranked:
        metric = NetworkMetric(
            keyword=keyword,
            degree_centrality=float(degree_score),
            betweenness_centrality=float(between.get(keyword, 0.0)),
        )
        session.add(metric)
        metrics.append(metric)

    session.commit()
    for m in metrics:
        session.refresh(m)
    return metrics


def get_network_visualization(session: Session, top_n: int = 25) -> NetworkVisualization:
    articles = session.exec(select(NewsArticle)).all()
    if not articles:
        return NetworkVisualization(nodes=[], edges=[])

    graph = nx.Graph()
    for article in articles:
        words = WORD_RE.findall(f"{article.title} {article.summary or ''}".lower())
        frequent_words = [w for w, _ in Counter(words).most_common(8)]
        for i, word_a in enumerate(frequent_words):
            for word_b in frequent_words[i + 1 :]:
                if word_a == word_b:
                    continue
                if graph.has_edge(word_a, word_b):
                    graph[word_a][word_b]["weight"] += 1
                else:
                    graph.add_edge(word_a, word_b, weight=1)

    if graph.number_of_nodes() == 0:
        return NetworkVisualization(nodes=[], edges=[])

    degree = nx.degree_centrality(graph)
    between = nx.betweenness_centrality(graph)
    top_nodes = sorted(degree, key=degree.get, reverse=True)[:top_n]
    subgraph = graph.subgraph(top_nodes).copy()

    nodes = [
        NetworkNode(
            id=node,
            label=node,
            degree_centrality=float(degree.get(node, 0.0)),
            betweenness_centrality=float(between.get(node, 0.0)),
        )
        for node in subgraph.nodes
    ]
    edges = [
        NetworkEdge(source=u, target=v, weight=float(data.get("weight", 1.0)))
        for u, v, data in subgraph.edges(data=True)
    ]
    return NetworkVisualization(nodes=nodes, edges=edges)
