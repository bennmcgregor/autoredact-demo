import json
from flask import Flask, request
from docx import Document
from pathlib import Path
import subprocess

app = Flask(__name__)
	
@app.route('/redactor', methods = ['POST'])
def upload_file():
   if request.method == 'POST':
      f = request.files['file']
      doc = Document(f)
      paras = []
      for i, p in enumerate(doc.paragraphs):
          paras.append({
             "i": i,
             "text": p.text
          })

      with open("data.jsonl", "w") as output:
        while len(paras) > 0:
            para = paras.pop(0)
            output.write(json.dumps(para) + "\n")
      
      subprocess.run(["python", "-m", "spacy", "apply", "./models/en_trf_mlt_label_v4_1000000/model-last", "data.jsonl", "output.spacy"])

      return 'file uploaded successfully'
		
if __name__ == '__main__':
   app.run(debug = True)