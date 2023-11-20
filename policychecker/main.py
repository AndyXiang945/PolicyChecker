import sys, os
import os.path
from sentence_processing import sentence_reciever
import pickle
import multiprocessing
from allennlp.predictors.predictor import Predictor
from sentence_transformers import SentenceTransformer
import spacy
import gc
import torch

def search_controller_id(URL, meta_file_folder):
    controller_id = ''
    app_title = ''
    file = open( meta_file_folder + 'hashedURL_to_deverloperID_mapping.pickle', 'rb')
    controller_id_mapping = pickle.load(file)
    url_hash = URL.split('.')[0]
    if url_hash in controller_id_mapping:
        controller_id = controller_id_mapping[url_hash]
    
    file = open(meta_file_folder + 'app_title_to_hashedURL_mapping.pickle', 'rb')
    appname_urls = pickle.load(file)
    for title, url in appname_urls.items():
        if url == url_hash: 
            app_title = title 
    return controller_id, app_title

def run(policy_name, input_path, output_folder, template_representations, meta_file_folder, model_folder, cuda):
    if cuda == -1:
        SRL_predictor = Predictor.from_path( model_folder + "structured-prediction-srl-bert.2020.12.15.tar.gz")
        sbert = SentenceTransformer('all-MiniLM-L6-v2')
        nlp = spacy.load(model_folder + 'NER')
        print('finish loading SRL, SBERT, NER models to CPU')
    else:
        try:
            device = 'cuda:'+str(cuda)
            SRL_predictor = Predictor.from_path( model_folder + "structured-prediction-srl-bert.2020.12.15.tar.gz", cuda_device=cuda )
            sbert = SentenceTransformer('all-MiniLM-L6-v2', device=device)

            spacy.prefer_gpu(cuda)
            nlp = spacy.load(model_folder + 'NER')
            print('Finish loading SRL, SBERT, NER models to GPU')
        except:
            print('Error allocation GPU, exit the process')
            torch.cuda.set_device(cuda)
            gc.collect()
            torch.cuda.empty_cache() 
            exit()   

    controller_id, app_title = search_controller_id(policy_name, meta_file_folder)

    file_extension = os.path.splitext(input_path)[1]
    if file_extension == '.txt':
        file_contents = []
        with open(input_path, 'r', encoding='utf-8') as file:
            for line in file:
                file_contents.append(line)
        print('sentence processing...')
        sentence_reciever(policy_name, file_contents, controller_id, app_title, template_representations, output_folder, sbert, nlp, SRL_predictor, True)
    else:
        print('error: file is no txt format')

    del SRL_predictor
    del sbert
    del nlp

    gc.collect()
    torch.cuda.set_device(cuda)
    torch.cuda.empty_cache()


def main():
    input_path = sys.argv[1]
    output_path = sys.argv[2] 
    policy_name = os.path.basename(input_path).split('/')[0]
    output_file = policy_name + '_report.json'

    if os.path.isfile(output_path + output_file):
        print('policy already processed')
        exit()

    meta_file_folder = sys.argv[3]
    model_folder = sys.argv[4]
    cuda = int(sys.argv[5])

    print ('#######################################')
    print ('input: ', input_path)
    print ('output to: ', output_path)
    print ('meta files:  ', meta_file_folder)
    print ('models: ', model_folder)
    print ('cuda id: ', cuda)
    print ('#######################################')

    f = open(meta_file_folder + 'comparsion_template.pickle', 'rb')
    template_representations = pickle.load(f)

    run(policy_name, input_path, output_path, template_representations, meta_file_folder, model_folder, cuda)

       
if __name__ == "__main__":
   main()