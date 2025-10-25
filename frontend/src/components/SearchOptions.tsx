interface SearchOptionsProps {
  topK: number
  setTopK: (value: number) => void
  summarize: boolean
  setSummarize: (value: boolean) => void
  clusterSummary: boolean
  setClusterSummary: (value: boolean) => void
  useMMR: boolean
  setUseMMR: (value: boolean) => void
}

export default function SearchOptions({
  topK,
  setTopK,
  summarize,
  setSummarize,
  clusterSummary,
  setClusterSummary,
  useMMR,
  setUseMMR,
}: SearchOptionsProps) {
  return (
    <div className="mt-4 p-4 bg-white border border-gray-200 rounded-lg">
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Top K */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Results: {topK}
          </label>
          <input
            type="range"
            min="1"
            max="20"
            value={topK}
            onChange={(e) => setTopK(parseInt(e.target.value))}
            className="w-full"
          />
        </div>

        {/* Summarize */}
        <div className="flex items-center">
          <input
            type="checkbox"
            id="summarize"
            checked={summarize}
            onChange={(e) => setSummarize(e.target.checked)}
            className="w-4 h-4 text-blue-600 rounded focus:ring-blue-500"
          />
          <label htmlFor="summarize" className="ml-2 text-sm font-medium text-gray-700">
            Per-doc summaries
          </label>
        </div>

        {/* Cluster Summary */}
        <div className="flex items-center">
          <input
            type="checkbox"
            id="cluster"
            checked={clusterSummary}
            onChange={(e) => setClusterSummary(e.target.checked)}
            className="w-4 h-4 text-blue-600 rounded focus:ring-blue-500"
          />
          <label htmlFor="cluster" className="ml-2 text-sm font-medium text-gray-700">
            Cluster summary
          </label>
        </div>

        {/* MMR */}
        <div className="flex items-center">
          <input
            type="checkbox"
            id="mmr"
            checked={useMMR}
            onChange={(e) => setUseMMR(e.target.checked)}
            className="w-4 h-4 text-blue-600 rounded focus:ring-blue-500"
          />
          <label htmlFor="mmr" className="ml-2 text-sm font-medium text-gray-700">
            MMR diversity
          </label>
        </div>
      </div>
    </div>
  )
}
