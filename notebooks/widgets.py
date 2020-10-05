import pandas as pd
import panel as pn
import hvplot.pandas
import pgeocode

pn.extension()

def get_all_bands():
    allBands = pd.read_csv('allBands.csv')
    allBands['bandNumber'] = allBands.index + 1
    allBands['Province'] = allBands['address'].apply(lambda x: x.split(' ')[-1])
    allBands = allBands.drop_duplicates(subset ="bandName", keep ='first') 
    return allBands

def get_band_count(allBands):
    allBands['Province'] = allBands['address'].apply(lambda x: x.split(' ')[-1])
    bandCount = allBands.groupby('Province')['bandName'].count()
    return bandCount

def get_provinces(allBands):
    province_list = sorted(allBands['Province'].unique())
    return province_list

def filter_bands(bands, key, whitelist):
    filteredBands = bands[bands[key].isin(whitelist)]
    return filteredBands

def get_province_choices(province_group):
    return sorted(filter_bands(allBands, 'Province', province_group)['bandName'])

def postal_to_latitude(p):
    return nomi.query_postal_code(p)['latitude']

def postal_to_longitude(p):
    return nomi.query_postal_code(p)['longitude']

allBands = get_all_bands()
province_list = get_provinces(allBands)
@pn.depends(province_group.param.value)
def update_nation_group(province_group):
    nation_choices = get_province_choices(province_group)
    nation_group.options=nation_choices
    return nation_group

@pn.depends(nation_group.param.value)
def nation_table(nation_group):
    # Get nations
    nations = filter_bands(allBands, 'bandName', nation_group)
    return nations.hvplot.table()

@pn.depends(nation_group.param.value)
def nation_map(nation_group):
    # Get nations
    nations = filter_bands(allBands, 'bandName', nation_group)
    
    nomi = pgeocode.Nominatim('CA')
    nations['latitude'] = nations['postalCode'].apply(postal_to_latitude)
    nations['longitude'] = nations['postalCode'].apply(postal_to_longitude)
    
    chart = nations.hvplot.points('longitude', 'latitude', geo=True, color='red', alpha=0.2,
                       xlim=(-180, -30), ylim=(0, 72), tiles='ESRI')
    
    return chart

def get_province_select_widget(province_list):
    province_group = pn.widgets.CrossSelector(
        name='Province',
        value=[],
        options=province_list,
    )
    return pn.WidgetBox('## Select Provinces', province_group)

def get_nation_select_widget():
    nation_group = pn.widgets.CrossSelector(
        name = 'Nation',
        value=[],
        options=[])
    return pn.WidgetBox('## Select Nations', update_nation_group)
    

province_select = get_province_select_widget(province_list)
nation_select = get_nation_select_widget()
nation_detail = get_nation_detail_table()
nation_map = get_nation_map()
    
if __name__ == "__main__":
    allBands = get_all_bands()
    province_list = get_provinces(allBands)
    province_select = get_province_select_widget(province_list)
    nation_select = get_nation_select_widget()
    nation_detail = get_nation_detail_table()
    nation_map = get_nation_map()

    panel_dashboard = pn.Column(
        pn.Row(
            pn.WidgetBox('## Select Provinces', province_group), 
            pn.WidgetBox('## Select Nations', update_nation_group),
        ),
        pn.Row(
            pn.WidgetBox('## Nations Detail', nation_table), 
        ),
        pn.Row(
            pn.WidgetBox('## Nations Map', nation_map),
        ),
    )
    
    panel_dashboard.show()