python3 txt-proc-new.py proc-new-data.txt -o ./summarization/proc-new-res.csv &
python3 txt-proc-mem.py proc-mem-data.txt -o ./summarization/proc-mem-res.csv &
python3 txt-proc-cpu.py proc-cpu-data.txt -o ./summarization/proc-cpu-res.csv &
python3 txt-network.py network-data.txt -o ./summarization/network-res.csv &
python3 txt-cpu-load.py cpu-load-data.txt -o ./summarization/cpu-load-res.csv &
python3 txt-file.py file-data.txt -o ./summarization/file-res.csv