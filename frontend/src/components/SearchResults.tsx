interface SearchResult {
  url: string
  title: string
  text?: string
  summary?: string
  bm25_score?: number
  semantic_score?: number
  hybrid_score?: number
}

interface SearchResponse {
  query: string
  cluster_summary?: string
  results: SearchResult[]
  total: number
}

interface SearchResultsProps {
  results: SearchResponse
}

export default function SearchResults({ results }: SearchResultsProps) {
  return (
    <div className="mt-6 space-y-4">
      {/* Meta Info */}
      <div className="text-sm text-gray-600">
        Found {results.total} results for "<strong>{results.query}</strong>"
      </div>

      {/* Cluster Summary */}
      {results.cluster_summary && (
        <div className="p-4 bg-blue-50 border border-blue-200 rounded-lg">
          <h3 className="font-medium text-blue-900 mb-2">Overall Summary</h3>
          <p className="text-sm text-blue-800 leading-relaxed">
            {results.cluster_summary}
          </p>
        </div>
      )}

      {/* Results */}
      <div className="space-y-4">
        {results.results.map((result, index) => (
          <div
            key={index}
            className="p-4 bg-white border border-gray-200 rounded-lg hover:shadow-md transition-shadow"
          >
            {/* Title & URL */}
            <div className="mb-2">
              <a
                href={result.url}
                target="_blank"
                rel="noopener noreferrer"
                className="text-lg font-medium text-blue-600 hover:underline"
              >
                {result.title}
              </a>
              <div className="text-xs text-gray-500 mt-1">{result.url}</div>
            </div>

            {/* Summary */}
            {result.summary && (
              <p className="text-sm text-gray-700 mb-3 leading-relaxed">
                {result.summary}
              </p>
            )}

            {/* Scores */}
            <div className="flex gap-4 text-xs text-gray-500">
              {result.bm25_score !== undefined && (
                <span>BM25: {result.bm25_score.toFixed(3)}</span>
              )}
              {result.semantic_score !== undefined && (
                <span>Semantic: {result.semantic_score.toFixed(3)}</span>
              )}
              {result.hybrid_score !== undefined && (
                <span className="font-medium">
                  Hybrid: {result.hybrid_score.toFixed(3)}
                </span>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
