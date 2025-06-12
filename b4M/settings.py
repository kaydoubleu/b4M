
import os

PARTY_DOCKER_TIMEOUT_MIN=60 # in minutes  

if __package__ is None or __package__ == '':
    # current directory visibility
    import PyEngines.eng_webSPDZ as eng_wSZ
    import PyEngines.eng_natSPDZ as eng_natSZ
    import PyEngines.eng_MPyCweb as eng_MPyCweb
    import PyEngines.eng_JIFF as eng_JIFF
else:
    # current package visibility
    from .PyEngines import eng_webSPDZ as eng_wSZ

# ##############################################################################
# Benchmark Settings :: General

PROGRAMS=[
  'dot_product',
  # 'multiplication',
  # 'addition',
  # 'stat_min',
  # 'stat_max',
  # 'stat_avg',
  # 'ppml_log-reg',
]

NR_PLAYERS=[
  # 3,
  4,
  # 5,
  # 6,
  # 7,
  # 8,
  # 9,
  # 10,
  # 11,
  # 12,
  # 13,
]

ARRAY_LENGTHS=[
  # 10**0,
  # 10**1,
  # 10**2,
  # 10**3,
  # 10**4,
  10**5,
  # 10**6,
]

# just comment in the protocol you want to run 🏃‍♂️ :)
# ...and vice-versa for not  
PROTOCOLS=[
  '0', # 'Shamir-Passive', 
  # '1', # 'Replicated-Ring' # 3-Parties; passive
  # '2', # 'Replicated-4-Ring' # 4-Parties; active
  # '3', # 'Shamir-Passive: ML-Eval', 
  # '4', # 'Shamir-Passive: ML-Train', 
  # '5', # 'RepRing (3P): ML-Eval', 
  # '6', # 'RepRing (3P): ML-Train', 
  # '7', # 'Rep4Ring: ML-Eval', 
  # '8', # 'Rep4Ring: ML-Train', 
  '9', # 'Shamir-Active', 
  '10', # MASCOT
  '11', # semi2 
]

ENGINES={
  'webSPDZ': eng_wSZ.webSPDZ_engine(),
  # 'natSPDZ': eng_natSZ.natSPDZ_engine(),
  # 'mpSPDZ': eng_mpSZ.mpSPDZ_engine(),
  # 'JIFF': eng_JIFF.JIFF_engine(),
  # 'MPyCweb': eng_MPyCweb.MPyCweb.engine(), # TODO <-- implement :D
  # 'mpycNat': ...,
}

NR_RUNS_PER_SETTING=3
# NR_RUNS_PER_SETTING=5
# NR_RUNS_PER_SETTING=10

# TEST_LOGS=True
TEST_LOGS=False

# ##############################################################################
# Benchmark Settings :: (Docker) Network Setup
# TODO::pump up for dynamic network choice (currently only LAN)
NETWORKS=[
  'LAN',
  # 'WAN',
]

DOCKER_NETWORKS='webSPDZ-Net'
IP_BASE='172.16.37.'

# ##############################################################################
# Graph Settings

# GRAPH_PROGRAMS=[
    # 'BB-Addition',
    # 'BB-Multiplication',
    # 'BB-Dot-Product',
    # 'BB-Array-Min',
    # 'BB-Array-Max',
    # 'BB-Array-Average',
    # 'LogReg-Breast-Cancer',
# ]

