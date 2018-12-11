# runmetal: Apple Metal Framework caller

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
- git clone https://github.com/wtnb75/runmetal.git
- cd runmetal
- python -m venv .
- ./bin/pip install -r requirements.txt
- ./bin/python setup.py install

(released version)
- pip install runmetal

## usage(runmetal command)

```
Usage: runmetal [OPTIONS] COMMAND [ARGS]...

Options:
  --help  Show this message and exit.

Commands:
  compile
  lsdev
  mtlinfo
  run
```

- compile
    - precompile source in YAML to .metallib
    - ... may not work (depends on your environment)
- lsdev
    - list GPU device
- mtlinfo
    - show GPU info like [mtlinfo](https://dmitri.shuralyov.com/gpu/mtl)
- run
    - run recipe

## examples(YAML)

- [pi](example/pi.yaml)
    - calculate π by monte carlo
        - numpy.random.random()
        - -> copy numpy to GPU buffer
        - -> compute sqrt(x\*x+y\*y) < 1.0
        - -> copy GPU buffer to numpy bool8 array
        - numpy.sum(result == True)/len(result)*4
    - runmetal run example/pi.yaml
- [rand](example/rand.yaml)
    - random number generator (LCG)
    - runmetal run example/rand.yaml

## examples(python)

TBD
