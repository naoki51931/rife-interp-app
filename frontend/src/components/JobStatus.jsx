import React from 'react'
import axios from 'axios'

export default function JobStatus({ job: initial }) {
  const [job, setJob] = React.useState(initial)

  React.useEffect(() => {
    if (!job?.id) return
    if (job.status === 'done' || job.status === 'error') return

    const t = setInterval(async () => {
      try {
        const { data } = await axios.get(`/api/jobs/${job.id}`)
        setJob(data)
      } catch (err) {
        console.error("JobStatus polling error:", err)
      }
    }, 1000)

    return () => clearInterval(t)
  }, [job?.id, job?.status])

  return (
    <div style={{
      marginTop: 16,
      padding: 12,
      border: '1px dashed #ccc',
      borderRadius: 8,
      background: job.status === 'error' ? '#ffeeee' : '#fafafa'
    }}>
      <div><b>Job:</b> {job.id}</div>
      <div><b>Status:</b> {job.status}</div>

      {job.error && (
        <div style={{ color: 'crimson', marginTop: 8 }}>
          {job.error}
        </div>
      )}

      {job.status === 'done' && (
        <div style={{ marginTop: 10 }}>
          {job.output_url && (
            <p>
              🎬 <a href={job.output_url} download>Download video (MP4)</a>
            </p>
          )}
          {/* もし中間フレームZIPがあるなら */}
          <p>
            🖼️ <a href={`/api/download_frames/${job.id}`} download>Download frames (ZIP)</a>
          </p>
        </div>
      )}
    </div>
  )
}

