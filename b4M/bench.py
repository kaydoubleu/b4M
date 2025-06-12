
import os
import sys
import time
import json
# import math
import docker

# import regex as re
import itertools as iter

# from lxml import html
from tqdm import tqdm # e.g., benchmarking progress bar in terminal output :)

if __package__ is None or __package__ == '':
    # current directory visibility
    import view as vw
    import utils as ut
    import settings as st
    import PyEngines.eng_webSPDZ as eng_wSZ
else:
    # current package visibility
    from . import view as vw
    from . import utils as ut
    from . import settings as st
    from .PyEngines import eng_webSPDZ as eng_wSZ


# ==============================================================================
def store_benchmark(engine, fname, meta, timings):
  data = {}
  data['timings'] = timings
  t = time.localtime()
  # TODO: fix meta storage: 
  # ...take meta as it comes - to also store engine-specific stuff - 
  # ...and add additional stuff as needed (e.g., time...)
  data['_meta'] = {
    # 'time_stored': f'{t[0]}-{t[1]}-{t[2]}_{t[3]}-{t[4]}',
    'time_stored': f'2025-Q1',
    'docker_img': meta['docker_img'],
    'computation': meta['computation'],
    'RAM': meta['RAM'],
    'CPU': meta['CPU'],
  }

  # check if file exists
  fdir = os.path.join(ut.DATA_DIR, engine)
  if (ut.check_file_exists(fdir, fname) == True):
    print('Storage Error: File already exists!', engine, fname)
    sys.exit(-1)

  # store
  with open(os.path.join(fdir,fname), 'w') as f:
    j_str = json.dumps(data, indent=2, separators=(',', ':'))
    f.write(j_str)


# ==============================================================================
# NOTE: returned 'meta' object from engine is (currently) thought to be always the same
def run_engine_parse_results(eng, nr_runs):
  nr_parties = eng.NR_PARTIES

  # run the engine (: 🏃‍♂️‍➡️
  # iterate #nr_runs & average :)
  res_ref = None
  avg_timings = {
    "full": [0]*nr_parties,
    "input": [0]*nr_parties,
    "computation": [0]*nr_parties,
    # "ML-train": [0]*nr_parties,
    # "ML-predict": [0]*nr_parties,
  }
  run_timings = {}

  for run_nr in range(nr_runs):
    print('-'*80)
    print(f"RUN NR: {run_nr+1}")

    (result, meta, timings) = eng.run(run_nr) # 🏃‍♂️‍➡️

    run_timings[str(run_nr)] = timings

    # ensure all parties have the same result(s)
    assert(result!=None)
    if (res_ref==None):
      res_ref = result
    else:
      print('DBG: result got: ', result)
      print('DBG: result ref: ', res_ref)
      # assert(result==res_ref)

    # timings
    assert(len(timings['full']) == nr_parties)
    for p_id in range(nr_parties):
      t_full = timings['full'][p_id]
      t_input = timings['input'][p_id]
      # t_ml_train = timings['ML-train'][p_id]
      # t_ml_predict = timings['ML-predict'][p_id]
      t_comp = timings['computation'][p_id]
      # t_inner_prod = timings['inner_prod'][p_id]
      assert(t_full!=None)
      avg_timings['full'][p_id] += (t_full / nr_runs)
      avg_timings['input'][p_id] += (t_input / nr_runs)
      # avg_timings['ML-train'][p_id] += (t_ml_train / nr_runs)
      # avg_timings['ML-predict'][p_id] += (t_ml_predict / nr_runs)
      avg_timings['computation'][p_id] += (t_comp / nr_runs)
      # avg_timings['inner_prod'][p_id] += (t_inner_prod / nr_runs)
    #for-end: p_id
  #for-end: run_nr

  # round final averages
  for p_id in range(nr_parties):
    avg_timings['full'][p_id] = round(avg_timings['full'][p_id], 3)
    avg_timings['input'][p_id] = round(avg_timings['input'][p_id], 3)
    # avg_timings['ML-train'][p_id] = round(avg_timings['ML-train'][p_id], 3)
    # avg_timings['ML-predict'][p_id] = round(avg_timings['ML-predict'][p_id], 3)
    avg_timings['computation'][p_id] = round(avg_timings['computation'][p_id], 3)
    # avg_timings['inner_prod'][p_id] = round(avg_timings['inner_prod'][p_id], 3)

  data_timings = {
    "avg": avg_timings,
    "runs": run_timings,
  }
  return (meta, data_timings)


