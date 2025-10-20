import React from 'react'
import UploadForm from './components/UploadForm'
import JobStatus from './components/JobStatus'

export default function App(){
  const [job, setJob] = React.useState(null)
  const [mode, setMode] = React.useState('video')

  return (
    <div style={{maxWidth: 880, margin: '2rem auto', fontFamily: 'system-ui, sans-serif'}}>
      <h1>RIFE Interpolation</h1>
      <p>Upload an anime clip or two frames to generate smooth in-betweens using RIFE.</p>

      <div style={{marginBottom: '1rem'}}>
        <label>
          <input type="radio" name="mode" value="video" checked={mode==='video'} onChange={()=>setMode('video')} /> Video → Interpolated Video
        </label>
        <label style={{marginLeft: '1rem'}}>
          <input type="radio" name="mode" value="frames" checked={mode==='frames'} onChange={()=>setMode('frames')} /> Two Frames → Sequence
        </label>
      </div>

      <UploadForm mode={mode} onSubmitted={setJob} />
      {job && <JobStatus job={job} />}
    </div>
  )
}