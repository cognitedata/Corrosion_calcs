import streamlit as st
from datetime import datetime
st.title("Tank Bottom Degradation - EDD653 Risk Level Assesment using Method A2.1")

## List down the required inputs
tank_info = st.sidebar.text_input("Tank ID")
product = st.sidebar.text_input("Product")
inspection_type = ["100% MFL/UT Scan","Spot Scan + EVA","Spot Scan","Visual Only"]
var_insp = st.sidebar.selectbox("Inspection Type",inspection_type) 
start_date = st.sidebar.date_input("Select last inspection date")
st.write('Last inspection date:', start_date)
curr_date = st.sidebar.date_input("Select next inspection date")
st.write('Next inspection date:', curr_date)
RTbc = st.sidebar.number_input("Minimum remaining thickness from bottom side after repairs (in)")
RTip = st.sidebar.number_input("Minimum remaining thickness from internal side after repairs (in)")
UPr = st.sidebar.text_input("Soil Side Corrosion rate (in/year)")
StPr = st.sidebar.text_input("Product Side Corrosion rate (in/year)")
coating_life = st.sidebar.number_input("Coating life (in years) - Input 0 if coating is absent")
cathodic_protection = st.sidebar.selectbox("Cathodic Protection",["Yes","No"]) 
ca = st.sidebar.selectbox("Level of conservative assessment",["Low","Medium","High"]) 
service_change = st.sidebar.selectbox("Service Change",["Yes","No"]) 

if service_change == "Yes":
    StPr2 = st.sidebar.text_input("Product Side Corrosion rate - second product (in/year)")
    sc_duration = st.sidebar.number_input("Service duration of first product (in/year)")

def inspection_effectiveness(var_insp):
    if var_insp == inspection_type[0]:
        eff = "High"
    
    elif var_insp == inspection_type[1]:
        eff = "Medium"
    
    else:
        eff = "Low - Use Method A2.2 or A.1"
    return eff


def probability_levels(var_insp, start_date, curr_date, RTip, RTbc, StPr, UPr,coating_life,cathodic_protection,ca,service_change,sc_duration=0,StPr2=0):
    inspection =  inspection_effectiveness(var_insp)
    date_format = "%Y-%m-%d"
    t1 = datetime.strptime(str(start_date), date_format)
    t2 = datetime.strptime(str(curr_date), date_format)
    Or = abs((t2 - t1).days)/365.25
    factor = 2/3
    StPr = float(StPr)
    UPr = float(UPr)
    StPr2 = float(StPr2)
    ## Defines various total corrosion rate and soil side corrosion rate based on conservative level - crc
    
    if service_change == "No":
    
        if ca == "Low":
            corrosion_rate = max((factor*StPr+UPr),(factor*UPr+StPr))
            UPr = (2/3)*UPr
            
        elif ca == "Medium":
            corrosion_rate = max((factor*StPr+UPr),(factor*UPr+StPr))
            UPr = UPr
            
        else:
            corrosion_rate = StPr + UPr
            UPr = UPr
            
        ## Calcuates MRT based on defined conservative level and presence/absence of cathodic protection
        ## Note: Corrosion rate varies for each level
        
        if cathodic_protection  == "No":
            MRT = min(RTip,RTbc) - (Or - coating_life)*corrosion_rate - (coating_life*UPr)
            
        else:
            MRT = min(RTip,RTbc) - (Or - coating_life)*(StPr)
    
    else:
         ## will have to review the complete condition
        if ca == "Low":
            corrosion_rate1 = max((factor*StPr+UPr),(factor*UPr+StPr))
            corrosion_rate2 = max((factor*StPr2+UPr),(factor*UPr+StPr2))
            UPr = (2/3)*UPr
            
        elif ca == "Medium":
            corrosion_rate1 = max((factor*StPr+UPr),(factor*UPr+StPr))
            corrosion_rate2 = max((factor*StPr2+UPr),(factor*UPr+StPr2))
            UPr = UPr
            
        else:
            corrosion_rate1 = StPr + UPr
            corrosion_rate2 = StPr2 + UPr
            UPr = UPr

        if cathodic_protection  == "No":
            MRT = min(RTip,RTbc) - (sc_duration - coating_life)*corrosion_rate1 - (Or - sc_duration )*corrosion_rate2 - (coating_life*UPr)
            
        else:
            MRT = min(RTip,RTbc) - (sc_duration - coating_life)*StPr - (Or - sc_duration )*StPr2

    a = 0
    b = 0.05
    c = 0.1
    d = 0.15
    e = 0.2
    if inspection == "High":
        if MRT <= a:
            pl = "A"
        elif MRT < b:
            pl = "B"
        elif MRT < c:
            pl = "C"
        elif MRT < d:
            pl = "D"
        else:
            pl = "E"
            
    elif inspection == "Medium":
        if MRT < b:
            pl = "A"
        elif MRT < c:
            pl = "B"
        elif MRT < d:
            pl = "C"
        elif MRT < e:
            pl = "D"
        else:
            pl = "E"
    
    else:
        pl = "Not Applicable"
    return pl

if st.button("EDD 653 Level 1 assessment - Method A2.1"):
    inspection =  inspection_effectiveness(var_insp)
    st.write("For the tank ID: ", tank_info, "and Product ID:", product,', the inspection effectiveness is', inspection,".")
    if service_change == "Yes":
        BP = probability_levels(var_insp, start_date, curr_date, RTip, RTbc, StPr, UPr,coating_life,cathodic_protection,ca, service_change,sc_duration,StPr2)
    else:
        BP = probability_levels(var_insp, start_date, curr_date, RTip, RTbc, StPr, UPr,coating_life,cathodic_protection,ca, service_change)
    st.write('The base probability level based on method A2.1 after inspection:', BP,".")
    
