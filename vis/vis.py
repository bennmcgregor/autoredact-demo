import pandas as pd
import numpy as np
import plotly
import plotly.express as px
import plotly.graph_objs as go

df = pd.read_csv('Training Results - Sheet1.csv')
df.drop(df.index[0])
df.columns = df.iloc[0]
df_labels = df.copy()


df_labels.dropna(subset=['Label'], inplace=True)

new_table = pd.DataFrame(columns=['Model Name', 'Label', 'Score', 'Score Type'])

row_id = 0
for index, row in df_labels.iloc[:,0:5].iterrows():
    if(index != 0):
        new_table.loc[row_id] = [row['Model Name'], row['Label'], row['P'], 'P']
        row_id += 1
        new_table.loc[row_id] = [row['Model Name'], row['Label'], row['R'], 'R']
        row_id += 1
        new_table.loc[row_id] = [row['Model Name'], row['Label'], row['F'], 'F']
        row_id += 1

def figures_to_html(figs, filename="dashboard.html"):
    with open(filename, 'w', encoding="utf-8") as dashboard:
        dashboard.write("<html><head></head><body>" + "\n")
        for fig in figs:
            inner_html = fig.to_html().split('<body>')[1].split('</body>')[0]
            dashboard.write(inner_html)
        dashboard.write("</body></html>" + "\n")

labels = []
color_discrete_sequence = []
for i in range(len(new_table)//3//3):
    labels.extend(["REDACTED", "ID", "CONTEXT"])
    color_discrete_sequence = ["#D8FAFD", '#3E5C76', '#748CAB']

print(new_table)
new_table["Score"] = new_table["Score"].astype(float)
print(new_table.dtypes)



# fig1 = px.bar(new_table.loc[new_table['Label'] == "REDACTED"], x="Model Name", y="Score",
#              color="Score Type", barmode = 'group', color_discrete_sequence=color_discrete_sequence, title="P, R, and F Scores for REDACTED")

# fig2 = px.bar(new_table.loc[new_table['Label'] == "ID"], x="Model Name", y="Score",
#              color="Score Type", barmode = 'group', color_discrete_sequence=color_discrete_sequence,  title="P, R, and F Scores for ID")

# fig3 = px.bar(new_table.loc[new_table['Label'] == "CONTEXT"], x="Model Name", y="Score",
#              color="Score Type", barmode = 'group', color_discrete_sequence=color_discrete_sequence,  title="P, R, and F Scores for CONTEXT")

# fig4 = px.bar(new_table, x="Model Name", y="Score",
#              color="Score Type", barmode = 'group', facet_col="Label", color_discrete_sequence=color_discrete_sequence)

# fig5 = px.bar(new_table, x="Model Name", y="Score",
#              color="Score Type", barmode = 'group', hover_data=["Model Name", "Score", "Score Type", "Label"],color_discrete_sequence=color_discrete_sequence,  title="P, R, and F Scores for REDACTED, ID, and CONTEXT" )

#fig5.update_traces(text=labels, insidetextanchor = "middle", textangle=0)

#fig5.update_traces(text='53WW',selector=)




figures_to_html([fig1, fig2, fig3, fig4, fig5])

# plot_json = []

# plot_json.extend()
# plot_json.extend(plotly.io.to_json(fig5, pretty=True))

print(plotly.io.to_json(fig4, pretty=True))