GRAPHS_RUNTIME=[
  # fixed 3/4 parties 
  # variable #input 
  {'X-axis': '#Eles', 
   'X-label': 'Training Epochs [#]',
  #  'X-label': 'Vector Elements [#]',
   'line-color': 'Protocol', 'line-style': 'Protocol', 'legend-title': 'MPC Protocol',
  #  'line-color': 'Engine', 'line-style': 'Engine', 'legend-title': 'MPC Engine',
   'active': 0,
   'settings': {
      'PROGRAMS': [
          'BB-Addition',
          'BB-Multiplication',
          'BB-Dot-Product',
          # 'BB-Array-Min',
          # 'BB-Array-Max',
          'BB-Array-Average',
          # 'LogReg-Breast-Cancer',
      ],

      # Shamir-Passive vs. Rep3
      # ...3 Parties - #array eles
      'PROTOCOLS': ['0', '1'], # Shamir-Passive (0), Rep3 (1)
      'NR_PLAYERS': [3], 
      # ....general computations:
      'ARRAY_LENGTHS': [10**0, 10**1, 10**2, 10**3, 10**4, 10**5, 10**6],
      # 'ARRAY_LENGTHS': [10**0, 10**1, 10**2, 10**3, 10**4, 10**5],
      'DIR_SUBPATH': f'natSPDZ/{{program}}/3-P_X-Eles',
      'GRAPH_TITLE': f'{{program}} :: MPC engine natSPDZ\n3 Parties & Various Vector Elements\n%s in LAN', #TODO: update 4 WAN
      # ....ML computations:
      # 'ARRAY_LENGTHS': [1,2,3,4,5],
      # 'DIR_SUBPATH': f'natSPDZ/{{program}}/3-P_X-Epoch',
      # 'GRAPH_TITLE': f'{{program}} :: MPC engine natSPDZ\n3 Parties & Various Training Epochs\n%s in LAN', #TODO: update 4 WAN

      # Shamir-Active vs. Rep4 
      # ..4 Parties - #array eles
      # 'PROTOCOLS': ['9', '2'], # Shamir-Active (9), Rep4 (2)
      # 'NR_PLAYERS': [4], 
      # ....general computations:
      # 'ARRAY_LENGTHS': [10**0, 10**1, 10**2, 10**3, 10**4, 10**5, 10**6],
      # 'ARRAY_LENGTHS': [10**0, 10**1, 10**2, 10**3, 10**4, 10**5],
      # 'DIR_SUBPATH': f'natSPDZ/{{program}}/4-P_X-Eles',
      # 'GRAPH_TITLE': f'{{program}} :: MPC engine natSPDZ\n4 Parties & Various Vector Elements\n%s in LAN', #TODO: update 4 WAN
      # ....ML computations:
      # 'ARRAY_LENGTHS': [1,2,3,4,5],
      # 'DIR_SUBPATH': f'natSPDZ/{{program}}/4-P_X-Epoch',
      # 'GRAPH_TITLE': f'{{program}} :: MPC engine natSPDZ\n4 Parties & Various Training Epochs\n%s in LAN', #TODO: update 4 WAN

      'NETWORKS': ['LAN'], #, 'WAN']
      'ENGINES': {
          # 'webSPDZ': eng_wSZ.webSPDZ_engine(), 
          'natSPDZ': eng_natSZ.natSPDZ_engine(),
      },
      # 'DIR_SUBPATH': os.path.join(f'natSPDZ', 'BB-Addition', '3-P_X-Eles'),
    }
  },

  # Variable #Parties 
  # Fixed #Input (e.g., 10^5 array eles, 1 training epoch, ..)
  {'X-axis': '#Parties', 'X-label': 'Nr. Parties [#]',
  #  'line-color': 'Protocol', 'line-style': 'Protocol', 'legend-title': 'MPC Protocol',
   'line-color': 'Engine', 'line-style': 'Engine', 'legend-title': 'MPC Engine',
   'active': 1,
   'settings': {
      'PROGRAMS': [
          # 'BB-Addition',
          # 'BB-Multiplication',
          'BB-Dot-Product',
          # 'BB-Array-Min',
          # 'BB-Array-Max',
          # 'BB-Array-Average',
          # 'LogReg-Breast-Cancer'
      ],

      # Shamir-Passive vs. Shamir-Active
      'PROTOCOLS': ['0'], # Shamir-Active (0), Shamir-Active (9)
      # 'NR_PLAYERS': [3,4,5,6,7,8,9,10,11,12,13], 
      'NR_PLAYERS': [3,4,5,6,7,8,9], 
      'ARRAY_LENGTHS': [10**5],
      'DIR_SUBPATH': f'b4M-ARES-SECPID/Party-Engines/{{program}}/X-P_10^5-Eles',
      # 'GRAPH_TITLE': f'{{program}} :: MPC engine natSPDZ\nVarious Nr. Parties & 10^5 Vector Elements\n%s in LAN', #TODO: update 4 WAN
      'GRAPH_TITLE': f'{{program}} :: Semi-Honest Shamir\nVarious Nr. Parties & 10^5 Vector Elements\n%s in LAN', #TODO: update 4 WAN

      # Shamir-Passive vs. Shamir-Active
      # ...#Parties - 10^5 array eles
      # 'PROTOCOLS': ['0', '9'], # Shamir-Passive (0), Shamir-Active (0)
      # 'NR_PLAYERS': [3,4,5,6,7,8,9,10,11,12,13], 
      # 'ARRAY_LENGTHS': [10**5],
      # 'DIR_SUBPATH': f'natSPDZ/{{program}}/X-P_10^5-Eles',
      # 'GRAPH_TITLE': f'{{program}} :: MPC engine natSPDZ\nVarious Nr. Parties & 10^5 Vector Elements\n%s in LAN', #TODO: update 4 WAN
      # 'ARRAY_LENGTHS': [1],
      # 'DIR_SUBPATH': f'natSPDZ/{{program}}/X-P_1-Epoch',
      # 'GRAPH_TITLE': f'{{program}} :: MPC engine natSPDZ\nVarious Nr. Parties & 1 Training Epoch\n%s in LAN', #TODO: update 4 WAN

      'NETWORKS': ['LAN'], #, 'WAN']
      'ENGINES': {
          'webSPDZ': eng_wSZ.webSPDZ_engine(), 
          'natSPDZ': eng_natSZ.natSPDZ_engine(),
      },
      # 'DIR_SUBPATH': os.path.join(f'natSPDZ', 'BB-Addition', '3-P_X-Eles'),
    }
  },

]




