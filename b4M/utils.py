
import os
import sys
import math
import json
import docker
import random

import distutils.file_util as duf # e.g., copy a file

from lxml import html

# ##############################################################################
# General Settings 
PROTO_MAP={
   '0': 'Shamir-Passive', 
   '1': 'Replicated-Ring', #passive
   '2': 'Replicated-4-Ring', #active
   '3': 'Shamir-Passive-ML-Eval', #passive/active?
   '4': 'Shamir-Passive-ML-Train', #passive/active?
   '5': 'Rep3Ring-ML-Eval', #passive/active?
   '6': 'Rep3Ring-ML-Train', #passive/active?
   '7': 'Rep4Ring-ML-Eval', #passive/active?
   '8': 'Rep4Ring-ML-Train', #passive/active?
   '9': 'Shamir-Active', 
  '10': 'MASCOT', # DH/active
  '11': 'semi2', #DH/passive
}

MPSPDZ_TIMER_IDS={
  '1': 'full',
  '2': 'input',
  # '3': 'inner_prod',
  '3': 'computation',
  # '3': 'ML-train',
  # '4': 'ML-predict',
}

# DEBUG_LVL=0
# DEBUG_LVL=1
DEBUG_LVL=2 # e.g., with full array output
# DEBUG_LVL=3 # even more verbose ^^ 

# ##############################################################################
# (Docker) Network Setup
DOCKER_NETWORK='webSPDZ-Net'
IP_BASE='172.16.37.'
IP_PARTY_START='10' # parties get the corresponding ascending numbers (10,11,12,...) for party IDs (0,1,2,...)

# ##############################################################################
# Docker-Container / Run Settings
## =============================================================================
## Resources (RAM / CPU)
# TODO::FUTURE: restrict containers' disk space (cf. task/ticket list)
# this should be in-memory usage (=RAM); there's an own approach for disk space 
MEMORY_PLAIN_LIMIT_PER_PARTY='4G' 
# MEMORY_PLAIN_LIMIT_PER_PARTY='16G' 
# defined memory swap = (amount of actual memory + swap capacity)
# ...if it has the same value as the actual memory limit, swapping shouldn't happen
MEMORY_SWAP_LIMIT_PER_PARTY='4G'  
# MEMORY_SWAP_LIMIT_PER_PARTY='16G'  

CPU_COUNT_PER_PARTY=4 # TODO: test impact of a PARTY's CPU
CPU_COUNT_MAX=64

## =============================================================================
# DOCK_POINT_INPUT_CONTAINER='/root/Dock-Point/Input'
# DOCK_POINT_INPUT_HOST=f'{os.getcwd()}/../Docker/Dock-Point/Input'
# DOCK_POINT_VOLUME_INPUT=f'{DOCK_POINT_INPUT_HOST}:{DOCK_POINT_INPUT_CONTAINER}:cached'

DOCK_POINT_PROGRAMS_HOST=f'{os.getcwd()}/Dock-Point/Programs'
DOCK_POINT_DATA_HOST=f'{os.getcwd()}/Dock-Point/Share-Data'
DOCK_POINT_LOGS_HOST=f'{os.getcwd()}/Dock-Point/Logs'
PARTY_LOGS='party_%s.log'
# PARTY_LOGS='party_%s.run-log.b4M' # TODO!
PARTY_LOGS_FORMAT=f'party_{{p_id_log}}.run-log.b4M'


REMOVE_DOCKER_CONTAINERS=True
# REMOVE_DOCKER_CONTAINERS=False
CLEANUP_DATA_LOGS_AFTER_BENCH=True
# CLEANUP_DATA_LOGS_AFTER_BENCH=False

# ##############################################################################
# Parsing & Data Archive
PARSE_MAGIC_HTML_ELEMENT='b3m4'

DATA_DIR_DEST='../Data'
# DATA_DIR_DEST='../Data/temp'
DATA_DIR=os.path.join(os.getcwd(), DATA_DIR_DEST)
DATA_FILE_SUFFIX='.json.b4M'

GRAPH_DIR=os.path.join(DATA_DIR, 'Graphs')


# ==============================================================================
def print_debug(text, lvl):
  if (lvl <= DEBUG_LVL):
    print(text)


