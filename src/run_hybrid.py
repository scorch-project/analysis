#!/usr/bin/env python3

import sys
import os
import glob
import yaml
import argparse
import subprocess
import pandas as pd
import re
import time


def parse_cmd():
  arg_parser = argparse.ArgumentParser()
  arg_parser.add_argument("--timeout", type=int, default=None, action="store",
              help="specifies the timeout for each of the tasks")
  arg_parser.add_argument("--sv-comp-root", default="", action="store",
              help="sets the root directory for the relative \
                  paths specified in the input file")
  arg_parser.add_argument("--esbmc-bin", default="$SCORCH_DIR/ESBMC-6.7.0-Linux/bin/esbmc", action="store",
              help="full path to the ESBMC binary")
  arg_parser.add_argument("--esbmc-opts", default="", nargs="*", 
              action="store", help="list of ESBMC options")
  arg_parser.add_argument("--fusebmc-path", default="$SCORCH_DIR/FuSeBMC_v4.0.1",  
              action="store", help="full path to FuSeBMC directory")
  arg_parser.add_argument("--CC-soft", 
              default="$SCORCH_DIR/softboundcets-34/softboundcets-llvm-clang34/Debug+Asserts/bin/clang", 
              action="store",
              help="full path to the SoftBoundCETS \
                  version of clang")
  arg_parser.add_argument("--CFLAGS-soft", 
              default=["-Wno-everything", 
                   "-fsoftboundcets", 
                   "-B/usr/lib/gcc/x86_64-linux-gnu/9/", 
                   "-pthread"
                  ], 
              action="extend", nargs="*", 
              help="additional CFLAGS for \
                 the SoftBoundCETS clang")
  arg_parser.add_argument("--LIBS-soft", 
              default=["-L$SCORCH_DIR/softboundcets-34/softboundcets-lib",
                   "-lsoftboundcets_rt", "-lm", 
                   "-L/usr/lib/gcc/x86_64-linux-gnu/9/"
                  ], 
              action="extend", 
              help="additional LIBS for the SoftBoundCETS clang")
  arg_parser.add_argument("--CC-def", default="$SCORCH_DIR/clang+llvm-12.0.0-x86_64-linux-gnu-ubuntu-20.04/bin/clang", action="store",
              help="full path to the default clang")
  arg_parser.add_argument("--CFLAGS-def", 
              default=["-Wno-everything", "-pthread", "-fsanitize=address"], 
              action="extend", nargs="*", 
              help="additional CFLAGS for the default clang")
  arg_parser.add_argument("--LIBS-def", default=[], action="extend", 
              help="additional LIBS for the default clang")
  arg_parser.add_argument("--CC-purecap", 
              default="$HOME/cheri/output/sdk/bin/clang", 
              action="store",
              help="full path to the Purecap clang")
  arg_parser.add_argument("--CFLAGS-purecap", 
              default=["-Wno-everything", 
                   "-pthread", 
                   "-target riscv64-unknown-freebsd13", 
                   "--sysroot=$HOME/cheri/output/rootfs-riscv64-purecap", 
                   "-B$HOME/cheri/output/sdk/bin", 
                   "-march=rv64imafdcxcheri", 
                   "-mabi=l64pc128d", 
                   "-mno-relax"
                  ], 
              action="extend", nargs="*", 
              help="additional CFLAGS for the Purecap clang")
  arg_parser.add_argument("--LIBS-purecap", 
              default=["-L$HOME/cheri/output/rootfs-riscv64-purecap/libcheri/"], 
              action="extend", 
              help="additional LIBS for the Purecap clang")
  arg_parser.add_argument("--purecap-address", default="localhost", 
              action="store", help="address of the Purecap VM")
  arg_parser.add_argument("--purecap-port", default=5555, type=int, 
              action="store", help="port of the Purecap VM")
  arg_parser.add_argument("--no-exec", default=False, action="store_true",
              help="do not execute the compiled binaries")
  arg_parser.add_argument("--output-dir", default="./", action="store",
              help="sets the output directory \
                  for the executables")
  arg_parser.add_argument("--output-table", default="./results.xlsx", 
              action="store",
              help="the full path to the XLS table \
                  containing the verification outputs")
  arg_parser.add_argument("input_file", 
              help="input file containing relative \
                  paths to the YAML files")
  return vars(arg_parser.parse_args())


def get_yml_paths(yml_list_path, yml_root_path):
  yml_paths = []
  with open(yml_list_path) as f:
    for line in f:
      line = line.strip()
      if not line.startswith("#") and line:
        yml_paths.extend(glob.glob(yml_root_path+"/"+line.strip()))
  
  return yml_paths


