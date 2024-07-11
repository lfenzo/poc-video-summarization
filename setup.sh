conda env create --name env --file environment.yaml
conda activate env

pip install llama-cpp-python \
  --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/cu124
