import os

# Create project folders
for base_folder in ['data', 'docs', 'models', 'notebooks', 'references', 'reports', 'src']:
    if os.path.exists(base_folder) is False:
        os.makedirs(base_folder)

for data_stage in ['raw', 'interim', 'processed']:
    if os.path.exists(f'data/{data_stage}') is False:
        os.makedirs(f'data/{data_stage}')

