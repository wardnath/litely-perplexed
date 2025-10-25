#!/usr/bin/env python3
"""Quick test script for the API"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_health():
    print("Testing health endpoint...")
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(json.dumps(response.json(), indent=2))
    print()

def test_search(query="quantum computing", top_k=5):
    print(f"Testing search with query: '{query}'")
    params = {
        "q": query,
        "top_k": top_k,
        "summarize": True,
        "cluster_summary": True,
        "use_mmr": True
    }
    response = requests.get(f"{BASE_URL}/search", params=params)
    print(f"Status: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        print(f"\nQuery: {data['query']}")
        print(f"Total results: {data['total']}")

        if data.get('cluster_summary'):
            print(f"\nCluster Summary:\n{data['cluster_summary']}")

        print(f"\nTop {len(data['results'])} Results:")
        for i, result in enumerate(data['results'], 1):
            print(f"\n{i}. {result['title']}")
            print(f"   URL: {result['url']}")
            print(f"   Scores - BM25: {result.get('bm25_score', 0):.3f}, "
                  f"Semantic: {result.get('semantic_score', 0):.3f}, "
                  f"Hybrid: {result.get('hybrid_score', 0):.3f}")
            if result.get('summary'):
                print(f"   Summary: {result['summary'][:150]}...")
    else:
        print(f"Error: {response.text}")

if __name__ == "__main__":
    test_health()
    print("\n" + "="*80 + "\n")
    test_search()
