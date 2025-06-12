
import os
import sys 
import math

# if __package__ is None or __package__ == '':
    # current directory visibility
sys.path.insert(0, '..')
import utils as ut
from PyEngines.eng_1base import BaseEngine
# else:
#     # current package visibility
#     print("package: ", __package__)
#     from .. import utils as ut


class JIFF_engine(BaseEngine):
  # ------------------------------------------------------------------------------
  # engine benchmark settings


  # ##############################################################################
  # (Docker) Network Setup

  # ##############################################################################
  # Docker-Container / Run Settings

  DOCK_POINT_LOGS_CONTAINER='/root/Dock-Point/Logs'
  DOCK_POINT_DATA_CONTAINER='/root/Dock-Point/Share-Data'
  INPUT_P0='Input-P0-share'
  INPUT_P1='Input-P1-share'
  INPUT_NULL='Input-Pk-null'
  CMD_PARTY_SINGLE=None

  DOCKER_CONT_NAME_SERVER='JIFF_server'
  cont_server=None
  MEMORY_PLAIN_LIMIT_SERVER='8G' 
  MEMORY_SWAP_LIMIT_SERVER='8G'
  CPU_COUNT_SERVER=8

  SERVER_IP=ut.IP_BASE + '9'
  SERVER_PORT=8080


  ## =============================================================================
  ## Meta Stuff (image name, ..) 

  # BIT_LENGTH_FIELD=128 # e.g., for Shamir


  # ==============================================================================
  def __init__(self):
    pass


  # ==============================================================================
  def load_specific(self):
    # Resources (CPU/RAM)
    cpu_count_max_parties = ut.CPU_COUNT_MAX - self.CPU_COUNT_SERVER
    assert( (self.NR_PARTIES*ut.CPU_COUNT_PER_PARTY) <= cpu_count_max_parties ) 

    # Docker Volumes
    DOCK_POINT_VOLUME_LOGS=f'{ut.DOCK_POINT_LOGS_HOST}:{self.DOCK_POINT_LOGS_CONTAINER}'
    DOCK_POINT_VOLUME_DATA=f'{ut.DOCK_POINT_DATA_HOST}:{self.DOCK_POINT_DATA_CONTAINER}'
    self.VOLUMES=[DOCK_POINT_VOLUME_LOGS, DOCK_POINT_VOLUME_DATA]
    
    # Setup CMDs for compilation & running
    if (self.PROTO_ID=='0'): # Shamir Pasive
      pass
    else:
      raise NotImplementedError('TODO support protocol: ', self.PROTO_ID)

    # CMD Compilation
    self.CMD_SERVER = '"node server.js"' 

    ## CMD Running
    comp_id = self.PROGRAM.replace(' ', '_')
    self.COMP_THRESHOLD=(math.ceil(self.NR_PARTIES / 2)) - 1
    # self.COMP_Zp=2315809577 # 32-bit 
    self.COMP_Zp=242637933131953 # 48-bit 
    # self.COMP_Zp=901817040935953 # 50-bit  
    # self.COMP_Zp=3535085106025729 # 52-bit
    # self.COMP_Zp=6261746364402779 # 53-bit # <-- works until here (for JIFF) 
    # self.COMP_Zp=9219123647033857 # 54-bit 
    # self.COMP_Zp=273222403014604579 # 58-bit 
    # self.COMP_Zp=659695699644571171 # 60-bit 
    # self.COMP_Zp=18446744073709551557 # 64-bit 
    # self.COMP_Zp=15602070592323557773 # 64-bit 
    # self.COMP_Zp=209195226289509098368867143132480695659 # 128-bit
    # self.COMP_Zp=179909201198258201664936577809428725721 # 128-bit
    # self.COMP_Zp=277377802911579465915177789534932614073 # 128-bit 
    self.COMP_Zp_BITS = '%.3f' % math.log(self.COMP_Zp, 2)

    ut.print_debug(lvl=1, text='JIFF CMD: '\
                   '// node party.js <server_IP> <server_PORT> <input_path> <nr_parties> <comp_id> <p_id>'\
                    ' <threshold> <Zp>')
    cmd_run = f'node party.js {self.SERVER_IP} {self.SERVER_PORT} {{input_path}} {self.NR_PARTIES} {comp_id}'\
            + f' {{p_id_run}} {self.COMP_THRESHOLD} {self.COMP_Zp}'
    self.CMD_PARTY_SINGLE=f'"{cmd_run} > {self.DOCK_POINT_LOGS_CONTAINER}/party_{{p_id_log}}.log 2>&1"'

    # Engine Meta
    self.ENGINE = 'JIFF'
    self.DOCKER_IMAGE='jiff_sok_2024_oct_thr_zp' 
    # self.DOCKER_IMAGE='jiff_sok_2024_oct_thr' 
    # self.DOCKER_IMAGE='jiff_sok_2024_oct' 
    # self.DOCKER_IMAGE='jiff_sok' 
    self.PARTY_ID_STARTS_WITH_0=False

    self.RUNTIME_UNIT='ms'
    self.TIMEOUT=30 # 30min
    self.TIMEOUT_SEC=self.TIMEOUT*60


  # ==============================================================================
  def craft_json_array_str(self, p_type):
    if (p_type=='share'):
      arr = ut.craft_input_array(self.ARRAY_LENGTH)
    elif (p_type=='null'):
      arr = ut.craft_input_array(self.ARRAY_LENGTH, nullify=True)
    else:
      raise NotImplementedError(f'JIFF array_str player type: {p_type}')

    arr_j_str = ut.get_json_string(arr) 
    return (arr_j_str, arr)


  # ==============================================================================
  def craft_network_file(self):
    s = '\n'.join(ut.IP_BASE+str(10+p) for p in range(self.NR_PARTIES))
    return s


  # ==============================================================================
  def prepare_program(self):
    # prepare parties input
    (arr_0_str, arr_0) = self.craft_json_array_str(p_type='share')
    (arr_1_str, arr_1) = self.craft_json_array_str(p_type='share')
    (arr_null_str, arr_null) = self.craft_json_array_str(p_type='null')

    ut.write_data(arr_0_str, os.path.join(ut.DOCK_POINT_DATA_HOST, self.INPUT_P0))
    ut.write_data(arr_1_str, os.path.join(ut.DOCK_POINT_DATA_HOST, self.INPUT_P1))
    ut.write_data(arr_null_str, os.path.join(ut.DOCK_POINT_DATA_HOST, self.INPUT_NULL))

    # store reference result
    self.REFERENCE_RESULT=ut.compute_inner_product(arr_0, arr_1)

    return True


  # ==============================================================================
  # <JIFF server>
  def sail_server(self):
    ut.print_debug("..Sail the JIFF server..", 1)
    ## Start the Server
    port_to_publish = self.SERVER_PORT 
    ports={port_to_publish : port_to_publish}
    
    self.cont_server = self.DOCK.containers.create(\
                    image=self.DOCKER_IMAGE, name=self.DOCKER_CONT_NAME_SERVER, command=self.CMD_SERVER, \
                    mem_limit=self.MEMORY_PLAIN_LIMIT_SERVER, memswap_limit=self.MEMORY_SWAP_LIMIT_SERVER, \
                    cpu_count=self.CPU_COUNT_SERVER, detach=True, \
                    ports=ports \
                  )

    self.DOCK_NET.connect(self.cont_server, ipv4_address=self.SERVER_IP)
    self.cont_server.start()
    
    print("..JIFF server is sailing ⛵") 
    return True
  # </JIFF server>


  # ==============================================================================
  def sail_specific(self):
    # prepare program input only once per benchmark setting :)
    if (self.RUN_NR_CURRENT==0):
      ut.clean_dir(ut.DOCK_POINT_DATA_HOST)
      if (self.prepare_program() != True): sys.exit(-1)
    
    # server is always needed
    if (self.sail_server() == False): sys.exit(-1)


  # ==============================================================================
  def run_wrap_down_specific(self):
    ## ...Then also cleanup the server
    # logs_server = self.cont_server.logs()
    self.cont_server.stop()
    ut.print_debug("....Server stopped 🛬", 1)
    # modulus = parse_server_modulus(str(server_wSZ_app_container.logs()))
    if (ut.REMOVE_DOCKER_CONTAINERS==True):
      self.cont_server.remove()


  # ==============================================================================
  def run_note_specific(self, meta):
    meta["RAM"]["server"] = self.MEMORY_PLAIN_LIMIT_SERVER
    meta["CPU"]["server"] = self.CPU_COUNT_SERVER

    return meta
    