def run_yml_task(yml_path):
  print("Processing tasks from %s" % (yml_path))
  global df
  # if yml_path in df["task"].values:
  #   print("The task has already been processed (ignore)")
  # else:
  with open(yml_path) as yml:
    yml_data = yaml.load(yml, Loader = yaml.FullLoader)
    if yml_data["options"]["language"] == "C":
      if type(yml_data["input_files"]) is list:
        if len(yml_data["input_files"]) > 1:
          print("Multiple input C files are not yet supported")
          exit(1)
        else:
          input_file = os.path.dirname(yml_path)+"/"+yml_data["input_files"][0]
          # run_pipeline(input_file)    
      else:
        global df
        if yml_path in df["task"].values:
          return 0;
        print("-----")
        input_file = os.path.dirname(yml_path)+"/" \
               +yml_data["input_files"]
        output_file = argv["output_dir"]+"/" \
                +os.path.splitext(yml_path)[0].replace("/","+")
        get_expected_verdict(yml_data["properties"])
        print("Input file: %s" % input_file)
        print("Output file: %s" % output_file)
        print("Output dir: %s" % argv["output_dir"])
        res = run_pipeline(input_file, output_file)
        res["task"] = yml_path
        res["input_files"] = input_file
        # removing the row if the task already exists
        df = df[:][df["task"]!=yml_path]
        df = df.append(res, ignore_index=True)
        df.to_excel(argv["output_table"])
    else:
      print("Unknown input language. This task will be ignored")

  return 0


def get_expected_verdict(yml_properties):
  for item in yml_properties:
    if "expected_verdict" in item:
      print("Found expected verdict \"%s\" for the property file \"%s\"" \
          % (item["expected_verdict"], item["property_file"]))


def print_subproc_output(returncode, output):
  print("Terminated successfully") if returncode == 0 else print("Terminated abnormally")
  print("Return code: %d" % returncode)
  if output: 
    print("Output:\n*****\n%s\n*****" % output)


def get_paren_block(pos, text, sym_open, sym_close):
  for i in range(pos, len(text)):
    if text[i] == sym_open:
      sym_count = 1
      for j in range(i+1, len(text)):
        if text[j] == sym_open:
          sym_count += 1
        if text[j] == sym_close:
          sym_count -= 1
        if sym_count == 0:
          return i,j


# this function will replace "void main()" and return a path to the newly modified
# input file, or None if the code does not feature a "void main()"
def contains_nondet_fun(input_file):
  with open(input_file) as in_file:
    file_str = in_file.read()
    # checking if the code contains a nondet function
    return re.search(r".*__VERIFIER_nondet_.*", file_str)



# this function will replace "void main()" and return a path to the newly modified
# input file, or None if the code does not feature a "void main()"
def replace_void_main(input_file):
  print("Trying to find a \"void main()\" in %s" % input_file)
  with open(input_file) as in_file:
    file_str = in_file.read()
    # checking if the code has void main
    match = re.search(r".*void\s+main\s*\(", file_str)
    if match:
      print("Found a \"void main()\". Replacing it with \"int main\"")
      main_begin = match.span()[0]
      main_end = match.span()[-1]-1
      # adding all the code before main()
      new_str = file_str[:main_begin]
      # adding the modified main() declaration
      new_str += file_str[main_begin:main_end].replace("void", "int")
      args_begin, args_end = get_paren_block(main_end, file_str, "(", ")")
      # adding main function arguments
      new_str += file_str[args_begin:args_end+1]
      body_begin, body_end = get_paren_block(args_end, file_str, "{", "}")
      # replacing all return without any constants with return 0
      new_body = re.sub(r"(.*)return\s*;(.*)", r"\1return 0;\2",
                file_str[body_begin:body_end+1])
      # adding return 0 as the last statement in the function body
      # in case there are no returns at all
      new_body = new_body[:-2] + "\nreturn 0;\n" + new_body[-2:]
      # adding the modified version of main() body
      new_str += new_body
      # adding all the code after the end of main() function body
      new_str += file_str[body_end+1:]
      # saving the modified code to the file and 
      # returning the full path to this file
      dirname, filename = os.path.split(input_file)
      filename_base, filename_ext = os.path.splitext(filename)
      tag = ".modified"
      output_file = os.getcwd()+"/"+filename_base+tag+filename_ext
      with open(output_file, "w") as out_file:
        out_file.write(new_str)
        return output_file
    #else:
      #print("Didn't find it")


def get_c_file_if_exists(filename):
  file_name, file_ext = os.path.splitext(filename)
  if file_ext == ".i":
    new_filename = file_name + ".c"
    if os.path.exists(new_filename):
      print("Found: " + new_filename)
      return new_filename

  return filename


