# runmetal: call Apple Metal Framework from Python (or YAML-recipe)

- numpy array -> GPU buffer -> compute -> copy result into numpy array

## requirements

- macOS
- Xcode (or CommandLineTools)
    - Metal Framework
- Python 3.x

## install

(python)
- brew install pyenv
- pyenv install 3.7.1

(venv)
- python -m venv .
- ./bin/pip install -r requirements.txt
- ./bin/python setup.py install
- ./bin/runmetal run example/xxx.yaml

## examples(YAML)

- [pi](example/pi.yaml)
    - calculate π by monte carlo
        - numpy.random.random()
        - -> copy numpy to GPU buffer
        - -> compute sqrt(x*x+y*y) < 1.0
        - -> copy GPU buffer to numpy bool8 array
        - numpy.sum(result == True)/len(result)*4
    - runmetal run example/pi.yaml
- [rand](example/rand.yaml)
    - random number generator (LCG)

## examples(python)

TBD
