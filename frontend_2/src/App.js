import './App.css';
import 'bootstrap/dist/css/bootstrap.min.css';
import Button from 'react-bootstrap/Button';
import Form from 'react-bootstrap/Form';
import Spinner from 'react-bootstrap/Spinner';
import Table from 'react-bootstrap/Table';
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
  const [prfEmptyReady, setPrfEmptyReady] = useState(false);
  const [prfReady, setPrfReady] = useState(false);
  const [prfNums, setPrfNums] = useState({});

  const HandleSubmit = (event) => {

    setLoadingLeft(true);
    setLoadingRight(true);
    setPrfEmptyReady(true);

    const formData = new FormData();
    formData.append('filename', event.target.file.files[0].name);

    fetch('http://127.0.0.1:5000/upload', {
      method: 'POST',
      body: formData
      })
      .then(() => {
        setLoadingLeft(false);
        setUploaded(true);
      });
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
        .then((response) => response.json())
        .then((res) => {
          // const res = response.json();
          setPrfNums(res);
          console.log(res);
          setPrfReady(true);
        });
      });
  };

  const Clear = () => {
    setUploaded(false);
    setRedacted(false);
    setPrfReady(false);
    setPrfEmptyReady(false);
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
        { redacted && <div className="PRF">
          <Table bordered hover>
          <thead>
            <tr>
              <th></th>
              <th>P</th>
              <th>R</th>
              <th>F</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td className='left-header'>REDACTED</td>
              {prfReady? <td>{prfNums.REDACTED.P}</td> : <td></td>}
              {prfReady? <td>{prfNums.REDACTED.R}</td> : <td></td>}
              {prfReady? <td>{prfNums.REDACTED.F}</td> : <td></td>}
            </tr>
            <tr>
              <td className='left-header'>ID</td>
              {prfReady? <td>{prfNums.ID.P}</td> : <td></td>}
              {prfReady? <td>{prfNums.ID.R}</td> : <td></td>}
              {prfReady? <td>{prfNums.ID.F}</td> : <td></td>}
            </tr>
            <tr>
              <td className='left-header'>CONTEXT</td>
              {prfReady? <td>{prfNums.CONTEXT.P}</td> : <td></td>}
              {prfReady? <td>{prfNums.CONTEXT.R}</td> : <td></td>}
              {prfReady? <td>{prfNums.CONTEXT.F}</td> : <td></td>}
            </tr>
          </tbody>
        </Table>
      </div> }

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
