
import os
import sys

# if __package__ is None or __package__ == '':
    # current directory visibility
sys.path.insert(0, '..')
import utils as ut
from PyEngines.eng_1base import BaseEngine
# else:
#     # current package visibility
#     print("package: ", __package__)
#     from .. import utils as ut


class natSPDZ_engine(BaseEngine):
  # ------------------------------------------------------------------------------
  # engine benchmark settings

  # PROTO_TO_BINARY={
  #   '0': './shamir-party.x', # Shamir Passive
  #   '1': # Replicated Ring
  # }

  # ##############################################################################
  # (Docker) Network Setup

  # ##############################################################################
  # Docker-Container / Run Settings

  MEMORY_PLAIN_LIMIT_COMPILATION='8G' 
  MEMORY_SWAP_LIMIT_COMPILATION='8G'
  TIMEOUT_COMPILATION_SEC=5*60 # 5 minutes

  ## =============================================================================
  ## Docker Meta Stuff (image name, ...) 
  DOCKER_IMAGE='mp_spdz_v0_4_0_from_2024_nov_ubuntu_all_protos' 
  # self.DOCKER_IMAGE='mp_spdz_v0_3_9_2024_june_20_ubuntu_all_protos' 
  DOCKER_CONT_NAME_COMPILE='natSPDZ_compilation'

  PROG_SUFFIX='.mpc'

  DOCK_POINT_LOGS_CONTAINER='/home/MP-SPDZ/Dock-Point/Logs'
  DOCK_POINT_DATA_CONTAINER='/home/MP-SPDZ/Dock-Point/Share-Data'

  BIT_LENGTH_FIELD=128 # e.g., for Shamir
  BIT_LENGTH_RING=128 # e.g., for Rep. Ring
  CMD_COMPILE=None
  CMD_PARTY_SINGLE=None

  NETWORK_FILE='NetworkData.txt'


  # ==============================================================================
  def __init__(self):
    pass


  # ==============================================================================
  def load_specific(self):
    # Resources (CPU/RAM)
    # cpu_count_max_parties = ut.CPU_COUNT_MAX - self.CPU_COUNT_SERVERS
    # assert( (self.NR_PARTIES*ut.CPU_COUNT_PER_PARTY) <= cpu_count_max_parties ) 
    assert( (self.NR_PARTIES*ut.CPU_COUNT_PER_PARTY) <= ut.CPU_COUNT_MAX ) 

    # Docker Volumes
    DOCK_POINT_VOLUME_LOGS=f'{ut.DOCK_POINT_LOGS_HOST}:{self.DOCK_POINT_LOGS_CONTAINER}'
    DOCK_POINT_VOLUME_DATA=f'{ut.DOCK_POINT_DATA_HOST}:{self.DOCK_POINT_DATA_CONTAINER}'
    self.VOLUMES=[DOCK_POINT_VOLUME_LOGS, DOCK_POINT_VOLUME_DATA]
    
    # Setup CMDs for compilation & running
    if (self.PROTO_ID=='0'): # Shamir Pasive
      binary = 'shamir-party.x'
      options_compile = f'--field={self.BIT_LENGTH_FIELD}'
      options_run = f'-N {self.NR_PARTIES}'
    elif (self.PROTO_ID=='1'): # Replicated Ring (Pasive)
      binary = 'replicated-ring-party.x'
      options_compile = f'--ring={self.BIT_LENGTH_RING}'
      options_run = f'--ring {self.BIT_LENGTH_RING}'
    elif (self.PROTO_ID=='2'): # Replicated 4 Ring (Active)
      binary = 'rep4-ring-party.x'
      options_compile = f'--ring={self.BIT_LENGTH_RING}'
      options_run = f'--ring {self.BIT_LENGTH_RING}'
    elif (self.PROTO_ID=='9'): # Shamir Active  
      binary = 'malicious-shamir-party.x'
      options_compile = f'--field={self.BIT_LENGTH_FIELD}'
      options_run = f'-N {self.NR_PARTIES}'
    elif (self.PROTO_ID=='10'): # MASCOT
      binary = 'mascot-party.x'
      options_compile = f'--field={self.BIT_LENGTH_FIELD}'
      options_run = f'-N {self.NR_PARTIES}'
    elif (self.PROTO_ID=='11'): # semi2
      binary = 'semi-party.x'
      options_compile = f'--field={self.BIT_LENGTH_FIELD}'
      options_run = f'-N {self.NR_PARTIES}'
    else:
      raise NotImplementedError('TODO support protocol: ', self.PROTO_ID)

    # CMD Compilation
    prog = self.PROGRAM + self.PROG_SUFFIX
    cmd_compile_pre = f'cp {self.DOCK_POINT_DATA_CONTAINER}/{prog} Programs/Source/'
    cmd_compile = f'./compile.py {options_compile} {self.PROGRAM} {self.ARRAY_LENGTH}'\
                + f' > {self.DOCK_POINT_LOGS_CONTAINER}/compile.log 2>&1'
    # cmd_compile_post = f'cp Programs/{{Bytecode,Schedules}}/{self.PROGRAM}* {self.DOCK_POINT_DATA_CONTAINER}'
    ## to copy also Player's binary data:
    cmd_compile_post = f'cp Programs/{{Bytecode,Schedules}}/{self.PROGRAM}* {self.DOCK_POINT_DATA_CONTAINER} && cp Player-Data/Input-Binary* {self.DOCK_POINT_DATA_CONTAINER}'
    self.CMD_COMPILE = f'"{cmd_compile_pre} && {cmd_compile} && {cmd_compile_post}"'

    ## CMD Running
    cmd_run_pre = f'cp {self.DOCK_POINT_DATA_CONTAINER}/Input* Player-Data/'\
                + f' && cp {self.DOCK_POINT_DATA_CONTAINER}/{self.NETWORK_FILE} Player-Data/'\
                + f' && cp {self.DOCK_POINT_DATA_CONTAINER}/{self.PROGRAM}*.bc Programs/Bytecode'\
                + f' && cp {self.DOCK_POINT_DATA_CONTAINER}/{self.PROGRAM}*.sch Programs/Schedules'

    # `-OF '.'` to have stdout for all parties :)
    cmd_run = f'./{binary} --output-file \'.\' --ip-file-name Player-Data/{self.NETWORK_FILE} {options_run}'\
            + f' {{p_id_run}} {self.PROGRAM}-{self.ARRAY_LENGTH}'
    
    # cmd_run_post = f''
    # cmd_run_post = f'ls Player-Data'

    # && {cmd_run_post}
    self.CMD_PARTY_SINGLE=f'"{cmd_run_pre} && {cmd_run} > {self.DOCK_POINT_LOGS_CONTAINER}/{ut.PARTY_LOGS_FORMAT} 2>&1"'

    # Engine Meta
    self.ENGINE = 'natSPDZ'
    self.PARTY_ID_STARTS_WITH_0=True


  # # ==============================================================================
  # def craft_array_str(self):
  #   arr = ut.craft_input_array(self.ARRAY_LENGTH)
  #   arr_str = ' '.join(str(e) for e in arr)
  #   return arr_str


  # ==============================================================================
  def craft_network_file(self):
    s = '\n'.join(ut.IP_BASE+str(10+p) for p in range(self.NR_PARTIES))
    return s


  # ==============================================================================
  def prepare_program(self):
    # copy .mpc to shared folder :)
    src_prog_path = os.path.join(ut.DOCK_POINT_PROGRAMS_HOST, self.PROGRAM+self.PROG_SUFFIX)
    dest_path = ut.DOCK_POINT_DATA_HOST 
    ut.copy_file(src_path=src_prog_path, dest_path=dest_path)

    # prepare parties input
    # arr_1_str = self.craft_array_str()
    # arr_2_str = self.craft_array_str()
    # ut.write_data(arr_1_str, os.path.join(ut.DOCK_POINT_DATA_HOST, 'Input-P0-0'))
    # ut.write_data(arr_2_str, os.path.join(ut.DOCK_POINT_DATA_HOST, 'Input-P1-0'))
    dest_path = ut.DOCK_POINT_DATA_HOST 
    src_arr_1_path = os.path.join(ut.DOCK_POINT_PROGRAMS_HOST, 'Input-P0-0')
    src_arr_2_path = os.path.join(ut.DOCK_POINT_PROGRAMS_HOST, 'Input-P1-0')
    ut.copy_file(src_path=src_arr_1_path, dest_path=dest_path)
    ut.copy_file(src_path=src_arr_2_path, dest_path=dest_path)

    # src_binary_0_path = os.path.join(ut.DOCK_POINT_PROGRAMS_HOST, 'Input-Binary-P0-0')
    # ut.copy_file(src_path=src_binary_0_path, dest_path=dest_path)

    # prepare network file
    dest_path = os.path.join(ut.DOCK_POINT_DATA_HOST, self.NETWORK_FILE)
    net_file = self.craft_network_file()
    ut.write_data(data=net_file, dest_path=dest_path)


  # ==============================================================================
  # <natSPDZ's compilation>
  def sail_compilation(self):
    # print("..Sail mpSPDZ's compilation..", end='', flush=True)
    ut.clean_dir(ut.DOCK_POINT_DATA_HOST) 
    self.prepare_program()
    print('cmd compile: ', self.CMD_COMPILE)
    cont_compilation = self.DOCK.containers.create(
                        image=self.DOCKER_IMAGE, name=self.DOCKER_CONT_NAME_COMPILE, command=self.CMD_COMPILE,
                        mem_limit=self.MEMORY_PLAIN_LIMIT_COMPILATION, memswap_limit=self.MEMORY_SWAP_LIMIT_COMPILATION,
                        # cpu_count=ut.CPU_COUNT_PER_PARTY, 
                        detach=True,
                        volumes=self.VOLUMES,
                       )

    cont_compilation.start()
    print("..natSPDZ's compilation is sailing ⛵", flush=True) 

    try:
      ut.print_debug("..natSPDZ's compilation finished :) 🛬" 
                     + "(%s)" % (str(cont_compilation.wait(timeout=self.TIMEOUT_COMPILATION_SEC))), 1)
    except:
      print("..natSPDZ's compilation failed 🛑") 
      print("....Container logs: ", cont_compilation.logs())
      cont_compilation.stop()
      return False
    
    cont_compilation.remove()

    return True 
  # </natSPDZ's compilation>


  # ==============================================================================
  def sail_specific(self):
    # compile only once per benchmark setting :)
    if (self.RUN_NR_CURRENT==0) and (self.sail_compilation() == False): sys.exit(-1)


  # ==============================================================================
  def run_wrap_down_specific(self):
    ## ...Then also cleanup the servers
    # logs_server_app = server_wSZ_app_container.logs()
    # self.cont_server_app.stop()
    # ut.print_debug("....Servers stopped", 1)
    # modulus = parse_server_modulus(str(server_wSZ_app_container.logs()))
    # server_container.remove() if (REMOVE_DOCKER_CONTAINERS==True)  
    # if (ut.REMOVE_DOCKER_CONTAINERS==True): 
    #   self.cont_server_app.remove() 
    pass


  # ==============================================================================
  def run_note_specific(self, meta):
    # meta["RAM"]["server_app"] = self.MEMORY_PLAIN_LIMIT_SERVER_wSZ_APP,
    # meta["CPU"]["server_app"] = self.CPU_COUNT_SERVER_wSZ_APP,

    return meta
    