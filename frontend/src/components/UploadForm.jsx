import React from 'react'
import axios from 'axios'

export default function UploadForm({mode, onSubmitted}){
  const [loading, setLoading] = React.useState(false)
  const [exp, setExp] = React.useState(2)
  const [fps, setFps] = React.useState('')
  const [scale, setScale] = React.useState(1)
  const [numMid, setNumMid] = React.useState(6)

  const onSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    try{
      const fd = new FormData()
      let url = ''
      if(mode==='video'){
        const file = e.target.file.files[0]
        fd.append('file', file)
        fd.append('exp', exp)
        if(fps) fd.append('fps', fps)
        fd.append('scale', scale)
        url = '/api/interpolate/video'
      }else{
        const a = e.target.frame_a.files[0]
        const b = e.target.frame_b.files[0]
        fd.append('frame_a', a)
        fd.append('frame_b', b)
        fd.append('num_mid', numMid)
        fd.append('fps', 30)
        url = '/api/interpolate/frames'
      }
      const {data} = await axios.post(url, fd)
      onSubmitted(data)
    }catch(err){
      alert(err?.response?.data?.detail||err.message)
    }finally{
      setLoading(false)
    }
  }

  return (
    <form onSubmit={onSubmit} style={{border:'1px solid #ddd', padding:'1rem', borderRadius:8}}>
      {mode==='video' ? (
        <>
          <div>
            <label>Video file: <input name="file" type="file" accept="video/*" required/></label>
          </div>
          <div style={{display:'flex', gap:12, marginTop:8}}>
            <label>exp (2^exp): <input type="number" value={exp} onChange={e=>setExp(+e.target.value)} min={1} max={6}/></label>
            <label>target fps: <input type="number" value={fps} onChange={e=>setFps(e.target.value)} placeholder="inherit"/></label>
            <label>scale: <select value={scale} onChange={e=>setScale(+e.target.value)}>
              <option value={1}>1</option>
              <option value={2}>2</option>
            </select></label>
          </div>
        </>
      ) : (
        <>
          <div>
            <label>Frame A: <input name="frame_a" type="file" accept="image/*" required/></label>
          </div>
          <div>
            <label>Frame B: <input name="frame_b" type="file" accept="image/*" required/></label>
          </div>
          <div style={{display:'flex', gap:12, marginTop:8}}>
            <label># of middle frames: <input type="number" value={numMid} onChange={e=>setNumMid(+e.target.value)} min={1} max={127}/></label>
          </div>
        </>
      )}
      <button disabled={loading} style={{marginTop:12}}>{loading? 'Processing...' : 'Run RIFE'}</button>
    </form>
  )
}