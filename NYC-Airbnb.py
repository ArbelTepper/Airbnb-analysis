#!/usr/bin/env python
# coding: utf-8

# ### Importing libraries
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.patches import Patch
from matplotlib.lines import Line2D

import folium
from folium import Choropleth, Circle, Marker
from folium.plugins import HeatMap, MarkerCluster


#Importing the downloaded map file
nyc = gpd.read_file(r'Data\shape files\nyad.shp')
print(nyc.crs)


#Importing the data file
Airbnb_df = pd.read_csv ("Data\AB_NYC_2019.csv", index_col = 'id')
Airbnb_geo = gpd.GeoDataFrame(Airbnb_df, geometry=gpd.points_from_xy(Airbnb_df.longitude, Airbnb_df.latitude))
Airbnb_geo = Airbnb_geo.set_crs('epsg:4326')
Airbnb_geo = Airbnb_geo.to_crs(epsg=2263)


#Plotting the data 
sns.set_style("white")
ax = nyc.plot(figsize = (15,15), color = 'gainsboro', edgecolor = 'black')
ax.set_axis_off()

plt.title("Airbnb locations in New York City (2019)", size = 30)
Airbnb_geo.plot(markersize=0.1, ax=ax)

plt.savefig ("NYC_locations", dpi=300, bbox_inches ="tight")
plt.show()


#Number of apartments by borough
sum = Airbnb_geo.groupby('neighbourhood_group').count().sort_values('host_id')# count the values for each borough and sort
sns.set_style("darkgrid")
plt.figure(figsize=(9,7))
plt.title ("Number of Airbnb apartments by borough (2019)", size = 21, fontname = "Comic Sans MS")

bar = sns.barplot (x=sum.index, y=sum.host_id, palette = "cool_r")

yticks = [* range(0,20001,5000)] # making a list for y-ticks. '[* range(start,stop,steps)]' converts range to list
bar.set_yticks([500,1000] + yticks) # adding values to the list and setting y-ticks list as y-ricks of the plot.
bar.set(xlabel= '', ylabel='') #removing auto generated x and y axis labels

plt.savefig ("Results\number_of_apts.png",bbox_inches ="tight", dpi=300)
plt.show()


#Top 100 most expensive apartments per night for each borough on one map, size of dot indicates cost, with legend, different color for each borough

#checking for missing price data
missing_values_count = Airbnb_geo.price.isnull().sum() 

#inserting values to geodataframes by borough name, sorting peices (descending), and taking the top 100
Brooklyn = Airbnb_geo.loc[Airbnb_geo.neighbourhood_group == 'Brooklyn'].sort_values('price', ascending=False).head(100)
Manhattan = Airbnb_geo.loc[Airbnb_geo.neighbourhood_group == 'Manhattan'].sort_values('price', ascending=False).head(100)
Queens = Airbnb_geo.loc[Airbnb_geo.neighbourhood_group == 'Queens'].sort_values('price', ascending=False).head(100)
Staten_Island = Airbnb_geo.loc[Airbnb_geo.neighbourhood_group == 'Staten Island'].sort_values('price', ascending=False).head(100)
Bronx = Airbnb_geo.loc[Airbnb_geo.neighbourhood_group == 'Bronx'].sort_values('price', ascending=False).head(100)

sns.set_style("darkgrid")

#reintroducing the previously made nyc map
ax = nyc.plot(figsize = (14,14), color = 'gainsboro', edgecolor = 'black')

#the function's input is a pandas dataseries of prices and the function's output is a list of marker sizes to match each plotted entry.
def size (series): 
    list = []
    
    for row in range(-1,len(series),1): #loop - starts from row 0, ends with the last row, 1 line per itiration
        if (series.values[row] < 701): #condition to be met
            list.append (40) #append a number to the list. the number represents the marker size of the plotted data.
        elif ((series.values[row] > 700) and (series.values[row] < 3001)):
             list.append (400)
        else:
            list.append (1400)

    return list #
    

#plotting data using the "size" fuction, including edge color
ax1 = Brooklyn.plot(markersize=size(Brooklyn.price), ax=ax, color='red', alpha = 0.5, marker = 'o', edgecolors='black') 
ax2 = Manhattan.plot(markersize=size(Manhattan.price), ax=ax, color='green', alpha = 0.5, marker = 'o', edgecolors='black')
ax3 = Queens.plot(markersize=size(Queens.price), ax=ax, color='blue', alpha = 0.5, marker = 'o', edgecolors='black')
ax4 = Staten_Island.plot(markersize=size(Staten_Island.price), ax=ax, color='purple', alpha = 0.5, marker = 'o', edgecolors='black')
ax5 = Bronx.plot(markersize=size(Bronx.price), ax=ax, color='orange', alpha = 0.5, marker = 'o', edgecolors='black')



legend_elements = [Patch(facecolor='red',label='Brooklyn'), #creating a list of shape objects that contain color and label
                   Patch(facecolor='green',label='Manhattan'),
                   Patch(facecolor='blue',label='Queens'),
                   Patch(facecolor='purple',label='Staten Island'),
                   Patch(facecolor='orange',label='Bronx'),
                   
                   Line2D([0], [0], marker='o', color='white', label='105 - 700 $', markerfacecolor='black', markersize=8),
                   Line2D([0], [0], marker='o', color='white', label='701 - 3000 $', markerfacecolor='black', markersize=19),
                   Line2D([0], [0], marker='o', color='white', label='3001 - 10000 $', markerfacecolor='black', markersize=32)
                   ]

#creating the legend
plt.legend(title = "Boroughs and price ranges " ,title_fontsize=19,  handles=legend_elements, loc='upper left', fontsize=18)

plt.title ("Top 100 most expensive Airbnb apartments per night, in each borough (2019)", fontname = "Calibri", size = 25)

plt.tick_params(left = False, labelleft = False , labelbottom = False, bottom = False) # remove ticks and axis labels

plt.savefig("Results\Top_100.png",bbox_inches ="tight", dpi=300)
plt.show()


# Using the Folium library to visualize the data above interactivly
#Heatmap
m_1 = folium.Map(location=[40.71427, -74.00597],tiles='openstreetmap', zoom_start=10)

HeatMap(data=Airbnb_geo[['latitude', 'longitude']], radius=12).add_to(m_1)

m_1.save("Results\Heatmap.html")

#Markercluster
m_2 = folium.Map(location=[40.71427, -74.00597],tiles='cartodbpositron', zoom_start=10)

mc = MarkerCluster()
for idx, row in Airbnb_geo.iterrows():
        mc.add_child(Marker([row['latitude'], row['longitude']]))
m_2.add_child(mc)

m_2.save("Results\MarkerCluster.html")

#Choropleth map
boroughs = gpd.read_file(r'shape files\geo_export_ac60301a-5a5b-46ae-91c9-53608c1b0201.shp') #getting shp file with boroughs
boroughs = boroughs[["boro_name", "geometry"]].set_index("boro_name")
boroughs.index.rename('borough', inplace = True) #renaming the index column
Airbnb_geo.rename(columns = {'neighbourhood_group':'borough'}, inplace = True) #renaming a column

boro_num = Airbnb_geo.borough.value_counts() #the series from which the data is taken

m_3 = folium.Map(location=[40.71427, -74.00597],tiles='cartodbpositron', zoom_start=10)

Choropleth(geo_data=boroughs.__geo_interface__, 
           data=boro_num, 
           key_on="feature.id", 
           fill_color='BuPu', 
           legend_name="Number of Airbnb apartments by borough (2019)"
          ).add_to(m_3)

m_3.save("Results\Choropleth.html")
