source ~/anaconda3/etc/profile.d/conda.sh

git clone https://github.com/dwadden/dygiepp.git
cd dygiepp


conda create --name dygiepp python=3.7
conda activate dygiepp
pip install -r requirements.txt
conda develop .   # Adds DyGIE to your PYTHONPATH

chmod 755 ./scripts/pretrained/get_dygiepp_pretrained.sh
./scripts/pretrained/get_dygiepp_pretrained.sh
  
input_directory=../../../data/processed/dygiepp_input/
output_directory=../../../data/processed/dygiepp_output/

mkdir ${output_directory}

for file in ${input_directory}*
do
        
        filename=$(basename ${file})
        echo '> dygiepp processing: '$filename
        if  [ ! -e ${output_directory}/${filename} ]; then
                allennlp predict pretrained/scierc.tar.gz $input_directory$filename --predictor dygie --include-package dygie --use-dataset-reader --output-file $output_directory${filename}  --cuda-device -1
        fi
done