def run_pipeline(input_file, output_file):
  input_file = get_c_file_if_exists(input_file)
  new_intput_file = replace_void_main(input_file)
  if new_intput_file: 
    input_file = new_intput_file

  res = {}

  # running FuSeBMC
  cmd = "cd " + argv["fusebmc_path"] \
      + " && ./fusebmc.py -s incr -p ~/sv-benchmarks/c/properties/valid-memsafety.prp "
  if not argv["sv_comp_root"]:
    cmd += os.getcwd() + "/"
  cmd += input_file
  start_time = time.time()
  returncode, message = run_bmc(cmd, argv["timeout"])
  end_time = time.time()
  print_subproc_output(returncode, message)
  res["fusebmc_return"] = returncode
  res["fusebmc_message"] = message
  res["fusebmc_time"] = end_time - start_time

  # running ESBMC
  cmd = argv["esbmc_bin"] + " " + " ".join(argv["esbmc_opts"]) + " --timeout " \
      + str(argv["timeout"]) + "s " + input_file
  start_time = time.time()
  returncode, message = run_bmc(cmd, argv["timeout"])
  end_time = time.time()
  print_subproc_output(returncode, message)
  res["esbmc_return"] = returncode
  res["esbmc_message"] = message
  res["esbmc_time"] = end_time - start_time

  # building an executable with the default clang and running it
  returncode, message = build_exec(argv["CC_def"], argv["CFLAGS_def"], 
                   [input_file], output_file+".def", 
                   argv["LIBS_def"])
  res["clang_compile_return"] = returncode
  res["clang_compile_message"] = message
  print_subproc_output(returncode, message)
  if returncode == 0:
    if not argv["no_exec"] and os.path.exists(output_file+".def"):
      start_time = time.time()
      returncode, message = run_exec(output_file+".def", argv["timeout"],
                       "localhost", -1)
      end_time = time.time()
      os.remove(output_file+".def")
      res["clang_exec_return"] = returncode
      res["clang_exec_message"] = message
      res["clang_exec_time"] = end_time - start_time
      print_subproc_output(returncode, message)

  # building an executable with SoftBoundCETS and running it
  returncode, message = build_exec(argv["CC_soft"], argv["CFLAGS_soft"], 
                   [input_file], output_file+".soft", 
                   argv["LIBS_soft"])
  res["soft_compile_return"] = returncode
  res["soft_compile_message"] = message
  print_subproc_output(returncode, message)
  if returncode == 0:
    if not argv["no_exec"] and os.path.exists(output_file+".soft"):
      start_time = time.time()
      returncode, message = run_exec(output_file+".soft", argv["timeout"],
                       "localhost", -1)
      end_time = time.time()
      os.remove(output_file+".soft")
      res["soft_exec_return"] = returncode
      res["soft_exec_message"] = message
      res["soft_exec_time"] = end_time - start_time
      print_subproc_output(returncode, message)
    
  # building an executable with PureCap and running it
  returncode, message = build_exec(argv["CC_purecap"], argv["CFLAGS_purecap"],
                   [input_file], output_file+".purecap", 
                   argv["LIBS_purecap"])
  res["purecap_riscv_compile_return"] = returncode
  res["purecap_riscv_compile_message"] = message
  print_subproc_output(returncode, message)
  if returncode == 0:
    if not argv["no_exec"] and os.path.exists(output_file+".purecap"):
      start_time = time.time()
      returncode, message = run_exec(output_file+".purecap", 
                       argv["timeout"], 
                       argv["purecap_address"], 
                       argv["purecap_port"])
      end_time = time.time()
      os.remove(output_file+".purecap")
      res["purecap_riscv_exec_return"] = returncode
      res["purecap_riscv_exec_message"] = message
      res["purecap_riscv_exec_time"] = end_time - start_time
      print_subproc_output(returncode, message)

  if new_intput_file:
    os.remove(new_intput_file)
  
  return res
        

def run_bmc(cmd, timeout):
  print("Running command: ", cmd)
  try:
    returncode = 0
    message = subprocess.check_output(cmd, stderr=subprocess.STDOUT, \
                      shell=True, timeout=timeout)
    message = message.decode("utf-8")
  except subprocess.CalledProcessError as exc:
    returncode = exc.returncode
    message = exc.output.decode("utf-8")
  except subprocess.TimeoutExpired as exc:
    returncode = 124
    message = ""
    if(exc.output):
      message += exc.output.decode("utf-8")
    message += "The time limit of %ds has been reached" % timeout
  
  return returncode, message