"""
# Rep.4 Ring (4P):: webSPDZ vs. mpSPDZ
{'X-axis': '#Eles', 'X-label': 'Vector Elements [#]',
  'active': 0,
  'settings': {
    'PROGRAMS': ['dot_product'],
    'PROTOCOLS': ['2'],
    'NR_PLAYERS': [4], 
    'ARRAY_LENGTHS': [10**2, 10**3, 10**4, 10**5, 10**6],
    'NETWORKS': ['LAN'], #, 'WAN']
    'ENGINES': {
        'webSPDZ': eng_wSZ.webSPDZ_engine(), 
        'natSPDZ': eng_natSZ.natSPDZ_engine(),
    },
    'DIR_SUBPATH': os.path.join('Rep-4-Ring_web-mp-SPDZ', '4-P_X-Eles'),
    'GRAPH_TITLE': 'Dot·Product :: Replicated 4 Ring (4 Parties)\n%s in LAN :: Various Vector Elements', #TODO: update 4 WAN
  }
},
# Shamir Passive :: All ENGINES ("Free For All" ^^) :: 3P - X eles
{'X-axis': '#Eles', 'X-label': 'Vector Elements [#]',
  'active': 0,
  'settings': {
    'PROGRAMS': ['dot_product'],
    'PROTOCOLS': ['0'],
    'NR_PLAYERS': [3], 
    'ARRAY_LENGTHS': [10**2, 10**3, 10**4, 10**5], #,10**6]
    'NETWORKS': ['LAN'], #, 'WAN']
    'ENGINES': {
      'webSPDZ': eng_wSZ.webSPDZ_engine(), 
      'natSPDZ': eng_natSZ.natSPDZ_engine(),
      'JIFF': eng_JIFF.JIFF_engine(), 
      # TODO: add ENGINES :)
    },
    'DIR_SUBPATH': os.path.join('Shamir-Passive_All-Engines', '3-P_X-Eles'),
    'GRAPH_TITLE': 'Dot·Product :: Passive Shamir\n%s in LAN :: 3 Parties & Various Vector Elements',#TODO: update 4 WAN
  }
},
# Shamir Passive :: All ENGINES ("Free For All" ^^) :: 10^5 eles - X-parties (3-6)
{'X-axis': '#Parties', 'X-label': 'Parties [#]',
  'active': 0,
  'settings': {
    'PROGRAMS': ['dot_product'],
    'PROTOCOLS': ['0'],
    'NR_PLAYERS': [3,4,5,6], 
    'ARRAY_LENGTHS': [10**5],
    'NETWORKS': ['LAN'], #, 'WAN']
    'ENGINES': {
      'webSPDZ': eng_wSZ.webSPDZ_engine(), 
      'natSPDZ': eng_natSZ.natSPDZ_engine(),
      'JIFF': eng_JIFF.JIFF_engine(), 
      # TODO: add ENGINES :)
    },
    'DIR_SUBPATH': os.path.join('Shamir-Passive_All-Engines', '3-6-P_10^5-Eles'),
    'GRAPH_TITLE': 'Dot·Product :: Passive Shamir\n%s in LAN :: 10^5 Vector Elements & 3-6 Parties',#TODO: update 4 WAN
  }
},
# Shamir Passive :: webSZ vs. mpSZ :: 10^5 eles - X-parties (3-13)
{'X-axis': '#Parties', 'X-label': 'Parties [#]',
  'active': 0,
  'settings': {
    'PROGRAMS': ['dot_product'],
    'PROTOCOLS': ['0'],
    'NR_PLAYERS': [3,4,5,6,7,8,9,10,11,12,13], 
    'ARRAY_LENGTHS': [10**5],
    'NETWORKS': ['LAN'], #, 'WAN']
    'ENGINES': {
      'webSPDZ': eng_wSZ.webSPDZ_engine(), 
      'natSPDZ': eng_natSZ.natSPDZ_engine(),
      # 'JIFF': eng_JIFF.JIFF_engine(), 
      # TODO: add ENGINES :)
    },
    'DIR_SUBPATH': os.path.join('Shamir-Passive_All-Engines', '3-13-P_10^5-Eles'),
    'GRAPH_TITLE': 'Dot·Product :: Passive Shamir\n%s in LAN :: 10^5 Vector Elements & 3-13 Parties',#TODO: update 4 WAN
  }
},
"""
TIMERS=[
  {'id':'full', 'Y-axis': 'runtime-avg-full', 'Y-label': 'Runtime - Whole Program [%s]', 
   'title': 'Whole Runtime',
  }, 
  {'id':'input', 'Y-axis': 'runtime-avg-input', 'Y-label': 'Runtime - Data Input [%s]', 
   'title': 'Data-Input Runtime',
  }, 
  # TODO: craft something more dynamic!
  {'id':'computation', 'Y-axis': 'runtime-avg-computation', 'Y-label': 'Runtime - Computation [%s]', 
   'title': 'Pure-Computation Runtime',
  },
  # {'id':'ML-train', 'Y-axis': 'runtime-avg-ML-train', 'Y-label': 'Runtime - ML Training [%s]', 
  #  'title': 'ML-Training Runtime',
  # },
  # {'id':'ML-predict', 'Y-axis': 'runtime-avg-ML-predict', 'Y-label': 'Runtime - ML Prediction [%s]', 
  #  'title': 'ML-Prediction Runtime',
  # },
]
  
# GRAPHS_COMMUNICATION=[

# ]


