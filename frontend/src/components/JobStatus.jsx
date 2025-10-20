import React from 'react'
import axios from 'axios'

export default function JobStatus({job: initial}){
  const [job, setJob] = React.useState(initial)

  React.useEffect(()=>{
    if(!job?.id) return
    if(job.status==='done' || job.status==='error') return
    const t = setInterval(async ()=>{
      const {data} = await axios.get(`/api/jobs/${job.id}`)
      setJob(data)
    }, 1000)
    return ()=>clearInterval(t)
  }, [job?.id, job?.status])

  return (
    <div style={{marginTop:16, padding:12, border:'1px dashed #ccc', borderRadius:8}}>
      <div><b>Job:</b> {job.id}</div>
      <div><b>Status:</b> {job.status}</div>
      {job.error && <div style={{color:'crimson'}}>{job.error}</div>}
      {job.output_url && (
        <p>
          <a href={job.output_url} download>Download result</a>
        </p>
      )}
    </div>
  )
}