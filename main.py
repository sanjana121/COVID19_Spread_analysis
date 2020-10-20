#inporting necesary library
from __future__ import print_function
from flask import Flask, render_template
import numpy as np
import pandas as pd
import folium

#preparing data for WORLD analysis
#loading datasets
death_df = pd.read_csv('https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_deaths_global.csv')
confirmed_df = pd.read_csv('https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv')
recovered_df = pd.read_csv('https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_recovered_global.csv')
country_df = pd.read_csv('https://raw.githubusercontent.com/CSSEGISandData/COVID-19/web-data/data/cases_country.csv')

#data cleaning- renaming the columns
country_df.columns = map(str.lower, country_df.columns)
confirmed_df.columns = map(str.lower, confirmed_df.columns)
death_df.columns = map(str.lower, death_df.columns)
recovered_df.columns = map(str.lower, recovered_df.columns)

confirmed_df = confirmed_df.rename(columns = {'province/state': 'state', 'country/region': 'country'})
recovered_df = recovered_df.rename(columns = {'province/state': 'state', 'country/region': 'country'})
death_df = death_df.rename(columns = {'province/state': 'state', 'country/region': 'country'})
country_df = country_df.rename(columns = {'country_region': 'country'})

#sorting data according to highest cases confirmed
sorted_country_df = country_df.sort_values('confirmed', ascending=False)

#to display table of top 20 affected countries
def find_top_confirmed(n = 20):
  by_country = country_df.groupby('country').sum()[['confirmed', 'deaths', 'recovered', 'active']]
  cdf = by_country.nlargest(n, 'confirmed')[['confirmed']]
  return cdf

#to pass into the flask then to html page 
cdf=find_top_confirmed()
pairs=[(country,confirmed) for country,confirmed in zip(cdf.index,cdf['confirmed'])]

#mapss
#showing these stats on the world map
w = folium.Figure(width=1018, height=500)
world_map = folium.Map(width=1018, height=500, location=[5,10], tiles='Stamen Terrain', 
                       zoom_start=2, max_zoom=6, min_zoom=2).add_to(w)

for i in range(len(confirmed_df)):
    folium.Circle(location=[confirmed_df.iloc[i]['lat'],confirmed_df.iloc[i]['long']],
                 fill = True,
                 radius = (int((np.log(confirmed_df.iloc[i,-1]+1.00001))) + 0.2)*50000,
                 fill_color = 'blue',
                 color = 'red',
                 tooltip= "<div style='margin: 0; background-color: black; color: white;'>"+
                            "<h4 style='text-align:center;font-weight: bold'>"+confirmed_df.iloc[i]['country'] + "</h4>"
                            "<hr style='margin:10px;color: white;'>"+
                            "<ul style='color: white;;list-style-type:circle;align-item:left;padding-left:20px;padding-right:20px'>"+
                                "<li>Confirmed: "+str(confirmed_df.iloc[i,-1])+"</li>"+
                                "<li>Deaths:   "+str(death_df.iloc[i,-1])+"</li>"+
                                "<li>Death Rate: "+ str(np.round(death_df.iloc[i,-1]/(confirmed_df.iloc[i,-1]+1.00001)*100,2))+ "</li>"+
                            "</ul></div>",
                 ).add_to(world_map)
world_map
world=world_map._repr_html_()

#preparing data for INDIA stats
#importing csv files
states_df = pd.read_csv('CLEAN_INDIA.csv')
cord_df = pd.read_csv('CLEAN_STATES.csv')
data = pd.read_csv('Data.csv')

#organizing Data
data = data.rename(columns = {'State Name': 'State'})
cord_df = cord_df.sort_values(by = ['State'], ascending=False)
states_df['State'] = states_df['State'].str.upper() 
data['State'] = data['State'].str.upper() 

#merging 3 csv into one
final_india_df = pd.merge(states_df, cord_df,  on="State")
final_india_df.drop(["Deaths"], axis=1, inplace=True)
final_india_df = pd.merge(final_india_df, data, on="State")
final_india_df

#to display table of top 20 affected states
def top_confirmed(n = 20):
  by_country = final_india_df.groupby('State').sum()[['Cases', 'Deaths']]
  cdf2 = by_country.nlargest(n, 'Cases')[['Cases']]
  return cdf2

#to pass into the flask then to html page 
cdf2 = top_confirmed()
pairs2=[(State, Cases) for State,Cases in zip(cdf2.index,cdf2['Cases'])]

#showing these stats on the indian map
f = folium.Figure(width=1018, height=700)
india_map = folium.Map(width=1018, height=700, location=[20,81], tiles='Stamen Terrain', 
                       zoom_start=5, max_zoom=6, min_zoom=2).add_to(f)

for i in range(len(final_india_df)):
    folium.Circle(location=[final_india_df.iloc[i]['lat'],final_india_df.iloc[i]['long']],
                 fill = True,
                 radius = (int((np.log(final_india_df.iloc[i]['Cases']+1.00001))) + 0.2)*20000,
                 fill_color = 'blue',
                 color = 'red',
                 tooltip= "<div style='margin: 0; background-color: black; color: white;'>"+
                            "<h4 style='text-align:center;font-weight: bold'>"+final_india_df.iloc[i]['State'] + "</h4>"
                            "<hr style='margin:10px;color: white;'>"+
                            "<ul style='color: white;;list-style-type:circle;align-item:left;padding-left:20px;padding-right:20px'>"+
                                "<li>Confirmed: "+str(final_india_df.iloc[i]['Cases'])+"</li>"+
                                "<li>Active:    "+str(final_india_df.iloc[i]['Active'])+"</li>"+
                                "<li>Recovered:  "+str(final_india_df.iloc[i]['Recovered'])+"</li>"+
                                "<li>Deaths:   "+str(final_india_df.iloc[i]['Deaths'])+"</li>"+
                            "</ul></div>",
                 ).add_to(india_map)
india_map
india = india_map._repr_html_()

#calling flask app 
app=Flask(__name__)
@app.route('/')
def home():
    return render_template("try.html", table=[cdf, cdf2], cmap=[world,india], pairs=[pairs, pairs2])

if __name__=="__main__":
    app.run(debug=False)