# ==============================================================================
def base_init_engines():
  # Get Docker..
  ## ..client
  dock = ut.get_docker_client() 
  ## ..network
  dock_net = ut.get_docker_network(dock)

  for eng in st.ENGINES.items():
    eng[1].base_init(dock=dock, dock_net=dock_net)


# ==============================================================================
def get_bms():
  return iter.product(st.PROGRAMS, st.NR_PLAYERS, st.ARRAY_LENGTHS, st.PROTOCOLS, st.ENGINES, st.NETWORKS)


# ==============================================================================
def benchmark():
  bms = list(get_bms())
  base_init_engines()

  with tqdm(total=len(bms), desc='All benchmark permutations (') as t:
    # for iteration in iter.product(NR_PLAYERS, ARRAY_LENGTHS, PROTOCOLS, ENGINES, NETWORKS):
    for iteration in bms:
      prog=iteration[0]
      nr_parties=iteration[1]
      arr_length=iteration[2]
      proto_id=iteration[3]
      engine=iteration[4]
      network=iteration[5]

      nr_runs = st.NR_RUNS_PER_SETTING

      proto = ut.PROTO_MAP[proto_id]
      data_fname = ut.get_json_file_name(prog=prog, engine=engine, protocol=proto, network=network,
                                         nr_parties=nr_parties, arr_length=arr_length,
                                         nr_runs=nr_runs)
      print('#'*80)
      print('Benchmarking: ', os.path.join(ut.DATA_DIR_DEST, data_fname))

      # sanity checks prior running
      data_dir = os.path.join(ut.DATA_DIR, engine)
      if (ut.check_file_exists(data_dir, data_fname) == True):
        print('Benchmarking file to approach already exists?! ')#, data_fname)
        continue

      # 🧘‍♂ load the engine ️
      eng = st.ENGINES[engine]
      eng.load(prog=prog, nr_parties=nr_parties, arr_length=arr_length, proto_id=proto_id, network=network)
      print('...using Docker Image: ', eng.DOCKER_IMAGE)

      # 🏃‍♂️‍➡️ run the engine (:
      (data_meta, data_timings) = run_engine_parse_results(eng, nr_runs)
      store_benchmark(engine, data_fname, data_meta, data_timings)

      t.update()
      # end-for: bms' iterations
  
  # cleanup after
  if (ut.CLEANUP_DATA_LOGS_AFTER_BENCH==True):
    ut.clean_dir(ut.DOCK_POINT_LOGS_HOST)
    ut.clean_dir(ut.DOCK_POINT_DATA_HOST)


# ==============================================================================
def craft_graphs():
  for gr in st.GRAPHS_RUNTIME:
    ut.print_debug(gr, lvl=3)
    if (gr['active'] == 0):
      continue # process only if 'active'==1 (!=0)

    gr_st = gr['settings']
    st.PROTOCOLS=gr_st['PROTOCOLS']
    st.NR_PLAYERS=gr_st['NR_PLAYERS']
    st.ARRAY_LENGTHS=gr_st['ARRAY_LENGTHS']
    st.NETWORKS=gr_st['NETWORKS']
    st.ENGINES=gr_st['ENGINES']

    # for each program:
    for program in gr_st['PROGRAMS']:
      print(f"crafting runtime graphs for '{program}'")

      # get current benchmark-setting view
      st.PROGRAMS=[program]
      bms = get_bms()

      graph_title = gr_st['GRAPH_TITLE'].format(program=program)
      graph_dir = os.path.join(ut.GRAPH_DIR, gr_st['DIR_SUBPATH'].format(program=program))
      if (os.path.isdir(graph_dir)==False): os.mkdir(graph_dir)


      vw.create_graph_runtime(bms=bms, nr_runs=st.NR_RUNS_PER_SETTING, program=program, 
                              graph_dir=graph_dir, graph_title=graph_title,
                              x_axis=gr['X-axis'], x_label=gr['X-label'],
                              line_color=gr['line-color'], line_style=gr['line-style'],
                              legend_title=gr['legend-title']
                             )
    

