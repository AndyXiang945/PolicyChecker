
# PolicyChecker

This repository host the following materials for the ACM CCS 2023 accepted paper: ***"PolicyChecker: Analyzing the GDPR Completeness of Mobile Apps’ Privacy Policies"*** .

  
- [The 20 pages long version of the paper](Policy_Checker_CCS_2023.pdf)

- [Android app dataset](https://mines0-my.sharepoint.com/:u:/g/personal/xianganhao_mines_edu/EUYTQS7cwHpErWp8bW6khRIBggsyyBK9qlAtoJA-5fghZg?e=6Tv7wW) 

- Code of the PolicyChecker framework


## Usage
1. Download and extract [NLP models](https://mines0-my.sharepoint.com/:f:/g/personal/xianganhao_mines_edu/Epfv5BHmuZxKksIn_1JlfHkBjXcM_qsfau-b0_-lEI08ZQ?e=8iIg2i) to ```\models```.

2. Download and extract [meta data files](https://mines0-my.sharepoint.com/:u:/g/personal/xianganhao_mines_edu/EeVQ364goKZAmIzngis6eDUBRWlY9QqFa_uMRwgkc1ovmg?e=S3IElG) to ```\meta_data```.
Note: You need to create two addtional meta files in order to perform controller identity detection: ```policy-to-app_title_mapping.pickle and policy-to-deverloperID_mapping.pickle``` 
Example: ``` ('policy_id : developer_id') ```

3. Run the code
```
# python = 3.8
pip install -r requirements.txt

python main.py
parameters: 
	-path to privacy policy
	-path to output folder
	-path to the folder storing metadata files
	-path to the folder storing NLP models
	-CUDA ID to run on the GPU (-1 to run on the CPU)
Example:
python main.py /path/to/input_folder/policy.txt /path/to/output_folder/ meta_data/ models/ 0
```

## Publication
Anhao Xiang, Weiping Pei, and Chuan Yue. 2023. PolicyChecker: Analyzing the GDPR Completeness of Mobile Apps’ Privacy Policies. In Proceedings of the 2023 ACM SIGSAC Conference on Computer and Communications Security (CCS ’23), November 26–30, 2023, Copenhagen, Denmark. ACM, New York, NY, USA, 15 pages. https://doi.org/10.1145/3576915.3623067

 ## Acknowledgement
This repo uses NER model published by [PurPliance ](https://github.com/ducalpha/PurPlianceOpenSource). 
The provided Android app dataset is obtained from the Androzoo collections:  

Kevin Allix, Tegawendé F Bissyandé, Jacques Klein, and Yves Le Traon. 2016. Androzoo: Collecting millions of android apps for the research community. In Proceedings of the International Conference on Mining Software Repositories (MSR)

## License
PolicyChecker is licensed under a Creative Commons Attribution International 4.0 License. 
