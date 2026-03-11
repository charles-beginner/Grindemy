import re
from collections import Counter

import networkx as nx
from sklearn.cluster import KMeans
from sklearn.feature_extraction.text import TfidfVectorizer
from sqlmodel import Session, delete, select

from app.models import NetworkMetric, NewsArticle, TopicCluster

WORD_RE = re.compile(r"[A-Za-z][A-Za-z0-9]{2,}")


def build_topic_clusters(session: Session, k: int = 4) -> list[TopicCluster]:
    articles = session.exec(select(NewsArticle)).all()
    if len(articles) < 2:
        return []

    texts = [f"{a.title} {a.summary or ''}" for a in articles]
    vectorizer = TfidfVectorizer(stop_words="english", max_features=1000)
    matrix = vectorizer.fit_transform(texts)

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
