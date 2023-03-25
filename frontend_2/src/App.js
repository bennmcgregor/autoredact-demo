import './App.css';
import 'bootstrap/dist/css/bootstrap.min.css';
import Button from 'react-bootstrap/Button';
import Form from 'react-bootstrap/Form';
import Spinner from 'react-bootstrap/Spinner';
import { useState } from 'react';
import { Switch } from 'antd';

import dataPDF from "./data.pdf";
import redactedPDF from "./redacted.pdf";
import Graphs from './Graphs';

function App() {

  const [uploaded, setUploaded] = useState(false);
  const [redacted, setRedacted] = useState(false);
  const [loadingLeft, setLoadingLeft] = useState(false);
  const [loadingRight, setLoadingRight] = useState(false);
  const [isToggled, setIsToggled] = useState(true);

  const HandleSubmit = (event) => {

    setLoadingLeft(true);
    setLoadingRight(true);

    const formData = new FormData();
    formData.append('file', event.target.file.files[0]);

    fetch('http://127.0.0.1:5000/upload', {
      method: 'POST',
      body: formData
      })
      .then(() => {
        setLoadingLeft(false);
        setUploaded(true);

        fetch('http://127.0.0.1:5000/redactor', {
          method: 'POST',
          body: formData
        })
        .then(() => {
          setLoadingRight(false);
          setRedacted(true);

          fetch('http://127.0.0.1:5000/getstats', {
            method: 'POST',
            body: formData
          })
          .then(() => console.log("Third req done"));

        });
      });
  };

  const Clear = () => {
    setUploaded(false);
    setRedacted(false);
  }

  const onChangeToggle = (checked) => {
    console.log(`switch to ${checked}`);
    setIsToggled(!isToggled);
  };

  return (
    <div className="App">
      <Switch defaultChecked onChange={onChangeToggle} className="toggle" style={{backgroundColor: isToggled ? '#EDF7F6' : '#3E5C76'}}/>
      <header className="App-header">
      
        <h1>
          [ REDACTED ]
        </h1>
        <p>
          AI-Powered redaction for refugee documents
        </p>
      </header>
   
      {isToggled ? <>
      <div className="demo">
        <div className="file-picker">
          <iframe name="dummyframe" title="dummyframe" id="dummyframe" style={{display: "none"}}></iframe>
          <Form onSubmit={HandleSubmit} onChange={Clear} target="dummyframe">
            <Form.Group className="form-control w-50 file-picker">
              <Form.Label>File to Redact:</Form.Label>
              <Form.Control type="file" id="file" name="file" size="sm" />
              <Button type="submit" variant="primary" size="sm" className="button">Redact</Button>
            </Form.Group>
          </Form>
        </div>
      </div>
      <div className="pdfs">
        <div className="column">
          {loadingLeft && <Spinner className="spinner" animation="border" role="status" style={{color: "#f5f3ed"}} size="lg"></Spinner>}
          {uploaded && <iframe src={`${dataPDF}#view=fitH`} title="Original" height="90%" width="90%" /> }
        </div>
        <div className="column">
          {loadingRight && <Spinner className="spinner" animation="border" role="status" style={{color: "#f5f3ed"}} size="lg"></Spinner>}
          {redacted && <iframe src={`${redactedPDF}#view=fitH`} title="Redacted" height="90%" width="90%" /> }
        </div>
      </div>
      </>:<div className='graphs'><Graphs></Graphs></div>}

    </div>
  );
}

export default App;