# this function returns a tuple (return_code, message)
def build_exec(cc, cflags, input_file, output_file, libs):
  cmd="%s %s %s -o %s %s" % (cc, " ".join(cflags), 
                 " ".join(input_file), output_file, 
                 " ".join(libs))
  print("Running %s" % cmd)
  returncode = 0;
  message = "";
  try:
    message = subprocess.check_output(cmd, stderr=subprocess.STDOUT,
                      shell=True)
    message = message.decode("utf-8")
  except subprocess.CalledProcessError as exc:
    returncode = exc.returncode
    message = exc.output.decode("utf-8")

  return returncode, message


def run_exec(output_file, timeout, address="localhost", port=-1):
  try:
    returncode = 0
    if port == -1:
      print("Running the executable localy...")
      if timeout:
        cmd = "timeout -s 9 %d %s" % (timeout, output_file)
      else:
        cmd = output_file
      message = subprocess.check_output(cmd, stderr=subprocess.STDOUT, 
                        shell=True, timeout=timeout)
      message = message.decode("utf-8")
    else:
      print("Running the executable on %s:%d" % (address, port))
      # some error messages generated by the shell and 
      # not by the executed binary might not be returned
      if timeout:
        cmd = "scp -P %d %s root@localhost: && ssh -p %d root@localhost timeout -s 9 %d %s 2>&1 && printf \"\n\"$?" % (port, output_file, port, timeout, output_file)
      else:
        cmd = "scp -P %d %s root@localhost: && ssh -p %d root@localhost %s 2>&1 && printf \"\n\"$?" % (port, output_file, port, output_file)
      message = subprocess.check_output(cmd, stderr=subprocess.STDOUT, 
                        shell=True)
      message = message.decode("utf-8")
      # the last line of the message is the executable return code
      returncode = int(message.splitlines()[-1])
      message = "\n".join(message.splitlines()[:-1])
  except subprocess.CalledProcessError as exc:
    returncode = exc.returncode
    message = exc.output.decode("utf-8")
  except subprocess.TimeoutExpired as exc:
    returncode = 124
    message = "The time limit of %ds has been reached" % timeout

  return returncode, message    


def main():
  global argv
  argv = parse_cmd()
  global df
  if os.path.exists(argv["output_table"]):
    df = pd.read_excel(argv["output_table"], index_col=0)
  else:
    df = pd.DataFrame(columns=[
                  "task", 
                  "input_files", 
                  "clang_compile_return", 
                  "clang_compile_message",
                  "clang_exec_return", 
                  "clang_exec_message",
                  "clang_exec_time",
                  "soft_compile_return", 
                  "soft_compile_message",
                  "soft_exec_return", 
                  "soft_exec_message",
                  "soft_exec_time",
                  "purecap_riscv_compile_return", 
                  "purecap_riscv_compile_message",
                  "purecap_riscv_exec_return", 
                  "purecap_riscv_exec_message",
                  "purecap_riscv_exec_time",
                  "esbmc_return",
                  "esbmc_message",
                  "esbmc_time",
                  "fusebmc_return",
                  "fusebmc_message",
                  "fusebmc_time"
                ])

  file_name, file_ext = os.path.splitext(argv["input_file"])
  if file_ext in [".yml", ".yaml"]:
    run_yml_task(argv["input_file"])
  elif file_ext in [".c", ".cpp", ".i"]:
    input_file = argv["input_file"]
    output_file = argv["output_dir"]+"/" \
            +os.path.splitext(input_file)[0].replace("/","+")
    print("Input file: %s" % input_file)
    print("Output file: %s" % output_file)
    res = run_pipeline(input_file, output_file)
  else:
    yml_paths = get_yml_paths(argv["input_file"], argv["sv_comp_root"])
    print("Found %d files %d of which are unique" 
        % (len(yml_paths), len(set(yml_paths))))
    yml_paths = list(set(yml_paths))
    yml_paths.sort()
    for yml_path in yml_paths:
      file_name, file_ext = os.path.splitext(argv["input_file"])
      if file_ext in [".yml", ".yaml"]:
        run_yml_task(yml_path)
      else:
        input_file = yml_path
        output_file = argv["output_dir"]+"/" \
                +os.path.splitext(input_file)[0].replace("/","+")
        print("Input file: %s" % input_file)
        print("Output file: %s" % output_file)
        res = run_pipeline(input_file, output_file)
        res["task"] = yml_path
        res["input_files"] = input_file
        # removing the row if the task already exists
        df = df[:][df["task"]!=yml_path]
        df = df.append(res, ignore_index=True)
        df.to_excel(argv["output_table"])


if __name__ == "__main__":
    main()          
        
        