# ==============================================================================
def get_json_file_name(prog, engine, protocol, nr_parties, arr_length, network, nr_runs):

  nr_p_str = '%02d' % int(nr_parties)

  # TODO: move 'array_length' (aka. data-input) check to program!
  if ('BB' in prog):
    arr_base = 10

    if (arr_length==1):
      arr_power = 0
    else:
      assert((arr_length%10)==0)
      # if ((arr_length%10)==0):
      arr_power = math.ceil(math.log(arr_length, arr_base))

    n = f'prog-{prog}_engine-{engine}_proto-{protocol}_network-{network}_parties-{nr_p_str}_array-{arr_base}^{arr_power}_runs-{nr_runs}'
  #end-if: 'BB"
  else:
    n = f'prog-{prog}_engine-{engine}_proto-{protocol}_network-{network}_parties-{nr_p_str}_array-{arr_length}_runs-{nr_runs}'

  n += DATA_FILE_SUFFIX
  return n


# ==============================================================================
def get_json_string(obj):
  return json.dumps(obj, indent=None, separators=(',', ':'))
  

# ==============================================================================
def get_docker_client():
  return docker.from_env()


# ==============================================================================
def get_docker_network(dock):
  return dock.networks.get(DOCKER_NETWORK)


# ==============================================================================
def clear_dock_point():
  for f in os.listdir(DOCK_POINT_LOGS_HOST):
    if (f.startswith('.')) or (f.startswith('..')):
      continue
    os.remove(os.path.join(DOCK_POINT_LOGS_HOST, f))


# ==============================================================================
def check_file_exists(fdir, fname):
  for f in os.listdir(fdir):
    if (f == fname):
      return True 

  return False 


# ==============================================================================
def copy_file(src_path, dest_path):
  dest_name, copied = duf.copy_file(src_path, dest_path)
  if not (copied==True):
    print("🛑%s: Copy failed: '%s' --> '%s'" % (sys._getframe().f_code.co_name, src_path, dest_path))
    sys.exit(-1)


# ==============================================================================
def clean_dir(dir_path):
  try:
    files = [f for f in os.listdir(dir_path) if not f.startswith('.')]
    [os.remove(os.path.join(dir_path, f)) for f in files]
  except OSError:
    print("🛑%s: Couldn't cleanup dir: %s" % (sys._getframe().f_code.co_name, dir_path))
    sys.exit(-1)

  return True


# ==============================================================================
# TODO: move data directory definition to beginning of settings!
# ......--> independent of engine, e.g.
def read_in_json(eng, program, fname):
  fname_path = os.path.join(DATA_DIR, 'b4M-ARES-SECPID-25', program, eng, fname)
  # fname_path = os.path.join(DATA_DIR, eng, fname)
  with open(fname_path, 'r') as f:
    j = json.loads(f.read())
  return j


# ==============================================================================
def craft_input_array(array_length, nullify=False):
  if(nullify==True):
    array = [None]*array_length
  else:
    array = []
    for i in range(array_length):
        e = 0
        while (e==0):
          e = random.sample(range(1000), 1)
        array.append(e[0])

  return array


# ==============================================================================
def write_data(data, dest_path):
  # with open(os.path.join(DOCK_POINT_INPUT_HOST,name), 'w') as f:
  with open(dest_path, 'w') as f:
    f.write(data)


# ==============================================================================
def get_array_input_json_str(array):
  return json.dumps(array, indent=None, separators=(',', ':'))


# ==============================================================================
def compute_inner_product(a,b):
  result=0
  for (entry_a, entry_b) in zip(a, b):
    result += entry_a * entry_b
  return result


# ==============================================================================
def verify_results(results, modulus, array_length):
  # (0) Check consistency
  result_check = results[0]
  for result in results:
    # assure all parties got the same result :D
    assert (result == result_check)

  # (1) Verify InnerProduct result
  array_a = craft_input_array(array_length)
  array_b = craft_input_array(array_length)
  plain_ip = compute_inner_product(array_a, array_b)
  result_ref = plain_ip % modulus
  
  print(f'..Reference Result: {result_ref:,} = {plain_ip:,} mod {modulus:,}')
  bits_result = math.log(result_ref, 2)
  bits_modulus = math.log(modulus, 2)
  print('....result:  %d-bit ceiled (%.5f)' % (math.ceil(bits_result), bits_result), end='')
  print('....modulus: %d-bit ceiled (%.5f)' % (math.ceil(bits_modulus), bits_modulus))
  assert (int(result_check) == result_ref)


# ==============================================================================
# Result's JSON should look like this:
# '<b3m4>{"result":1234}</b3m4>'
def parse_result(log):
  # Benchmark data is wrapped into HTML elements
  tree = html.fromstring(str(log))
  parse_tree_str = '//%s/text()' % PARSE_MAGIC_HTML_ELEMENT
  content = tree.xpath(parse_tree_str)

  # print('got log: ', log)
  # print('HTML parsed: ', content)

  found_result = 0
  result = None
  for c in content:
    bench_json = json.loads(c)
    if ('result' in bench_json):
      result = bench_json['result']
      found_result += 1

  assert (found_result == 1)
  return result


