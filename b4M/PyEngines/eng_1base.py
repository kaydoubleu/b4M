
import os
import sys
import math
import time

# TODO: enhance importing with package view
sys.path.insert(0,'..')
import utils as ut
import settings as st


class BaseEngine():
  # ------------------------------------------------------------------------------
  # generic benchmark settings
  PROGRAM=None
  NR_PARTIES=None
  ARRAY_LENGTH=None
  PROTO_ID=None
  NETWORK=None

  RUN_NR_CURRENT=None
  PARTY_ID_STARTS_WITH_0=None

  DOCK=None
  DOCK_NET=None
  TIMEOUT=st.PARTY_DOCKER_TIMEOUT_MIN # in minutes
  TIMEOUT_SEC=TIMEOUT*60
  RUNTIME_UNIT='s' # defauls to seconds

  ENGINE=None
  VOLUMES=None
  DOCKER_IMAGE=None
  DOCKER_CONT_NAME_PARTY=None

  REFERENCE_RESULT=None
  COMP_THRESHOLD=None
  COMP_Zp=None
  COMP_Zp_BITS=None


  # ==============================================================================
  def __init__(self):
    pass


  # ==============================================================================
  def base_init(self, dock, dock_net):
    self.DOCK=dock
    self.DOCK_NET=dock_net


  # ==============================================================================
  def load(self, prog, nr_parties, arr_length, proto_id, network):
    self.PROGRAM=prog
    self.NR_PARTIES = nr_parties
    self.ARRAY_LENGTH = arr_length
    self.PROTO_ID = proto_id
    self.NETWORK = network

    self.load_specific()
    assert(self.DOCKER_IMAGE != None)
    assert(self.ENGINE != None)
    assert(self.PARTY_ID_STARTS_WITH_0 != None)
    self.DOCKER_CONT_NAME_PARTY=f'{self.ENGINE}_party_%s'


  # ==============================================================================
  def load_specific(self):
    raise NotImplementedError('To-Be Implemented by Child Class ;)')
    # self.DOCKER_IMAGE
    # self.CMD_PARTY_SINGLE
    # self.DOCKER_CONT_NAME_PARTY


  # ==============================================================================
  def sail_specific():
    raise NotImplementedError('To-Be Implemented by Child Class ;)')


  # ==============================================================================
  def run_wrap_down_specific():
    raise NotImplementedError('To-Be Implemented by Child Class ;)')


  # ==============================================================================
  def run_note_specific(meta):
    raise NotImplementedError('To-Be Implemented by Child Class ;)')


  # ==============================================================================
  def verify_results_base(self, results, modulus):
    res_0 = results[0]
    assert (res_0 != None)

    # consistency among parties
    for res in results:
      if (res != None): assert (res == res_0)

    # compare with reference results
    mod = modulus[0]
    assert (mod != None)
    res_check = res_0 % mod 
    res_ref = self.REFERENCE_RESULT % mod

    bits_res = math.log(mod, 2)

    # TODO: 
    ut.print_debug(f'..ref result {res_ref} <--> {res_check} computed', lvl=1)
    ut.print_debug(f'..mod {self.COMP_Zp} <--> {mod} parsed', lvl=1)
    ut.print_debug(f'....bits modulus: {self.COMP_Zp_BITS}', lvl=1)
    ut.print_debug('....bits result: %.3f' % bits_res, lvl=1)

    assert (res_ref == res_check)


  # ==============================================================================
  # <parties>
  def sail_parties(self):
    ut.print_debug("..Sailing party containers...", 2)
    party_containers = []

    # input_array_computation = craft_input_array(array_length)
    # input_array_computation_str = get_JIFF_array_input_str(input_array_computation)
    # print_debug("....Crafted array for computation:\n" + input_array_computation_str, 2)
    # input_array_comp_file = 'input.txt'
    # write_input_array_to_dock_point(input_array_computation_str, input_array_comp_file)

    # input_array_null = [None]*array_length
    # input_array_null_str = get_JIFF_array_input_str(input_array_null)
    # print_debug("....Crafted \"pseudo array\" for other players:\n" + input_array_null_str, 2)
    # input_array_null_file = 'input_null.txt'
    # write_input_array_to_dock_point(input_array_null_str, input_array_null_file)

    ## create party containers
    for party_id in range(self.NR_PARTIES):
      container_name = self.DOCKER_CONT_NAME_PARTY  % str(party_id)

      ### only player 1 & 2 input an array for computation
      # if (party_id <= 2):
      #   # input_array = input_array_computation_str
      #   input_array_path = os.path.join(DOCK_POINT_INPUT_CONTAINER, input_array_comp_file)
      # else:
      #   # input_array = input_array_null_str
      #   input_array_path = os.path.join(DOCK_POINT_INPUT_CONTAINER, input_array_null_file)

      # TODO: add network setup as pre-cmd

      # if (ut.TEST_LOGS==True):
      #   cmd_run_party = CMD_PARTY_SINGLE_TEST_LOGS % party_id
      # else:
      p_id_run = party_id if (self.PARTY_ID_STARTS_WITH_0==True) else (party_id+1)
      p_id_log = party_id

      if (self.ENGINE=='JIFF'):
        base_path = self.DOCK_POINT_DATA_CONTAINER
        if (party_id==0):
          input_path = os.path.join(base_path, self.INPUT_P0)
        elif (party_id==1):
          input_path = os.path.join(base_path, self.INPUT_P1)
        else:
          input_path = os.path.join(base_path, self.INPUT_NULL)
        cmd_run_party = self.CMD_PARTY_SINGLE.format(p_id_run=p_id_run, p_id_log=p_id_log, input_path=input_path)
      else:
        cmd_run_party = self.CMD_PARTY_SINGLE.format(p_id_run=p_id_run, p_id_log=p_id_log)

      ut.print_debug("....Party CMD:\n"+cmd_run_party, 2)
      ut.print_debug(f'\n....Docker image "{self.DOCKER_IMAGE}" with volumes: {self.VOLUMES}\n', 3)
      cont_party = self.DOCK.containers.create(
                    image=self.DOCKER_IMAGE, name=container_name, command=cmd_run_party, \
                    mem_limit=ut.MEMORY_PLAIN_LIMIT_PER_PARTY, memswap_limit=ut.MEMORY_SWAP_LIMIT_PER_PARTY, \
                    cpu_count=ut.CPU_COUNT_PER_PARTY, volumes=self.VOLUMES, detach=True, \
                    cap_add=['NET_ADMIN'], \
                    #ports=ports, /
                   )
      
      ip = ut.IP_BASE + str(int(ut.IP_PARTY_START) + party_id)
      self.DOCK_NET.connect(cont_party, ipv4_address=ip)
      party_containers.append(cont_party)

    ## sail party containers
    for cont_party in party_containers:
        cont_party.start()
        ut.print_debug(f"....`{cont_party.name}` sails :)", 1)

    time.sleep(5)
    print("..Sailed party containers :D ⛵️ ...and now performing MPC 🔐🔄🙌🙃")
    return party_containers
  # </parties>


  # ==============================================================================
  # <wait-n-clean>
  # Scrub the deck :)
  def wait_for_bench_n_cleanup(self, party_containers):
    print("..Wait to finish & then start cleanup: \"scrub the deck\" :b...\n", end='', flush=True)

    nr_p = self.NR_PARTIES
    assert(nr_p==len(party_containers))
    ## Wait for party containers...
    results = [None] * nr_p 
    modulus = [None] * nr_p
    timings = {
      "full": [None] * nr_p, 
      "input": [None] * nr_p, 
      "computation": [None] * nr_p,
      # "ML-train": [None] * nr_p,
      # "ML-predict": [None] * nr_p,
      # "inner_prod": [None] * nr_p,
    } 

    ut.print_debug(f"....container timeout: {self.TIMEOUT}min\n", lvl=1)
    for (i,cont) in enumerate(party_containers):
      #print(container.name, container.status)
      try:
        ut.print_debug("....Party `%s` finished: %s" % (cont.name, str(cont.wait(timeout=self.TIMEOUT_SEC))), 1)
        finished = True
      except:
        print("....Party `%s` ran into a timeout (%ds)" % (cont.name, self.TIMEOUT_SEC))
        print("....Container logs: ", cont.logs())
        cont.stop()
        finished = False
      
      ut.print_debug("......Cont. Logs: "+str(cont.logs()), 1)

      party_id = int(cont.name.split('_')[2])
      log_path = ut.os.path.join(ut.DOCK_POINT_LOGS_HOST, ut.PARTY_LOGS%str(party_id) )
      with open(log_path, mode='r') as f:
        logs = f.read()

      results[party_id] = ut.parse_result(logs) #if (finished==True) else None

      # TODO: unify parsing! adapt webSZ's/mpSZ's logging/parsing :)
      if (self.ENGINE=='JIFF'):
        modulus[party_id] = ut.parse_modulus(logs) #if (finished==True) else None
      else:
        modulus = None

      # TODO: unify parsing! adapt mpSZ's logging/parsing :)
      # if (self.ENGINE=='mpSPDZ'):
        # timings = ut.parse_timings_mpSZ(logs, timings, party_id) #if (finished==True) else None
      # else:
      timings = ut.parse_timings(logs, timings, party_id, time_unit=self.RUNTIME_UNIT,
                                 engine=self.ENGINE) #if (finished==True) else None

      ## Since the run/create argument 'auto_removal' seems to be "too fast"/does not work
      ## - at least in 2023 - remove the containers manually
      if (ut.REMOVE_DOCKER_CONTAINERS==True): cont.remove()
    # end-for: enumerate(party_containers)

    self.run_wrap_down_specific()

    print("..Finished scrubbing! 🧼")
    return (results, modulus, timings)
  # </wait-n-clean>


  # ==============================================================================
  def run(self, run_nr):
    self.RUN_NR_CURRENT = run_nr
    # pre-cleanup 🧼
    ut.clean_dir(ut.DOCK_POINT_LOGS_HOST)
    # sail parties :) ⛵️
    self.sail_specific()
    cont_parties = self.sail_parties()

    (results, modulus, timings) = self.wait_for_bench_n_cleanup(cont_parties)
    if (modulus != None):
      self.verify_results_base(results, modulus)

    meta = {
      "docker_img": self.DOCKER_IMAGE,
      "computation": {
        "threshold": self.COMP_THRESHOLD,
        "Zp_bits": self.COMP_Zp_BITS,
        "Zp": self.COMP_Zp,
      },
      "RAM": {
         "parties": ut.MEMORY_PLAIN_LIMIT_PER_PARTY,
      },
      "CPU": {
         "parties": ut.CPU_COUNT_PER_PARTY,
      },
    }
    meta = self.run_note_specific(meta)

    return (results, meta, timings)

