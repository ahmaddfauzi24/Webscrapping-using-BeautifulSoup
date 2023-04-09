from flask import Flask, render_template
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
from io import BytesIO
import base64
from bs4 import BeautifulSoup 
import requests

#don't change this
matplotlib.use('Agg')
app = Flask(__name__) #do not change this

#insert the scrapping here
url_get = requests.get('https://www.exchange-rates.org/history/IDR/USD/T')
soup = BeautifulSoup(url_get.content,"html.parser")

#find your right key here
table = soup.find('tbody')
row = table.find_all('a', attrs={'class':'n'})

row_length = len(row)

temp = [] #initiating a list 

for i in range(0, row_length):
    
    #get date 
    date = table.find_all('a', attrs={'class':'n'})[i].text
    
    #get kurs
    kurs = table.find_all('span', attrs={'class':'w'})[i].text
    kurs = kurs.strip() #to remove excess white space
    
    temp.append((date,kurs)) 

temp = temp[::-1]

#change into dataframe
df = pd.DataFrame(temp,columns=['Date','Kurs'])

#insert data wrangling here
# to get rid of the string '$'
df['Kurs'] = df['Kurs'].str.replace('$','')

# to get rid of the string '1 ='
df['Kurs'] = df['Kurs'].str.replace('1 =','')

# to get rid of the string 'Rp'
df['Kurs'] = df['Kurs'].str.replace('Rp','')

# to get rid of the string ','
df['Kurs'] = df['Kurs'].str.replace(',','')

# to change the data type in columns date to datetime64
df['Date'] = df['Date'].astype('datetime64')

# to change the data type in columns kurs to float
df['Kurs'] = df['Kurs'].astype('float')

# make new column to get contain month
df['Month'] = df['Date'].dt.to_period('M')

# using groupby to get mean in every month
df_mean = df.groupby('Month').mean().round(2)

#end of data wranggling 

@app.route("/")
def index(): 
	
	card_data = f'{df["Kurs"].mean().round(2)}' #be careful with the " and ' 

	# generate plot
	ax = df_mean.plot(figsize = (12,6)) 
	
	# Rendering plot
	# Do not change this
	figfile = BytesIO()
	plt.savefig(figfile, format='png', transparent=True)
	figfile.seek(0)
	figdata_png = base64.b64encode(figfile.getvalue())
	plot_result = str(figdata_png)[2:-1]

	# render to html
	return render_template('index.html',
		card_data = card_data, 
		plot_result=plot_result
		)


if __name__ == "__main__": 
    app.run(debug=True)