# ==============================================================================
def remove_all_Docker_containers():
  dock = docker.from_env() # get client

  # remove all containers programmatically :D
  for c in dock.containers.list(all=True):
      c.stop()
      c.remove()


# ==============================================================================
def bench_prog(prog, protocols, bench_test=False):
  st.PROGRAMS=[prog]

  ###########################
  # Initial Benchmark Testing
  if (bench_test == True):
    print('\n', '#'*80, f'Benchmarking Test for {st.PROGRAMS}')
    # st.ARRAY_LENGTHS=[ 10**0 ]
    st.ARRAY_LENGTHS=[ 1 ]
    # st.ARRAY_LENGTHS=[ 10**1 ]
    # st.NR_PLAYERS=[3]
    st.NR_PLAYERS=[4]
    st.PROTOCOLS=protocols # Shamir-Active (9)
    benchmark() # 🏃‍♂️
    sys.exit(0)
  ###########################

  ## Use Case: 3/4 parties ... #array length
  # st.ARRAY_LENGTHS=[
  #   # 10**0, 10**1, 10**2, 10**3, 10**4, 10**5, 10**6,
  #   1, 2, 3, 4, 5 
  # ]
  # st.NR_PLAYERS=[3]
  # st.PROTOCOLS=['0', '1'] # Shamir-Passive (0), Rep3Ring (1)
  # print('\n', '#'*80, 'Benchmarking 3P / #array / (Shamir Passive & Rep3)')
  # benchmark() # 🏃‍♂️
  # st.NR_PLAYERS=[4]
  # st.PROTOCOLS=['9', '2'] # Shamir-Active (9), Rep4Ring (2)
  # print('\n', '#'*80, 'Benchmarking 4P / #array / (Shamir Active & Rep4)')
  # benchmark() # 🏃‍♂️

  ## Use Case: #parties ... 10^5 array legnth
  # st.NR_PLAYERS=[3,4,5,6,7,8,9,10,11,12,13]
  st.NR_PLAYERS=[10,11,12,13]
  prog_input = [10**5]
  # prog_input = [1]
  st.ARRAY_LENGTHS=prog_input
  st.PROTOCOLS=protocols
  print('\n', '#'*80, f'Benchmarking {prog}: #P / {prog_input}ProgInput / {protocols}')
  benchmark() # 🏃‍♂️


# ==============================================================================
def main():
  if (len(sys.argv) > 1):
    # going 1-by-1 through list to enable ordered commands (:
    # ...e.g., rm containers --then-> benchmarking 
    for arg in sys.argv:
      # ⛵🏃‍♂️🏋️‍♂️ run/sail the benchmarks? (:
      if (arg=='run') or (arg=='sail'):
        # ASIT TGV 25-1 benches:
        # ...for each program:

        bench_test = False
        # bench_test = True

        # st.PROGRAMS=['dot_product']
        # st.PROGRAMS=['BB-multiplication']
        # st.PROGRAMS=['BB-addition']
        # bench_prog('BB-array-min', bench_test=bench_test)
        # bench_prog('BB-array-max', bench_test=bench_test)
        # bench_prog('BB-array-average', bench_test=bench_test)
        protocols = ['0'] # Shamir-Passive (0)
        bench_prog(prog='BB-Dot-Product', protocols=protocols, bench_test=bench_test)
        # protocols = ['10', '11'] # MASCOT (10), semi2 (11)
        # protocols = ['10'] 
        # bench_prog(prog='LogReg-Breast-Cancer', protocols=protocols, bench_test=bench_test)
        # bench_prog('logreg_test', bench_test=bench_test)

      # 🧼⛴️ cleanup/remove all Docker containers?
      elif (arg=='rmc'):
        remove_all_Docker_containers()
      # 🏞️📊 craft graphs? :)
      elif (arg=='graphs'):
        craft_graphs()


# ==============================================================================
if __name__=="__main__":
  main()


