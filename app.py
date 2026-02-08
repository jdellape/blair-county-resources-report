import streamlit as st
import json
import pandas as pd
from firebase_client import get_firestore

SERVICES_OPTIONS = []

DAYS_OF_WEEK = ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']

MEALS = ["Breakfast", "Lunch", "Dinner"]

SERVICES_ON_SCHEDULE = ['Food/Pantries','Food/Meals','Warming Center']

SERVICES_ON_SCHEDULE_KEY_STRING_DICT = {'Food/Pantries':'food_pantries_','Food/Meals':'food_meals_','Warming Center':'warming_center_'}

#Read in list of available services
with open('available_services.txt') as f:
    for line in f.readlines():
        SERVICES_OPTIONS.append(line.strip())
SERVICES_OPTIONS.sort()

@st.cache_data()
def get_agency_list(_db_connection):
    agency_ref = _db_connection.collection("agencies")
    agency_list = [doc.to_dict() for doc in agency_ref.stream()]
    return sorted(agency_list, key=lambda d:d['name'])

def get_service_list_intersection(db_doc_services_name_list):
    return set(SERVICES_OPTIONS).intersection(db_doc_services_name_list)

def get_service_names_from_db_doc(doc):
    return [service for service in list(doc['services'].keys())]
    
def get_ordered_df_column_list(service_name):
    if service_name == 'Food/Meals':
        return ['day','meal','available','beginning at','ending at']
    else:
        return ['day', 'available','beginning at','ending at']

# Make connection to firestore db
DB = get_firestore()

# Get data from db and cache it
AGENCY_LIST = get_agency_list(DB)
AGENCY_NAMES = [agency['name'] for agency in AGENCY_LIST]

#Radio button to either view all agencies or restrict by name or service
st.subheader('Report View Mode')
view_mode_selection = st.radio('View Mode', options=['All Organizations','Single Organization','Organizations Based on Services Provided'],
                                horizontal=True, label_visibility='hidden')
#Show all orgs by default
if view_mode_selection == 'All Organizations':
    for agency in AGENCY_LIST:
        st.subheader(agency['name'])
        st.write(f"Phone #: ", agency['phone_num'])
        with st.expander("See More Information"):
            st.write(f"Address : {agency['address_line_one']}")
            st.write(f"City : {agency['city']}")
            st.write(f"Zip Code : {agency['zip_code']}")
            st.write(f"Contact Name : {agency['contact_name']}")
            st.write(f"Email : {agency['email']}")
            st.write(f"Description of Services: {agency['services_description']}")
            st.write('Schedule :')
            hours_of_operation_from_db = pd.DataFrame.from_dict(agency['hours_of_operation'])
            hours_of_operation_from_db = hours_of_operation_from_db[get_ordered_df_column_list('hours_of_operation_view')]
            st.write(hours_of_operation_from_db)
            st.subheader('Services')
            for service in agency['services']:
                st.write(service)
                if agency['services'][service]['has_schedule']:
                    schedule_df_from_db = pd.DataFrame.from_dict(agency['services'][service]['schedule'])
                    schedule_df_from_db = schedule_df_from_db[get_ordered_df_column_list(service)]
                    st.write(schedule_df_from_db)

#filter the agency_list for only a single agency name selected by user
if view_mode_selection == 'Single Organization':
    selected_agency = st.selectbox('Select an Agency to View', options=[""] + AGENCY_NAMES, key='selected_agency_view_report')
    if selected_agency != "":
        #Get the agency from db
        agency = [a for a in AGENCY_LIST if a['name'] == selected_agency][0]
        st.subheader(agency['name'])
        st.write(f"Phone #: ", agency['phone_num'])
        with st.expander("See More Information"):
            st.write(f"Address : {agency['address_line_one']}")
            st.write(f"City : {agency['city']}")
            st.write(f"Zip Code : {agency['zip_code']}")
            st.write(f"Contact Name : {agency['contact_name']}")
            st.write(f"Email : {agency['email']}")
            st.write(f"Description of Services: {agency['services_description']}")
            st.write('Schedule :')
            hours_of_operation_from_db = pd.DataFrame.from_dict(agency['hours_of_operation'])
            hours_of_operation_from_db = hours_of_operation_from_db[get_ordered_df_column_list('hours_of_operation_view')]
            st.write(hours_of_operation_from_db)
            st.subheader('Services')
            for service in agency['services']:
                st.write(service)
                if agency['services'][service]['has_schedule']:
                    schedule_df_from_db = pd.DataFrame.from_dict(agency['services'][service]['schedule'])
                    schedule_df_from_db = schedule_df_from_db[get_ordered_df_column_list(service)]
                    st.write(schedule_df_from_db)

#filter the agency_list for only agencies which provide a particular service
if view_mode_selection == 'Organizations Based on Services Provided':
    selected_service = st.selectbox('Select Service of Interest', options=[""] + SERVICES_OPTIONS, key='selected_service_view_report')
    if selected_service != "":
        #Get the agency from db
        agencies_with_selected_service_list = []
        for a in AGENCY_LIST:
            try:
                service = a['services'][selected_service]
                agencies_with_selected_service_list.append(a)
            except:
                pass
        for agency in agencies_with_selected_service_list:
            st.subheader(agency['name'])
            st.write(f"Phone #: ", agency['phone_num'])
            with st.expander("See More Information"):
                st.write(f"Address : {agency['address_line_one']}")
                st.write(f"City : {agency['city']}")
                st.write(f"Zip Code : {agency['zip_code']}")
                st.write(f"Contact Name : {agency['contact_name']}")
                st.write(f"Email : {agency['email']}")
                st.write(f"Description of Services: {agency['services_description']}")
                st.write('Schedule :')
                hours_of_operation_from_db = pd.DataFrame.from_dict(agency['hours_of_operation'])
                hours_of_operation_from_db = hours_of_operation_from_db[get_ordered_df_column_list('hours_of_operation_view')]
                st.write(hours_of_operation_from_db)
                st.subheader('Services')
                for service in agency['services']:
                    st.write(service)
                    if agency['services'][service]['has_schedule']:
                        schedule_df_from_db = pd.DataFrame.from_dict(agency['services'][service]['schedule'])
                        schedule_df_from_db = schedule_df_from_db[get_ordered_df_column_list(service)]
                        st.write(schedule_df_from_db)
