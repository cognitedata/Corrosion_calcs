from datetime import datetime
import streamlit as st

def inspection_effectiveness(var_insp):
    if var_insp == inspection_type[0]:
        eff = 'High'

    elif var_insp == inspection_type[1]:
        eff = 'Medium'

    else:
        eff = 'Low - Use Method A2.2 or A.1'

    return eff

def findProbabilityLevel(scr, startDate, currentDate, mst, inspection_type):

    # scr = float(scr)
    date_format = "%Y-%m-%d"
    t1 = datetime.strptime(str(startDate), date_format)
    t2 = datetime.strptime(str(currentDate), date_format)
    duration = abs((t2 - t1).days)/365.25
    pst = mst - scr * duration
    
    if inspection_type == 'Medium':
        if pst >= 1.1 * rst:
            output = 'The Probability Level is E, ie; Practically impossible'

        elif rst <= pst and pst <= 1.1 * rst:
            output = 'The Probability Level is D, ie; Very Unlikely'

        elif 0.9 * rst <= pst and pst <= rst:
            output = 'The Probability Level is C, ie; Unlikely'

        elif pst < 0.9 * rst:
            output = 'The Probability Level is B, ie; Somewhat Likely'



    elif inspection_type == 'High':

        if (pst >= 1.1 * rst) or (rst <= pst and pst <= 1.1 * rst):
            output = 'The Probability Level is E, ie; Practically impossible'

        elif 0.9 * rst <= pst and pst <= rst:
            output = 'The Probability Level is D, ie; Very Unlikely'

        elif pst < 0.9 * rst:
            output = 'The Probability Level is C, ie; Unlikely'

    else:
        output = inspection_type
    
    return output
    
if __name__ == "__main__":
    
    st.title('Equipment Strategy Tank Floor Corrosion - EDD653 Risk Level Assessment using Method A2.2 ')

    inspection_type = ["100% MFL/UT Scan","Spot Scan + EVA","Spot Scan","Visual Only"]
    var_insp = st.sidebar.selectbox("Inspection Type", inspection_type)
    tank_id = st.sidebar.text_input('Tank ID : ')
    product_id = st.sidebar.text_input('Product ID : ')
    mst = st.sidebar.number_input('Please enter the Measured Structural Thickness at last inspection : ')
    rst = st.sidebar.number_input('Please enter the Required Structural Thickness per API 653 : ')
    startDate = st.sidebar.date_input('Please enter the date of Last Inspection : ')
    currentDate = st.sidebar.date_input('Please enter the date of Current Inspection : ')

    scr = st.sidebar.number_input('Please enter the Structural Corrosion Rate : ')
    possiblities = ['Yes', 'No']
    criticalCorrosion = st.sidebar.selectbox('Corrosion in the critical area?', possiblities)
    
    if criticalCorrosion == 'Yes':
        scr = 0.05
        inspection_type = 'Medium'
    else:
        inspection_type = inspection_effectiveness(var_insp)

    st.write('Last Inspection Date : ', startDate)
    st.write('Next Inspection Date : ', currentDate)
    if st.button('EDD Critical Area Corrosionn Assessment'):
        result = findProbabilityLevel(scr, startDate, currentDate, mst, inspection_type)
        st.write(f'For the tank ID : {tank_id} and the product ID : {product_id}, the inspection level is {inspection_type}')
        st.write(result)