# ==============================================================================
# Modulus' JSON should look like this:
# '<b3m4>{"modulus":4321}</b3m4>'
def parse_modulus(log):
  mod_key = 'modulus'
  # Benchmark data is wrapped into HTML elements
  tree = html.fromstring(log)
  parse_tree_str = '//%s/text()' % PARSE_MAGIC_HTML_ELEMENT
  content = tree.xpath(parse_tree_str)

  found_mod = 0
  mod = None
  for c in content:
    bench_json = json.loads(c)
    if (mod_key in bench_json):
      mod = bench_json[mod_key]
      found_mod += 1

  assert (found_mod == 1)
  return mod


# ==============================================================================
# time-log adapter for (current) natSPDZ's log output
# ...currently given as: {'timer': 1, 'time': {'sec': 0.000364141, 'ms': 0.364141}} 
def extract_time_tag_val_natSPDZ(timer_json_b4M):
  # extract time in sec
  val = timer_json_b4M['time']['sec']
  # map natSPDZ's timer id to a tag
  t_id = str(timer_json_b4M['timer'])
  tag = MPSPDZ_TIMER_IDS[t_id]
  return (tag,val)


# ==============================================================================
# Timers' JSON should look like this:
# - e.g. for the whole/full program - 
# '<b3m4>{"timer":{"full":300}}</b3m4>'
def parse_timings(log, timings, party_nr, time_unit, engine=None):
  # Benchmark data is wrapped into HTML elements
  tree = html.fromstring(log)
  parse_tree_str = '//%s/text()' % PARSE_MAGIC_HTML_ELEMENT
  content = tree.xpath(parse_tree_str)

  found_result = 0
  if (party_nr==0): print_debug('Party-0\'s log json: ', lvl=2) 

  for c in content:
    bench_json = json.loads(c)
    if (party_nr==0): print_debug('..' + str(bench_json), lvl=2) 
    if ('timer' in bench_json):
      ## extract time tag+value
      if (engine=='natSPDZ'):
        (t_tag,t_val) = extract_time_tag_val_natSPDZ(bench_json)
      else:
        bench_time = list(bench_json['timer'].items())
        assert (len(bench_time) == 1)
        t_tag = bench_time[0][0]
        t_val = bench_time[0][1]

      if (time_unit=='s'):
        # nothing to do for seconds
        pass
      elif (time_unit=='ms'):
        t_val /= 10**3
      else:
        raise NotImplementedError(f'parse_time::unit: {time_unit}')

      timings[t_tag][party_nr] = round(t_val, 3)
      found_result += 1

  assert (found_result == 3)
  # TODO!
  # ...4 timings in current ML benchmarks (full / input / ML-train / Ml-predict)
  # assert (found_result == 4)
  return timings 


# ==============================================================================
# Timers' JSON for mpSPDZ - currently - look like this:
# - e.g. for timer ID 1 - 
# '<b3m4>{"timer":1, "time":{"sec":0.3, "ms": 300}}</b3m4>'
def parse_timings_mpSZ(log, timings, party_nr):
  # Benchmark data is wrapped into HTML elements
  tree = html.fromstring(log)
  parse_tree_str = '//%s/text()' % PARSE_MAGIC_HTML_ELEMENT
  content = tree.xpath(parse_tree_str)

  found_result = 0
  for c in content:
    bench_json = json.loads(c)
    if (party_nr==0): print_debug('..' + str(bench_json), lvl=2) 

    if ('timer' in bench_json):
      assert (len(list(bench_json)) == 2)
      t_id = str(bench_json['timer'])
      t_tag = MPSPDZ_TIMER_IDS[t_id]
      t_sec = bench_json['time']['sec']

      timings[t_tag][party_nr] = round(t_sec, 3)
      found_result += 1

  assert (found_result==3) # full / input / inner_prod
  return timings 

# ==============================================================================
def parse_server_modulus(server_log):
  pass
  # pattern = re.compile("Zp: '[0-9]*'")
  # matches = pattern.findall(server_log)

  # # Assure consistency
  # ref = matches[0]
  # for match in matches:
  #   assert (match==ref)

  # # Convert to int
  # ## Now we have, e.g.: "Zp: '16777729'"
  # modulus = int( ref.split(' ')[1].replace('\'','') )
  # return modulus