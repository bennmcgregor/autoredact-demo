import './App.css';
import 'bootstrap/dist/css/bootstrap.min.css';
import Button from 'react-bootstrap/Button';
import Form from 'react-bootstrap/Form';
import Spinner from 'react-bootstrap/Spinner';

function App() {
  return (
    <div className="App">
      <header className="App-header">
        <h1>
          [ REDACTED ]
        </h1>
        <p>
          AI-Powered redaction for refugee documents
        </p>
      </header>
      <div className="demo">
        <div className="file-picker">
          <Form.Group controlId="formFileLg" className="form-control w-50 file-picker">
            <Form.Label>File to Redact:</Form.Label>
            <Form.Control type="file" size="sm" />
          </Form.Group>
        </div>
        <Button variant="primary" size="sm" className="button">Redact</Button>
      </div>
      <div className="pdfs">
        <Spinner animation="border" role="status" className="spinner" style={{color: "#f5f3ed"}} size="lg"></Spinner>
      </div>

    </div>
  );
}

export default App;
