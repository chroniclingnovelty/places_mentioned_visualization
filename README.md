# Horizons of interest: Places mentioned in chronicles 1770-1815
    
## Project description        
Based on chronicles recorded from 1770 to 1815, the project aims to      

<br> 

## chronicles processing strategy
XML file was processed in `./script/process_chronicles_ITag.py`, class `ChronicleBucket` is defined for each chronicle. 


Select dates ranging from 1770 to 1815 in a monthly resolution. 
The mentioned location (with a locatie tag)'s date is defined as the nearest date (with a datum tag) before it. 



## Scripts
`./script/mapping.ipynb`         
`./script/multiple_chronicles_new.ipynb`        
`./script/process_chronicles_ITag.py`     
`./script/st_vis.py`    


## Preprocessed data for map visualization
`../data/corrected_mapping_filter.csv`       
manually corrected original locations with their modern names. columns include geo-coordinates of the mentioned locations, hover, raw_location, true_place etc. Generated from script `mapping.ipynb`   
<br> 
_la, lo:_ latitude, longtitude      
_hover:_ hover info shown in the map, the content of chronicles mentioned the location   
_belong_date:_ the date when the location is mentioned         
_raw_location:_ original locations in the content     
_true_place:_ corresponding modern name for the raw locations   
_rownames:_ chronicles contents with mentioned locations.    
<br>

`./data/Chronicle-Center-new.pickle`     
A dictionary. Keys are names of the chronicles, values contains matched place (where the chronicle is written), latitude and longtitude of the place. Generated from script `mapping.ipynb`. 
```
{'1793_Bred_Ouko': {'match_place': 'Breda', 'la': '51.58656', 'lo': '4.77596'},    
'1795_Maas_Anon': {'match_place': 'Maastricht', 'la': '50.84833', 'lo': '5.68889'},...}
```     
<br>    

`/app/chronicle_vis_project/data/summary_table.csv`    
A summary of the corrected_mapping_filter.




## Map visaulization 
 





       




