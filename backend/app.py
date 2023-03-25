import json
from flask import Flask, request, render_template
from docx import Document
from pathlib import Path
import subprocess
from docx import Document
import spacy
from spacy.tokens import DocBin
from docx2pdf import convert
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

class redact_index:
    def __init__(self, start, end):
        self.start = start
        self.end = end
        self.count = 0

class redact_token:
    def __init__(self, text, is_r):
        self.text = text
        self.is_redacted = is_r


def redact_doc():
   nlp = spacy.blank("en")
   doc_bin = DocBin().from_disk("output.spacy")
   docs = list(doc_bin.get_docs(nlp.vocab))

   redact_paras = {}

   for i,doc in enumerate(docs):
      if doc.spans:
         for t in doc.spans['sc']:
               if(not (i in redact_paras)):
                  redact_paras[i] = []
               redact_paras[i].append(t)

   data_doc = Document("../frontend_2/src/data.docx")


   for i in redact_paras:
      redact_indices = []
      # print(i)
      para_doc = nlp(data_doc.paragraphs[i].text)
      tokens = [redact_token(x, False) for x in para_doc]
      spaces = [x.whitespace_ for x in para_doc]
      #tokens = re.findall(r"[\w']+|[.,!?;]", data_doc.paragraphs[i].text)
      # print(tokens)
      for span_r in redact_paras[i]:
         start = span_r.start
         while start < span_r.end:
               # tokens[start].text = "X" * len(tokens[start].text)
               tokens[start].is_redacted = True
               start += 1
      output = ""
      for token_i in range(len(tokens)):
         if(tokens[token_i].is_redacted):
               # if(len(output) == 0):
               #     redact_i = redact_index(len(output), len(output) + len(tokens[token_i].text))
               # else:
               redact_i = redact_index(len(output), len(output) + len(tokens[token_i].text))
               redact_indices.append(redact_i)
         output += f'{tokens[token_i].text}{spaces[token_i]}'
      # # out_tokens = nlp(output)
      # print(out_tokens)
      out_ic = 0
      recently_redacted = False
      for run_i in range(len(data_doc.paragraphs[i].runs)):
         run_text = data_doc.paragraphs[i].runs[run_i].text
         # run_tokens = nlp(run_text)
         # print(run_tokens)
         data_doc.paragraphs[i].runs[run_i].text = ""
         for rt_i in range(len(run_text)):
               # if out_ic < len(tokens):
               if run_text[rt_i]:
                  if len(redact_indices) and redact_indices[0].start <= out_ic and redact_indices[0].end > out_ic:
                     redact_indices[0].count += 1
                     print(redact_indices[0].start, redact_indices[0].end, redact_indices[0].count)
                     print(redact_indices[0].count)
                     print(redact_indices[0].end - redact_indices[0].start)
                     if(redact_indices[0].count == redact_indices[0].end - redact_indices[0].start):
                           print(recently_redacted)
                           if(not recently_redacted):
                              data_doc.paragraphs[i].runs[run_i].text += "XXXX"
                           redact_indices.pop(0)
                           recently_redacted = True
                  else:
                     data_doc.paragraphs[i].runs[run_i].text += output[out_ic]
                     recently_redacted = False
                  out_ic += 1

   # for i in redact_paras:
   #    para_doc = nlp(data_doc.paragraphs[i].text)
   #    tokens = [x for x in para_doc]
   #    spaces = [x.whitespace_ for x in para_doc]
   #    #tokens = re.findall(r"[\w']+|[.,!?;]", data_doc.paragraphs[i].text)
   #    # print(tokens)
   #    for span_r in redact_paras[i]:
   #       start = span_r.start
   #       while start < span_r.end:
   #             tokens[start] = "XXXX"
   #             start += 1
   #    output = ""
   #    for token_i in range(len(tokens)):
   #       output += f'{tokens[token_i]}{spaces[token_i]}'
   #    data_doc.paragraphs[i].text = output
   data_doc.save('../frontend_2/src/redacted.docx')
   convert("../frontend_2/src/redacted.docx", "../frontend_2/src/redacted.pdf")

# test_bin = DocBin().from_disk("../data/paired_data/test_data.spacy")
# tests = list(test_bin.get_docs(nlp.vocab))
# print("HIII")
# for i,test in enumerate(tests):
#         #print(test)
#         print(test.spans["sc"])
	
@app.route('/')
def home_page():
   return render_template("index.html")

@app.route('/upload', methods = ['POST'])
def upload_file():
    if request.method == 'POST':
      f = request.files['file']

      f.save('../frontend_2/src/data.docx')
      convert('../frontend_2/src/data.docx', '../frontend_2/src/data.pdf')

      return render_template("index.html")

@app.route('/redactor', methods = ['POST'])
def redact():
   if request.method == 'POST':
      f = request.files['file']

      doc = Document(f)
      paras = []

      """for i,t in enumerate(doc.tables):
          for r in t.rows:
              for c in r.cells:
                  paras.append({
                     "t": i,
                     "text": c.text
                  })"""
      for i, p in enumerate(doc.paragraphs):
          paras.append({
             "i": i,
             "text": p.text
          })


      with open("data.jsonl", "w") as output:
        while len(paras) > 0:
            para = paras.pop(0)
            output.write(json.dumps(para) + "\n")
      
      subprocess.run(["python", "-m", "spacy", "apply", "./models/en_trf_docs_v5_bs_2000_orig/model-best", "data.jsonl", "output.spacy", "--force"])

      redact_doc()

      return render_template("index.html")
   

