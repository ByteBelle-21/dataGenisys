import pandas as pd
import numpy as np
from django.shortcuts import render, redirect
from django.http import HttpResponse
from .nan_handler import NaN_handler
from .data_encoder import category_encoder
from .correlations import get_corr
from .graphs import graph_generator
from django.http import JsonResponse
import json
from .machine_learning_models import predictive_model

def home_page(request):
    return render(request,'datagenisys/home_page.html')

def about_us(request):
     return render(request,'datagenisys/about_us.html')

def get_dataset(request):
    got_data = False
    if request.method == 'POST':
        if 'csvFile' in request.FILES:
            csv_file = request.FILES['csvFile']
            target_variable = request.POST['targetVariable']
            categorical_columns = request.POST['categoricalNumeric']
            Numeric_categorical_columns = []
            if(categorical_columns!="No"):
                Numeric_categorical_columns = [column.strip() for column in categorical_columns.split(',')]
            dataframe = pd.read_csv(csv_file)
            false_target = False
            if(target_variable  not in dataframe.columns):
                false_target = True 
            got_data = True
            data_initial_info = []
            data_cleaning_steps = []
            for col, dtype in dataframe.dtypes.items():
                data_initial_info.append((col,dtype,dataframe[col].isnull().sum())) 

            # Handle the missing values int the dataframe
            dataframe,data_cleaning_steps = NaN_handler(dataframe,Numeric_categorical_columns, data_cleaning_steps)
            df_json = dataframe.to_json()
            datetime_cols = {
                'original_col' :[],
                'new_cols' :[]
            }

            dataframe, data_cleaning_steps,Numeric_categorical_columns,data_encoding_map, datetime_cols = category_encoder(dataframe,data_cleaning_steps,Numeric_categorical_columns,datetime_cols)
            
            cleaned_dataset = []
            for col, dtype in dataframe.dtypes.items():
                cleaned_dataset.append((col,dtype,dataframe[col].isnull().sum()))  

            correlation_dict = json.dumps(get_corr(dataframe)) 

            #predictive_model(dataframe,target_variable)
            context = {
                'false_target': false_target,
                'got_data': got_data,
                'data_initial_info':data_initial_info, 
                'data_cleaning_steps' : data_cleaning_steps,
                'cleaned_dataset':cleaned_dataset,
                'df_json':df_json,
                'correlation_dict':correlation_dict,
                'Numeric_categorical_columns':Numeric_categorical_columns,
                'target_variable':target_variable,
            }
            return render(request, 'datagenisys/home_page.html', context)
    return render(request, 'datagenisys/home_page.html', {'got_data': got_data})


def get_graphs(request):
    print("i am here get graphs")
    if request.method == 'POST':
        column = request.POST['column']
        updated_df_json = request.POST['df_json']
        categorical_cols = request.POST['Numeric_categorical_columns']
        target_variable = request.POST['target_variable']
        correlated_cols_js = request.POST['correlation_dict']
        correlated_cols = json.loads(correlated_cols_js)
        updated_df = pd.read_json(updated_df_json) 
        graphs_url = graph_generator(updated_df,column,correlated_cols[column],categorical_cols,target_variable)
        response_data={
                'graphs_url':graphs_url,
                'column':column,
            }
        return JsonResponse(response_data)
    return JsonResponse({'error': 'Invalid request'}, status=400)




