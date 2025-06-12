
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


class webSPDZ_engine(BaseEngine):
  # ------------------------------------------------------------------------------
  # engine benchmark settings

  # ##############################################################################
  # (Docker) Network Setup
  APP_SERVER_IP=ut.IP_BASE+'8'
  APP_SERVER_PORT='8080'
  SIGNALING_SERVER_IP=ut.IP_BASE+'9'
  SIGNALING_SERVER_PORT='8089'

  # ##############################################################################
  # Docker-Container / Run Settings
  DOCK=None
  DOCK_NET=None

  MEMORY_PLAIN_LIMIT_SERVER_wSZ_APP='4G'
  MEMORY_SWAP_LIMIT_SERVER_wSZ_APP='4G'
  CPU_COUNT_SERVER_wSZ_APP=4

  MEMORY_PLAIN_LIMIT_SERVER_SIGNALING='4G'
  MEMORY_SWAP_LIMIT_SERVER_SIGNALING='4G'
  CPU_COUNT_SERVER_SIGNALING=4
  CPU_COUNT_SERVERS = CPU_COUNT_SERVER_wSZ_APP + CPU_COUNT_SERVER_SIGNALING

  ## =============================================================================
  ## Meta Stuff (image name, ..) 
  DOCKER_CONT_NAME_SERVER_wSZ_app='webSPDZ_app_server'
  DOCKER_CONT_NAME_SERVER_SIGNALING='WebRTC_signaling_server'
  DOCKER_CONT_NAME_PARTY='webSPDZ_party_%s'

  # DOCK_POINT_LOGS_CONTAINER='/webSPDZ-64/Logs'
  # DOCK_POINT_LOGS_CONTAINER='/home/webSPDZ-64/Logs'
  DOCK_POINT_LOGS_CONTAINER='/home/webSPDZ/Logs'

  CMD_SERVER_wSZ_APP='"bash run_webSPDZ-app-server.sh"'
  CMD_SERVER_SIGNALING='"bash run_WebRTC-signaling-server.sh"'
  CMD_PARTY_SINGLE=None
  CMD_PARTY_SINGLE_TEST_LOGS='"bash craft_test-logs.sh %s"'

  cont_server_app = None
  cont_server_signaling = None


  # ==============================================================================
  def __init__(self):
    # proto = 'None' #self.PROTO_MAP[str(self.PROTO_ID)]
    # print("JSON name: ", ut.get_json_file_name(self.ENGINE, proto, self.NR_PARTIES, 1, self.NETWORK, self.NR_RUNS))
    pass


  # ==============================================================================
  def load_specific(self):
    # Resources (RAM/CPU)
    cpu_count_max_parties = ut.CPU_COUNT_MAX - self.CPU_COUNT_SERVERS
    assert( (self.NR_PARTIES*ut.CPU_COUNT_PER_PARTY) <= cpu_count_max_parties ) 

    # Docker Volumes
    DOCK_POINT_VOLUME_LOGS=f'{ut.DOCK_POINT_LOGS_HOST}:{self.DOCK_POINT_LOGS_CONTAINER}'
    self.VOLUMES=[DOCK_POINT_VOLUME_LOGS]

    # ...party-single.sh: <nr_parties> <party_id> <protocol> <array_size> 
    self.CMD_PARTY_SINGLE=f'"bash run_webSPDZ-party-single.sh {self.NR_PARTIES} {{p_id_run}} {self.PROTO_ID} {self.ARRAY_LENGTH}"'

    # Engine Meta
    self.ENGINE='webSPDZ'
    self.DOCKER_IMAGE='webspdz_ubuntu24'
    # self.DOCKER_IMAGE='webspdz-64_ubuntu_firefox' 
    # self.DOCKER_IMAGE='webspdz-64_ubuntu_oct-30_new-firefox'
    # self.DOCKER_IMAGE='webspdz-64_ubuntu_oct-30'
    # self.DOCKER_IMAGE='webspdz-64_ubuntu_oct-15'
    # DOCKER_IMAGE='webspdz-64_ubuntu'
    self.PARTY_ID_STARTS_WITH_0=True


  # ==============================================================================
  def sail_specific(self):
    self.cont_server_app = self.sail_webSPDZ_app_server()
    self.cont_server_signaling = self.sail_WebRTC_signaling_server()


  # ==============================================================================
  def run_wrap_down_specific(self):
    ## ...Then also cleanup the servers
    # logs_server_app = server_wSZ_app_container.logs()
    self.cont_server_app.stop()
    # logs_server_signaling = server_signaling_container.logs()
    self.cont_server_signaling.stop()
    ut.print_debug("....Servers stopped", 1)
    # modulus = parse_server_modulus(str(server_wSZ_app_container.logs()))
    # server_container.remove() if (REMOVE_DOCKER_CONTAINERS==True)  
    if (ut.REMOVE_DOCKER_CONTAINERS==True): 
      self.cont_server_app.remove() 
      self.cont_server_signaling.remove() 


  # ==============================================================================
  def run_note_specific(self, meta):
    meta["RAM"]["server_app"] = self.MEMORY_PLAIN_LIMIT_SERVER_wSZ_APP,
    meta["RAM"]["server_signaling"] = self.MEMORY_PLAIN_LIMIT_SERVER_SIGNALING,

    meta["CPU"]["server_app"] = self.CPU_COUNT_SERVER_wSZ_APP,
    meta["CPU"]["server_signaling"] = self.CPU_COUNT_SERVER_SIGNALING,

    return meta


  # ==============================================================================
  # <webSPDZ's app server>
  def sail_webSPDZ_app_server(self):
    print("..Sail webSPDZ's app server..", end='', flush=True)
    ## Start the Server
    port_to_publish = self.APP_SERVER_PORT 
    ports={port_to_publish : port_to_publish}
    
    cont_app_server = self.DOCK.containers.create(\
                    image=self.DOCKER_IMAGE, name=self.DOCKER_CONT_NAME_SERVER_wSZ_app, command=self.CMD_SERVER_wSZ_APP, \
                    mem_limit=self.MEMORY_PLAIN_LIMIT_SERVER_wSZ_APP, memswap_limit=self.MEMORY_SWAP_LIMIT_SERVER_wSZ_APP, \
                    cpu_count=self.CPU_COUNT_SERVER_wSZ_APP, detach=True, \
                    volumes=self.VOLUMES,
                    ports=ports \
                  )

    self.DOCK_NET.connect(cont_app_server, ipv4_address=self.APP_SERVER_IP)
    cont_app_server.start()
    
    print("..webSPDZ's app server is sailing ⛵") 
    return cont_app_server
  # </webSPDZ's app server>


  # ==============================================================================
  # <WebRTC's signaling server>
  def sail_WebRTC_signaling_server(self):
    print("..Sail WebRTC's signaling server..", end='', flush=True)
    ## Start the Server
    port_to_publish = self.SIGNALING_SERVER_PORT 
    ports={port_to_publish : port_to_publish}
    
    cont_signaling_server = self.DOCK.containers.create(\
                    image=self.DOCKER_IMAGE, name=self.DOCKER_CONT_NAME_SERVER_SIGNALING, command=self.CMD_SERVER_SIGNALING, \
                    mem_limit=self.MEMORY_PLAIN_LIMIT_SERVER_SIGNALING, memswap_limit=self.MEMORY_SWAP_LIMIT_SERVER_SIGNALING, \
                    cpu_count=self.CPU_COUNT_SERVER_SIGNALING, detach=True, \
                    volumes=self.VOLUMES,
                    ports=ports \
                  )

    self.DOCK_NET.connect(cont_signaling_server, ipv4_address=self.SIGNALING_SERVER_IP)
    cont_signaling_server.start()
    
    print("..WebRTC's signaling server is sailing ⛵") 
    return cont_signaling_server
  # </WebRTC's signaling server>