import pandas as pd
import numpy as np
import plotly
import plotly.express as px
import plotly.graph_objs as go
import json

def figures_to_html(figs):
   #  with open(filename, 'w', encoding="utf-8") as dashboard:
      #   dashboard.write("<html><head></head><body>" + "\n")
      html = []
      for fig in figs:
         inner_html = fig.to_html().split('<body>')[1].split('</body>')[0]
         html.append(inner_html)
      return html
      #   dashboard.write("</body></html>" + "\n")

@app.route('/graphs', methods = ['POST', 'GET'])
def graphs():
   df = pd.read_csv('Training Results - Sheet1.csv')
   df.drop(df.index[0])
   # print(df)
   # print(df.loc[[0]])
   # df.columns = df.loc[[0]]
   df.columns = df.iloc[0]
   # df.columns = df.iloc[1]
   # # df.rename(columns=df.iloc[1])
   # print(df.columns)
   # print(df.iloc[:,0])
   # print(df.iloc[:,1])
   df_labels = df.copy()


   df_labels.dropna(subset=['Label'], inplace=True)

   new_table = pd.DataFrame(columns=['Model Name', 'Label', 'Score', 'Score Type', 'Params'])
   # new_table.loc[0] = ['Model Name', 'Label', 'Score', 'Score Type']
   # print(new_table)
   row_id = 0
   for index, row in df_labels.iloc[:,0:6].iterrows():
      # print(row['Model Name'])
      # print(row['Label'])
      if(index != 0):
         new_table.loc[row_id] = [row['Model Name'], row['Label'], row['P'], 'P', row["Parameters (differerent from default)"]]
         row_id += 1
         new_table.loc[row_id] = [row['Model Name'], row['Label'], row['R'], 'R', row["Parameters (differerent from default)"]]
         row_id += 1
         new_table.loc[row_id] = [row['Model Name'], row['Label'], row['F'], 'F', row["Parameters (differerent from default)"]]
         row_id += 1


   # print(new_table)
      # print(row[0]: row[1])
   # 


   # test = px.data.iris()
   # print(test)

   labels = []
   color_discrete_sequence = []
   for i in range(len(new_table)//3//3):
      labels.extend(["REDACTED", "ID", "CONTEXT"])
      color_discrete_sequence = ["#D8FAFD", '#3E5C76', '#5c6f87']

   print(new_table)
   new_table["Score"] = new_table["Score"].astype(float)
   print(new_table.dtypes)



   fig1 = px.bar(new_table.loc[new_table['Label'] == "REDACTED"], x="Model Name", y="Score",
             color="Score Type", barmode = 'group', hover_data=["Model Name", "Score", "Score Type", "Label", "Params"], color_discrete_sequence=color_discrete_sequence, title="P, R, and F Scores for REDACTED")
   #yaxis={'categoryorder':'total ascending'})

   # data = [go.Bar(
   #    x = new_table["Model Name"],
   #    y = new_table["Score"]
   # )]
   # fig = go.Figure(data=data)
   # fig.show()

   # fig1.update_layout(
   #     yaxis={
   #         'range':[0.0,1.0]
   #     })

   # fig1.show()

   fig2 = px.bar(new_table.loc[new_table['Label'] == "ID"], x="Model Name", y="Score",
               color="Score Type", barmode = 'group', hover_data=["Model Name", "Score", "Score Type", "Label", "Params"], color_discrete_sequence=color_discrete_sequence,  title="P, R, and F Scores for ID")

   fig3 = px.bar(new_table.loc[new_table['Label'] == "CONTEXT"], x="Model Name", y="Score",
               color="Score Type", barmode = 'group', hover_data=["Model Name", "Score", "Score Type", "Label", "Params"], color_discrete_sequence=color_discrete_sequence,  title="P, R, and F Scores for CONTEXT")
   # color_discrete_map={
   #                 "P": "red",
   #                 "R": "green",
   #                 "F": "blue",
   #                 "REDACTED": "goldenrod",
   #                 "ID": "magenta",
   #                 "CONTEXT": "orange"},

   fig4 = px.bar(new_table, x="Model Name", y="Score",
               color="Score Type", barmode = 'group', facet_col="Label",hover_data=["Model Name", "Score", "Score Type", "Label", "Params"], color_discrete_sequence=color_discrete_sequence, title="P, R, and F Scores for REDACTED, ID, and CONTEXT")




   fig5 = px.bar(new_table, x="Model Name", y="Score",
             color="Score Type", barmode = 'group', hover_data=["Model Name", "Score", "Score Type", "Label", "Params"],color_discrete_sequence=color_discrete_sequence,  title="P, R, and F Scores for REDACTED, ID, and CONTEXT" )

   custom_labels = ["REDACTED", "ID", "CONTEXT"]


   fig5.update_traces(text=labels, insidetextanchor = "middle", textangle=0)


   # fig5.update_traces(text='53WW',selector=)



   plot_json = []

   # plot_json.append(plotly.io.to_json(fig4, pretty=True))
   plot_json.append(plotly.io.to_json(fig5, pretty=False))
   plot_json.append(plotly.io.to_json(fig4, pretty=False))
   plot_json.append(plotly.io.to_json(fig1, pretty=False))
   plot_json.append(plotly.io.to_json(fig2, pretty=False))
   plot_json.append(plotly.io.to_json(fig3, pretty=False))
   # for x in plot_json:
   #     print(x)

   # plot_html = figures_to_html([fig4, fig5])

   return json.dumps(plot_json)

   # print(df_labels)


   # print(df.to_string()) 
         
if __name__ == '__main__':
   app.run(debug = True)