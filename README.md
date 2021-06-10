This repository contains scripts for running multiple software verification techniques.


# How to use (Linux)
Create `scorch-analysis` directory
```
mkdir scorch-analysis
cd scorch-analysis
git clone https://github.com/scorch-project/analysis.git
```


## Dependencies
### FuSeBMC
```
wget https://github.com/kaled-alshmrany/FuSeBMC/releases/download/v4.0.1/FuSeBMC_v4.0.1.zip
unzip FuSeBMC_v4.0.1.zip
```
### ESBMC
```
wget https://github.com/esbmc/esbmc/releases/download/v6.7/ESBMC-Linux.sh
bash ESBMC-Linux.sh
```
### clang
```
wget https://github.com/llvm/llvm-project/releases/download/llvmorg-12.0.0/clang+llvm-12.0.0-x86_64-linux-gnu-ubuntu-20.04.tar.xz
tar xf clang+llvm-12.0.0-x86_64-linux-gnu-ubuntu-20.04.tar.xz
```
### SoftBoundCETS
```
git clone https://github.com/santoshn/softboundcets-34.git
cd softboundcets-34/softboundcets-llvm-clang34
./configure --enable-assertions --disable-optimized
make -j8
```
The above command will build a version of LLVM/Clang with SoftBoundCETS enabled. This might take about 30 minutes.
```
cd ../softboundcets-34/softboundcets-lib
make
cd ../..
```
### PureCap
```
git clone https://github.com/CTSRD-CHERI/cheribuild.git
cd cheribuild
./cheribuild.py --run/ssh-forwarding-port 5555 run-riscv64-purecap -d
```
The first time you run this command it will take over two hours as `cheribuild.py` will need to build the VM and the dependencies in your home folder (`$HOME/cheri`). This command will also start a virtual machine in the current terminal window so you will need to open a new terminal and navigate to the `scorch-analysis` folder.


## How to run

```
cd scorch-analysis
export SCORCH_DIR=$PWD
cd analysis
```

You can run the script executing the following command in the `src` directory:
```
src/run_hybrid.py examples/stack-use/after-return.c
```

The full list of supported command line options is available via:
```
src/run_hybrid.py --help
```


## Running SV-COMP benchmarks

Download SV-COMP benchmarks from GitHub:
```
cd $SCORCH_DIR
git clone https://github.com/sosy-lab/sv-benchmarks.git
cd analysis 
```

To run our script on 178 benchmarks not requiring any inputs use the following command:
```
src/run_hybrid.py --CFLAGS-soft=src/extra-defs.c --CFLAGS-def=src/extra-defs.c --CFLAGS-purecap=src/extra-defs.c --esbmc-opts="--incremental-bmc --unlimited-k-steps --memory-leak-check --no-div-by-zero-check --force-malloc-success --state-hashing --no-align-check --quiet" --sv-comp-root=$SCORCH_DIR/sv-benchmarks benchmarks/sv-comp-without-nondet.txt --timeout=60
```

Similarly, to run our script on 127 unsafe benchmarks requiring inputs use the following command:
```
src/run_hybrid.py --CFLAGS-soft=src/extra-defs.c --CFLAGS-def=src/extra-defs.c --CFLAGS-purecap=src/extra-defs.c --esbmc-opts="--incremental-bmc --unlimited-k-steps --memory-leak-check --no-div-by-zero-check --force-malloc-success --state-hashing --no-align-check --quiet" --sv-comp-root=$SCORCH_DIR/sv-benchmarks benchmarks/sv-comp-nondet-unsafe.txt --timeout=60
```

