"""Function to copy the inference files we want to analises from fugu to ponyta
"""
import pandas as pd 
import os 

def main(path_inference_list, path_directory, path_to_be_saved, number_files=20):
    df = pd.read_csv(path_inference_list)  
    # print(df.head())
    # print(df.Lightcurve_path.head())
    df_new = (df.tail(number_files)).copy()
    lightcurve_paths = df_new.Lightcurve_path
    for path in lightcurve_paths:
        file_path = path.split("ive/")[1].split(".feather")[0]
        file_path = file_path.replace('_','/')
        total_file_path = path_directory + file_path + '.gz'
        #print(total_file_path)
        command_line = 'scp gs66-fugu.ndc.nasa.gov:'+total_file_path+' '+path_to_be_saved
        os.system(command_line)
    return None

if __name__ == '__main__':
    path_inference_list = "/Users/sishitan/Documents/MOA/inference_Jul_Aug/MOA_microlensing_4/Inference_on_positives/infer_results_2020-08-02-22-51-30.csv"
    path_directory = '/local/data/fugu3/sishitan/MOAdata/lcurve/'
    path_to_be_saved = '/Users/sishitan/Documents/MOA/inference_Jul_Aug/MOA_microlensing_4/Inference_on_positives/'
    main(path_inference_list, path_directory, path_to_be_saved)


