
wget https://downloads.cs.stanford.edu/nlp/software/stanford-corenlp-4.5.4.zip
unzip stanford-corenlp-4.5.4.zip
rm stanford-corenlp-4.5.4.zip

cd stanford-corenlp-4.5.4
java -mx16g -cp "*" edu.stanford.nlp.pipeline.StanfordCoreNLPServer -port 9050 -timeout 15000 -threads 6 &
corenlp_process_pid=$!
cd ..
echo $corenlp_process_pid
python corenlp_extractor.py 4
kill -9 $corenlp_process_pid

