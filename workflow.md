# What dataset did we download:
## SafeGraph:
- Open Census Data: computer-readable version made by Safegraph, but the source of the data is the American Community Survey (2016) publish by the United States Census Bureau. This is the only data from SafeGraph publicly available [SafeGraph](https://www.safegraph.com/open-census-data)
- CBG geographical definitions for the three states included inside the New York Metro Area (Connecticut, New York, New Jersey)
- ZTCA geographical definitions for all the USA
- Core POI Files: Datasets containin information about POIs (id , category, address, city, region, postalcode, ...)
- Home Summary Files: Weekly data about CBGs (CBG ID, state, number devices residing, ...)
- Social Distancing Files: Daily data about behaviours in CBGs (CBG ID, device count, completely home device count, destination CBG, ...)
- Weekly Pattern Files: Weekly data about POIs (POI ID, hourly visits, median visit time, visitor home CBGs, ...)
- POI area file: Area in square foot of each POI

## New York Times:
- New York Times COVID-19 Dataset [GitHub](https://github.com/nytimes/covid-19-data)

## USA.com:
- New York Area ZIP Codes [New York, Northern New Jersey, Long Island Metro Area ZIP Codes and Maps](http://www.usa.com/new-york-northern-new-jersey-long-island-ny-nj-pa-area-zip-code-and-maps.htm)

# Data Preprocessing
## Filtering
1. Remove duplicated entries from the New York Area ZIP Codes dataset and transformed into a computer-readable format (handmade activity)
2. Build a correspondance table between each CBG and ZIP Code (ZTCA) inside the 3 states, then remove the CBGs that are not in the New York Metro Area
3. Filter out the CBGs outside the New York Metro Area form the Social Distancing datasets using the newly build correspondance table
4. Filter all the Core POI datasets by ZIP codes and contatenate them into a single file
5. Filter out the CBGs outside the New York Metro Area form the Home Summary datasets using the CBGs - ZIP codes correspondance table
6. Replace the headers of each file inside the Open Census Dataset with the original field fullname, then filter out the CBGs outside the New York Metro Area from the Open Census datasets using the CBGs - ZIP codes correspondance table
7. Filter out the POIs outside the New York Metro Area form the Home Summary datasets using ZIP codes

## Build matrix indexes
1. Extract all the POI IDs from each Weekly Pattern dataset into an ordered set, which will be used to construct other POI-related matrixes
2. Extract all the CBG IDs from each Weekly Pattern dataset into an ordered set, which will be used to construct other CBG-related matrixes
3. Uniquely identify all the POI categories from the Core POI file and gather them into a single dataset

## Build simulation matrixes
1. Area: Build a matrix containing the areas of each POI using the POI index matrix, categories and the POI area dataset 
2. Nc(i): Build a matrix containing the estimated CBG population size using the CBG index matrix and Population dataset (cbg_b01)
3. Hc(i): Build weekly matrixes containing the estimated fraction of people who left their home using CBG index matrix and Social Distancing datasets for each CBG
4. Build weekly matrixes containing estimated median dwell time spent by a person for each POI using POI index matrix and Weekly Pattern datasets
5. Wr(ij): Build an aggregate matrix for each week that contain how many person from each CBG go to a specific POI, it use the Weekly Pattern datasets and the matrix indexes
6. POI marginals: Build a matrix that contains the number of people inside a POI at a specific time t. For building it use the Weekly Pattern datasets, matrix indexes
7. CBG marginals: Build a matrix that contain how much movements each CBG generate. For building it use the POI marginals, the CBG population and the Hc(i)