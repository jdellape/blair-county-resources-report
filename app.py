import streamlit as st
import json
import pandas as pd
from organization import Organization
from service import Service
from weekly_schedule import WeeklySchedule
from daily_schedule import DailySchedule, DailyMealSchedule
from google.cloud import firestore
from google.oauth2 import service_account

#Set global vars
#tab3 = st.tabs(["View Report"])

SERVICES_OPTIONS = []

DAYS_OF_WEEK = ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']

MEALS = ["Breakfast", "Lunch", "Dinner"]

SERVICES_ON_SCHEDULE = ['Food/Pantries','Food/Meals','Warming Center']

SERVICES_ON_SCHEDULE_KEY_STRING_DICT = {'Food/Pantries':'food_pantries_','Food/Meals':'food_meals_','Warming Center':'warming_center_'}

#Read in list of available services
with open('available_services.txt') as f:
    for line in f.readlines():
        SERVICES_OPTIONS.append(line.strip())

#Define functions
@st.cache_resource
def get_db_object():
    key_dict = json.loads(st.secrets["textkey"])
    creds = service_account.Credentials.from_service_account_info(key_dict)
    db = firestore.Client(credentials=creds, project="streamlit-sources")
    return db

def get_editable_df_for_basic_schedule(service_key):
    is_available = [False for x in DAYS_OF_WEEK]
    open_times = ["" for x in DAYS_OF_WEEK]
    close_times = ["" for x in DAYS_OF_WEEK]
    df = pd.DataFrame(list(zip(DAYS_OF_WEEK, is_available, open_times, close_times)),
    columns =['day', 'available', 'beginning at', 'ending at'])
    return st.experimental_data_editor(df, key=service_key + '_weekly_schedule')   

def get_editable_df_for_meal_schedule(service_key):
    is_available = []
    days = []
    meals = []
    open_times = []
    close_times = []
    for day in DAYS_OF_WEEK:
        for meal in MEALS:
            is_available.append(False)
            days.append(day)
            meals.append(meal)
            open_times.append("")
            close_times.append("")
    df = pd.DataFrame(list(zip(days, meals, is_available, open_times, close_times)),
    columns =['day', 'meal', 'available', 'beginning at', 'ending at'])
    return st.experimental_data_editor(df, key=service_key + '_weekly_schedule')   

def get_service_list_intersection(db_doc_services_name_list):
    return set(SERVICES_OPTIONS).intersection(db_doc_services_name_list)

def get_service_names_from_db_doc(doc):
    return [service for service in list(doc['services'].keys())]      

def get_service_check_boxes_for_existing_agency(doc):
    service_list_to_return  = []
    #get list intersection
    found_services = get_service_names_from_db_doc(doc)
    for service in SERVICES_OPTIONS:
        #Check if it has a schedule
        #has_schedule_flag = service['has_schedule']
        if service in found_services:
            service_list_to_return.append(st.checkbox(label=service, value=True, key=service))
        else:
            service_list_to_return.append(st.checkbox(label=service, value=False, key=service))
    return service_list_to_return

def get_services_with_schedules(services_dict):
    #This returns a list of strings
    return [s for s in list(services_dict.keys()) if s in SERVICES_ON_SCHEDULE]

def get_schedule_entry_object_for_service(service_name):
    if service_name == "Food/Meals":
        return get_editable_df_for_meal_schedule(SERVICES_ON_SCHEDULE_KEY_STRING_DICT[service_name])
    else:
        return get_editable_df_for_basic_schedule(SERVICES_ON_SCHEDULE_KEY_STRING_DICT[service_name])
    
def get_ordered_df_column_list(service_name):
    if service_name == 'Food/Meals':
        return ['day','meal','available','beginning at','ending at']
    else:
        return ['day', 'available','beginning at','ending at']

#Make connection to firestore db
DB = get_db_object()

AGENCY_REF = DB.collection("agencies")
AGENCY_LIST = [doc.to_dict() for doc in AGENCY_REF.stream()]
AGENCY_NAMES = [agency['name'] for agency in AGENCY_LIST]

#with tab3:
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
