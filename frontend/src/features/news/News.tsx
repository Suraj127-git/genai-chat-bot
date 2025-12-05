import { useDispatch, useSelector } from 'react-redux'
import type { RootState } from '../../store'
import { setTimeframe, fetchNews } from './slice'

export default function News() {
  const dispatch = useDispatch()
  const { summary, timeframe, loading } = useSelector((s: RootState) => s.news)

  return (
    <div className="max-w-3xl mx-auto p-4 space-y-4">
      <div className="flex gap-4 items-center">
        <select className="border p-2" value={timeframe} onChange={e => dispatch(setTimeframe(e.target.value) as any)}>
          <option>last 24 hours</option>
          <option>last 3 days</option>
          <option>last week</option>
          <option>last month</option>
        </select>
        <button className="bg-green-600 text-white px-4 py-2 rounded" onClick={() => dispatch(fetchNews() as any)}>Fetch</button>
      </div>
      <div className="prose max-w-none">
        {loading ? 'Loading...' : (summary || '')}
      </div>
    </div>
  )
}
